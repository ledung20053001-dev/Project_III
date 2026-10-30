#!/usr/bin/env python3
"""Chia dataset thành train/val/test theo nhóm ca, tỷ lệ 70/15/15.

Các ca có chung content_sha256 được nối thành một thành phần liên thông và luôn
nằm trong cùng split. Script kiểm tra rò rỉ case_id, group_id, image_path và
content_sha256; không sao chép hoặc di chuyển ảnh.
"""

import argparse
import csv
import hashlib
import json
import platform
import random
import sys
from collections import defaultdict
from pathlib import Path


SPLITS = ('train', 'val', 'test')
RATIOS = {'train': 0.70, 'val': 0.15, 'test': 0.15}


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


class UnionFind:
    def __init__(self, items):
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item):
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left, right):
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='data/metadata/dataset_images.csv')
    parser.add_argument('--mapping', default='data/metadata/class_mapping.json')
    parser.add_argument('--output-dir', default='data/metadata')
    parser.add_argument('--seed', type=int, default=42)
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_mapping(path):
    with Path(path).open(encoding='utf-8') as handle:
        raw = json.load(handle)
    mapping = {}
    for key, value in raw.items():
        class_id = int(key)
        if not isinstance(value, dict) or not value.get('label_en') or not value.get('label_vi'):
            raise ValueError(f'{path}: mapping không hợp lệ tại class_id {key}')
        mapping[class_id] = {
            'label_en': value['label_en'],
            'label_vi': value['label_vi'],
        }
    if sorted(mapping) != list(range(len(mapping))):
        raise ValueError(f'{path}: class_id phải liên tục từ 0 đến N-1')
    return mapping


def read_manifest(path, mapping):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        required = {
            'case_id', 'image_path', 'label_en', 'label_vi', 'class_id',
            'content_sha256',
        }
        missing = required - set(fieldnames)
        if missing:
            raise ValueError(f'{path}: thiếu cột {sorted(missing)}')
        rows = []
        seen_paths = set()
        case_classes = {}
        for row in reader:
            line = reader.line_num
            case_id = (row.get('case_id') or '').strip()
            image_path = Path((row.get('image_path') or '').strip()).as_posix()
            content_hash = (row.get('content_sha256') or '').strip()
            if not case_id or not image_path or not content_hash:
                raise ValueError(f'{path}: thiếu dữ liệu bắt buộc tại dòng {line}')
            if image_path in seen_paths:
                raise ValueError(f'{path}: image_path trùng tại dòng {line}: {image_path}')
            seen_paths.add(image_path)
            try:
                class_id = int(row['class_id'])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{path}: class_id sai tại dòng {line}') from exc
            if class_id not in mapping:
                raise ValueError(f'{path}: class_id {class_id} không có trong mapping')
            if row['label_en'] != mapping[class_id]['label_en'] or row['label_vi'] != mapping[class_id]['label_vi']:
                raise ValueError(f'{path}: nhãn không khớp mapping tại dòng {line}')
            if case_id in case_classes and case_classes[case_id] != class_id:
                raise ValueError(f'{path}: case_id {case_id} có nhiều class_id')
            case_classes[case_id] = class_id
            clean = dict(row)
            clean['case_id'] = case_id
            clean['image_path'] = image_path
            clean['class_id'] = class_id
            clean['content_sha256'] = content_hash
            rows.append(clean)
    if not rows:
        raise ValueError(f'{path}: manifest rỗng')
    return rows, fieldnames, case_classes


def build_groups(rows, case_classes):
    union_find = UnionFind(case_classes)
    cases_by_content = defaultdict(set)
    for row in rows:
        cases_by_content[row['content_sha256']].add(row['case_id'])
    for cases in cases_by_content.values():
        ordered = sorted(cases)
        for case_id in ordered[1:]:
            union_find.union(ordered[0], case_id)

    components = defaultdict(list)
    for case_id in case_classes:
        components[union_find.find(case_id)].append(case_id)

    groups = []
    case_to_group = {}
    for cases in components.values():
        ordered_cases = sorted(cases)
        class_ids = {case_classes[case_id] for case_id in ordered_cases}
        if len(class_ids) != 1:
            raise ValueError(
                'Nhóm ảnh trùng chứa nhiều lớp: '
                f'cases={ordered_cases}, classes={sorted(class_ids)}'
            )
        group_hash = hashlib.sha256('|'.join(ordered_cases).encode('utf-8')).hexdigest()[:16]
        group_id = f'G_{group_hash}'
        group = {
            'group_id': group_id,
            'case_ids': ordered_cases,
            'class_id': next(iter(class_ids)),
            'size': len(ordered_cases),
        }
        groups.append(group)
        for case_id in ordered_cases:
            case_to_group[case_id] = group_id
    groups.sort(key=lambda group: (group['class_id'], group['group_id']))
    return groups, case_to_group


def target_counts(total):
    raw = {split: total * RATIOS[split] for split in SPLITS}
    result = {split: int(raw[split]) for split in SPLITS}
    remainder = total - sum(result.values())
    order = sorted(
        SPLITS,
        key=lambda split: (-(raw[split] - result[split]), SPLITS.index(split)),
    )
    for split in order[:remainder]:
        result[split] += 1
    return result


def split_groups(groups, seed, class_ids):
    rng = random.Random(seed)
    assignment = {}
    targets_by_class = {}
    actual_by_class = {}

    for class_id in class_ids:
        class_groups = [group for group in groups if group['class_id'] == class_id]
        total_cases = sum(group['size'] for group in class_groups)
        targets = target_counts(total_cases)
        targets_by_class[class_id] = targets
        remaining = dict(targets)

        tie_break = list(SPLITS)
        rng.shuffle(tie_break)
        split_priority = {split: index for index, split in enumerate(tie_break)}
        rng.shuffle(class_groups)
        class_groups.sort(key=lambda group: -group['size'])

        for group in class_groups:
            fitting = [
                split for split in SPLITS
                if remaining[split] >= group['size']
            ]
            if fitting:
                chosen = max(
                    fitting,
                    key=lambda split: (
                        remaining[split] / max(targets[split], 1),
                        remaining[split],
                        -split_priority[split],
                    ),
                )
            else:
                chosen = min(
                    SPLITS,
                    key=lambda split: (
                        max(0, group['size'] - remaining[split]),
                        -remaining[split],
                        split_priority[split],
                    ),
                )
            assignment[group['group_id']] = chosen
            remaining[chosen] -= group['size']

        actual = {split: 0 for split in SPLITS}
        for group in class_groups:
            actual[assignment[group['group_id']]] += group['size']
        actual_by_class[class_id] = actual
    return assignment, targets_by_class, actual_by_class


def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pairwise_intersections(values_by_split):
    result = {}
    for left_index, left in enumerate(SPLITS):
        for right in SPLITS[left_index + 1:]:
            result[f'{left}_vs_{right}'] = len(values_by_split[left] & values_by_split[right])
    return result


def main():
    args = parse_args()
    manifest_path = Path(args.manifest)
    mapping_path = Path(args.mapping)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = load_mapping(mapping_path)
    rows, original_fields, case_classes = read_manifest(manifest_path, mapping)
    groups, case_to_group = build_groups(rows, case_classes)
    group_assignment, targets, actual = split_groups(groups, args.seed, sorted(mapping))

    case_image_counts = defaultdict(int)
    for row in rows:
        case_image_counts[row['case_id']] += 1
    group_by_id = {group['group_id']: group for group in groups}
    case_assignments = []
    case_to_split = {}
    for case_id in sorted(case_classes, key=lambda value: (case_classes[value], value)):
        group_id = case_to_group[case_id]
        split = group_assignment[group_id]
        case_to_split[case_id] = split
        class_id = case_classes[case_id]
        case_assignments.append({
            'case_id': case_id,
            'class_id': class_id,
            'label_en': mapping[class_id]['label_en'],
            'label_vi': mapping[class_id]['label_vi'],
            'group_id': group_id,
            'group_size': group_by_id[group_id]['size'],
            'split': split,
            'total_images': case_image_counts[case_id],
        })
    write_csv(
        output_dir / 'case_split_assignments.csv',
        [
            'case_id', 'class_id', 'label_en', 'label_vi', 'group_id',
            'group_size', 'split', 'total_images',
        ],
        case_assignments,
    )

    split_rows = {split: [] for split in SPLITS}
    output_fields = list(original_fields) + ['group_id', 'split']
    for row in rows:
        split = case_to_split[row['case_id']]
        output = {field: row[field] for field in original_fields}
        output['group_id'] = case_to_group[row['case_id']]
        output['split'] = split
        split_rows[split].append(output)
    for split in SPLITS:
        split_rows[split].sort(
            key=lambda row: (int(row['class_id']), row['case_id'], int(row['image_index']))
        )
        write_csv(output_dir / f'{split}.csv', output_fields, split_rows[split])

    summary_rows = []
    for split in SPLITS:
        split_total_cases = len({row['case_id'] for row in split_rows[split]})
        split_total_images = len(split_rows[split])
        for class_id in sorted(mapping):
            class_rows = [row for row in split_rows[split] if int(row['class_id']) == class_id]
            class_cases = {row['case_id'] for row in class_rows}
            summary_rows.append({
                'split': split,
                'class_id': class_id,
                'label_en': mapping[class_id]['label_en'],
                'label_vi': mapping[class_id]['label_vi'],
                'total_cases': len(class_cases),
                'total_images': len(class_rows),
                'case_percentage': round(len(class_cases) / split_total_cases * 100, 4),
                'image_percentage': round(len(class_rows) / split_total_images * 100, 4),
                'target_cases': targets[class_id][split],
                'target_difference': len(class_cases) - targets[class_id][split],
            })
    write_csv(
        output_dir / 'split_summary.csv',
        [
            'split', 'class_id', 'label_en', 'label_vi', 'total_cases',
            'total_images', 'case_percentage', 'image_percentage',
            'target_cases', 'target_difference',
        ],
        summary_rows,
    )

    sets = {}
    for field in ('case_id', 'group_id', 'image_path', 'content_sha256'):
        sets[field] = {
            split: {row[field] for row in split_rows[split]}
            for split in SPLITS
        }
    intersections = {
        field: pairwise_intersections(values)
        for field, values in sets.items()
    }
    class_presence = {
        split: sorted({int(row['class_id']) for row in split_rows[split]})
        for split in SPLITS
    }
    validation = {
        'status': 'passed',
        'manifest_images': len(rows),
        'split_images': {split: len(split_rows[split]) for split in SPLITS},
        'split_cases': {
            split: len({row['case_id'] for row in split_rows[split]})
            for split in SPLITS
        },
        'split_groups': {
            split: len({row['group_id'] for row in split_rows[split]})
            for split in SPLITS
        },
        'sum_split_images': sum(len(split_rows[split]) for split in SPLITS),
        'pairwise_intersections': intersections,
        'class_presence': class_presence,
        'all_classes_present_in_every_split': all(
            class_presence[split] == sorted(mapping) for split in SPLITS
        ),
        'each_image_assigned_once': (
            sum(len(split_rows[split]) for split in SPLITS) == len(rows)
            and len(set().union(*(sets['image_path'][split] for split in SPLITS))) == len(rows)
        ),
    }
    leakage = any(
        count != 0
        for field_result in intersections.values()
        for count in field_result.values()
    )
    if leakage or not validation['all_classes_present_in_every_split'] or not validation['each_image_assigned_once']:
        validation['status'] = 'failed'
        raise ValueError(f'Kiểm tra split thất bại: {validation}')
    with (output_dir / 'split_validation.json').open('w', encoding='utf-8') as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

    train_counts = {
        class_id: sum(1 for row in split_rows['train'] if int(row['class_id']) == class_id)
        for class_id in sorted(mapping)
    }
    train_total = len(split_rows['train'])
    class_weights = {
        class_id: train_total / (len(mapping) * count)
        for class_id, count in train_counts.items()
    }
    weights_output = {
        'formula': 'N / (K * n_c)',
        'source_split': 'train',
        'train_total_images': train_total,
        'num_classes': len(mapping),
        'weights_in_class_id_order': [round(class_weights[class_id], 8) for class_id in sorted(mapping)],
        'by_class_id': {
            str(class_id): {
                'label_en': mapping[class_id]['label_en'],
                'train_images': train_counts[class_id],
                'class_weight': round(class_weights[class_id], 8),
            }
            for class_id in sorted(mapping)
        },
    }
    with (output_dir / 'train_class_weights.json').open('w', encoding='utf-8') as handle:
        json.dump(weights_output, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

    config = {
        'random_seed': args.seed,
        'ratios': RATIOS,
        'method': 'deterministic per-class grouped allocation by case count',
        'group_rule': 'connected components of case_id linked by identical content_sha256',
        'manifest_path': manifest_path.as_posix(),
        'manifest_sha256': sha256_file(manifest_path),
        'mapping_path': mapping_path.as_posix(),
        'mapping_sha256': sha256_file(mapping_path),
        'python_version': platform.python_version(),
        'library': 'Python standard library; no sklearn',
        'targets_by_class': {str(key): value for key, value in targets.items()},
        'actual_cases_by_class': {str(key): value for key, value in actual.items()},
    }
    with (output_dir / 'split_config.json').open('w', encoding='utf-8') as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

    print(f'Tổng ca: {len(case_classes)}')
    print(f'Tổng group: {len(groups)}')
    for split in SPLITS:
        print(
            f"{split}: {validation['split_cases'][split]} ca, "
            f"{validation['split_images'][split]} ảnh, "
            f"{validation['split_groups'][split]} group"
        )
    print('Kiểm tra rò rỉ: PASSED')
    print(f'Đã ghi kết quả vào: {output_dir.resolve()}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        sys.exit(1)

