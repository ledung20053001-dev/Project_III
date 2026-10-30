#!/usr/bin/env python3
"""Thống kê và cố định các lớp bệnh cho Task 1.

Script đọc dữ liệu một nhãn ở mức ca, kiểm tra tính duy nhất của case_id,
thống kê toàn bộ nhãn và tạo ba đầu ra chính:

* class_statistics.csv: thống kê tất cả lớp sau lọc single-label;
* selected_classes.csv: thống kê các lớp được chọn và class_id cố định;
* selected_cases.csv: danh sách ca thuộc các lớp được chọn;
* class_mapping.json: ánh xạ class_id sang tên tiếng Anh/Việt;
* duplicate_image_references.csv: đường dẫn nguồn được nhiều ca tham chiếu.

Ảnh chỉ được kiểm tra tồn tại theo tên <case_id>_<image_index>.jpg. Script
không mở hoặc đánh giá nội dung ảnh; việc xác thực ảnh thuộc Task 2.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


IMAGE_COLS = ['image_1_path', 'image_2_path', 'image_3_path']

# Mapping này là giao diện đầu ra cố định của mô hình. Không sắp xếp động theo
# thống kê vì thứ tự class_id phải ổn định giữa train, evaluate và predict.
SELECTED_LABELS = [
    'Eczema',
    'Allergic Contact Dermatitis',
    'Urticaria',
    'Insect Bite',
    'Folliculitis',
    'Psoriasis',
    'Tinea',
    'Herpes Simplex',
]


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input',
        default='data/metadata/scin_single_label_05.csv',
        help='CSV một dòng cho mỗi ca, có primary_label và label_weight.',
    )
    parser.add_argument('--images-dir', default='data/images_all')
    parser.add_argument('--translations', default='labels_vi.json')
    parser.add_argument('--output-dir', default='data/metadata')
    return parser.parse_args()


def read_single_label(path):
    required = {'case_id', 'primary_label', 'label_weight', *IMAGE_COLS}
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path}: thiếu cột {sorted(missing)}')

        rows = []
        labels_by_case = {}
        for row in reader:
            case_id = (row.get('case_id') or '').strip()
            label = (row.get('primary_label') or '').strip()
            if not case_id or not label:
                raise ValueError(f'{path}: case_id/primary_label trống tại dòng {reader.line_num}')
            if case_id in labels_by_case:
                previous = labels_by_case[case_id]
                detail = 'nhiều nhãn' if previous != label else 'nhiều dòng'
                raise ValueError(f'{path}: case_id {case_id} có {detail} tại dòng {reader.line_num}')
            try:
                weight = float(row['label_weight'])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{path}: label_weight không hợp lệ tại dòng {reader.line_num}') from exc
            if not 0.5 < weight <= 1:
                raise ValueError(f'{path}: label_weight ngoài khoảng (0.5, 1] tại dòng {reader.line_num}')

            clean = {
                'case_id': case_id,
                'primary_label': label,
                'label_weight': weight,
            }
            for column in IMAGE_COLS:
                value = (row.get(column) or '').strip()
                clean[column] = '' if value.lower() in {'nan', 'none', 'null'} else value
            if not any(clean[column] for column in IMAGE_COLS):
                raise ValueError(f'{path}: case_id {case_id} không có đường dẫn ảnh')
            labels_by_case[case_id] = label
            rows.append(clean)
    return rows


def load_translations(path):
    with Path(path).open(encoding='utf-8') as handle:
        raw = json.load(handle)
    translations = {}
    for label, value in raw.items():
        if isinstance(value, dict):
            value = value.get('vi')
        if isinstance(value, str) and value.strip():
            translations[label] = value.strip()
    missing = [label for label in SELECTED_LABELS if label not in translations]
    if missing:
        raise ValueError(f'{path}: thiếu bản dịch cho {missing}')
    return translations


def local_image_path(images_dir, case_id, image_index):
    return images_dir / f'{case_id}_{image_index}.jpg'


def collect_statistics(rows, images_dir):
    groups = defaultdict(list)
    source_references = defaultdict(list)
    for row in rows:
        groups[row['primary_label']].append(row)
        for index, column in enumerate(IMAGE_COLS, start=1):
            source_path = row[column]
            if source_path:
                source_references[source_path].append({
                    'case_id': row['case_id'],
                    'primary_label': row['primary_label'],
                    'image_index': index,
                    'local_path': str(local_image_path(images_dir, row['case_id'], index)),
                })

    statistics = []
    for label, cases in groups.items():
        referenced_paths = {}
        total_references = 0
        weights = []
        for case in cases:
            weights.append(case['label_weight'])
            for index, column in enumerate(IMAGE_COLS, start=1):
                if not case[column]:
                    continue
                total_references += 1
                exists = local_image_path(images_dir, case['case_id'], index).is_file()
                referenced_paths[case[column]] = referenced_paths.get(case[column], False) or exists
        referenced = len(referenced_paths)
        local_existing = sum(referenced_paths.values())
        total_cases = len(cases)
        statistics.append({
            'primary_label': label,
            'total_cases': total_cases,
            'referenced_images': referenced,
            'local_existing_images': local_existing,
            'missing_images': referenced - local_existing,
            'duplicate_references': total_references - referenced,
            'avg_images_per_case': round(referenced / total_cases, 4),
            'avg_label_weight': round(sum(weights) / total_cases, 4),
            'min_label_weight': round(min(weights), 4),
        })
    statistics.sort(key=lambda item: (-item['total_cases'], item['primary_label'].lower()))
    duplicates = []
    for source_path, references in source_references.items():
        if len(references) < 2:
            continue
        duplicates.append({
            'source_path': source_path,
            'reference_count': len(references),
            'case_ids': ';'.join(item['case_id'] for item in references),
            'primary_labels': ';'.join(item['primary_label'] for item in references),
            'image_indexes': ';'.join(str(item['image_index']) for item in references),
            'local_paths': ';'.join(item['local_path'] for item in references),
            'cross_label': len({item['primary_label'] for item in references}) > 1,
        })
    duplicates.sort(key=lambda item: (-item['reference_count'], item['source_path']))
    return statistics, duplicates


def estimated_split(total_cases):
    train = round(total_cases * 0.70)
    val = round(total_cases * 0.15)
    return train, val, total_cases - train - val


def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    images_dir = Path(args.images_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_single_label(args.input)
    translations = load_translations(args.translations)
    statistics, duplicates = collect_statistics(rows, images_dir)
    stats_by_label = {item['primary_label']: item for item in statistics}

    absent = [label for label in SELECTED_LABELS if label not in stats_by_label]
    if absent:
        raise ValueError(f'Không tìm thấy lớp đã chọn trong dữ liệu: {absent}')

    write_csv(
        output_dir / 'class_statistics.csv',
        [
            'primary_label', 'total_cases', 'referenced_images',
            'local_existing_images', 'missing_images', 'avg_images_per_case',
            'duplicate_references', 'avg_label_weight', 'min_label_weight',
        ],
        statistics,
    )

    write_csv(
        output_dir / 'duplicate_image_references.csv',
        [
            'source_path', 'reference_count', 'case_ids', 'primary_labels',
            'image_indexes', 'local_paths', 'cross_label',
        ],
        duplicates,
    )

    selected_stats = []
    total_selected_cases = sum(stats_by_label[label]['total_cases'] for label in SELECTED_LABELS)
    total_selected_images = sum(stats_by_label[label]['local_existing_images'] for label in SELECTED_LABELS)
    for class_id, label in enumerate(SELECTED_LABELS):
        stats = stats_by_label[label]
        train, val, test = estimated_split(stats['total_cases'])
        selected_stats.append({
            'class_id': class_id,
            'label_en': label,
            'label_vi': translations[label],
            'total_cases': stats['total_cases'],
            'total_images': stats['local_existing_images'],
            'referenced_images': stats['referenced_images'],
            'missing_images': stats['missing_images'],
            'image_count_type': 'local_exists_not_content_validated',
            'case_percentage': round(stats['total_cases'] / total_selected_cases * 100, 4),
            'image_percentage': round(stats['local_existing_images'] / total_selected_images * 100, 4),
            'avg_images_per_case': stats['avg_images_per_case'],
            'estimated_train_cases': train,
            'estimated_val_cases': val,
            'estimated_test_cases': test,
        })

    write_csv(
        output_dir / 'selected_classes.csv',
        [
            'class_id', 'label_en', 'label_vi', 'total_cases', 'total_images',
            'referenced_images', 'missing_images', 'image_count_type',
            'case_percentage', 'image_percentage', 'avg_images_per_case',
            'estimated_train_cases', 'estimated_val_cases', 'estimated_test_cases',
        ],
        selected_stats,
    )

    class_lookup = {label: class_id for class_id, label in enumerate(SELECTED_LABELS)}
    selected_cases = []
    for row in rows:
        label = row['primary_label']
        if label not in class_lookup:
            continue
        output_row = {
            'case_id': row['case_id'],
            'class_id': class_lookup[label],
            'primary_label': label,
            'label_vi': translations[label],
            'label_weight': row['label_weight'],
        }
        referenced_count = 0
        existing_count = 0
        for index, column in enumerate(IMAGE_COLS, start=1):
            source_path = row[column]
            local_path = local_image_path(images_dir, row['case_id'], index)
            output_row[column] = source_path
            output_row[f'local_image_{index}_path'] = str(local_path) if source_path and local_path.is_file() else ''
            if source_path:
                referenced_count += 1
                existing_count += int(local_path.is_file())
        output_row['referenced_image_count'] = referenced_count
        output_row['local_existing_image_count'] = existing_count
        selected_cases.append(output_row)

    selected_cases.sort(key=lambda item: (item['class_id'], item['case_id']))
    case_fields = [
        'case_id', 'class_id', 'primary_label', 'label_vi', 'label_weight',
        'image_1_path', 'image_2_path', 'image_3_path',
        'local_image_1_path', 'local_image_2_path', 'local_image_3_path',
        'referenced_image_count', 'local_existing_image_count',
    ]
    write_csv(output_dir / 'selected_cases.csv', case_fields, selected_cases)

    mapping = {
        str(class_id): {
            'label_en': label,
            'label_vi': translations[label],
        }
        for class_id, label in enumerate(SELECTED_LABELS)
    }
    with (output_dir / 'class_mapping.json').open('w', encoding='utf-8') as handle:
        json.dump(mapping, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

    print(f'Tổng ca single-label: {len(rows)}')
    print(f'Tổng lớp sau lọc: {len(statistics)}')
    print(f'Lớp được chọn: {len(SELECTED_LABELS)}')
    print(f'Ca được chọn: {len(selected_cases)}')
    print(f'Ảnh local được chọn: {total_selected_images}')
    print(f'Đường dẫn ảnh bị nhiều ca tham chiếu: {len(duplicates)}')
    print(f'Đã ghi kết quả vào: {output_dir.resolve()}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        sys.exit(1)

