#!/usr/bin/env python3
"""Tạo manifest một dòng cho mỗi ảnh hợp lệ từ selected_cases.csv.

Ảnh được kiểm tra tồn tại, nhận diện định dạng, verify, giải mã toàn bộ bằng
load(), kiểm tra kích thước và chuyển RGB. Script không sửa hoặc sao chép ảnh,
không tạo augmentation và chưa chia train/validation/test.
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


IMAGE_COLS = ['image_1_path', 'image_2_path', 'image_3_path']
LOCAL_IMAGE_COLS = [
    'local_image_1_path',
    'local_image_2_path',
    'local_image_3_path',
]


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', default='data/metadata/selected_cases.csv')
    parser.add_argument('--mapping', default='data/metadata/class_mapping.json')
    parser.add_argument('--images-dir', default='data/images_all')
    parser.add_argument('--output-dir', default='data/metadata')
    parser.add_argument(
        '--project-root',
        default='.',
        help='Gốc dùng để lưu và phân giải image_path tương đối.',
    )
    return parser.parse_args()


def load_mapping(path):
    with Path(path).open(encoding='utf-8') as handle:
        raw = json.load(handle)
    mapping = {}
    labels = set()
    for key, value in raw.items():
        try:
            class_id = int(key)
        except ValueError as exc:
            raise ValueError(f'{path}: class_id không phải số nguyên: {key}') from exc
        if class_id < 0 or not isinstance(value, dict):
            raise ValueError(f'{path}: mapping không hợp lệ tại class_id {key}')
        label_en = value.get('label_en')
        label_vi = value.get('label_vi')
        if not isinstance(label_en, str) or not label_en.strip():
            raise ValueError(f'{path}: thiếu label_en tại class_id {key}')
        if not isinstance(label_vi, str) or not label_vi.strip():
            raise ValueError(f'{path}: thiếu label_vi tại class_id {key}')
        if label_en in labels:
            raise ValueError(f'{path}: label_en bị trùng: {label_en}')
        labels.add(label_en)
        mapping[class_id] = {
            'label_en': label_en.strip(),
            'label_vi': label_vi.strip(),
        }
    if sorted(mapping) != list(range(len(mapping))):
        raise ValueError(f'{path}: class_id phải liên tục từ 0 đến N-1')
    return mapping


def read_cases(path, mapping):
    required = {
        'case_id', 'class_id', 'primary_label', 'label_vi', 'label_weight',
        *IMAGE_COLS, *LOCAL_IMAGE_COLS,
    }
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path}: thiếu cột {sorted(missing)}')
        rows = []
        seen_cases = set()
        for row in reader:
            line = reader.line_num
            case_id = (row.get('case_id') or '').strip()
            if not case_id or case_id in seen_cases:
                raise ValueError(f'{path}: case_id trống hoặc trùng tại dòng {line}')
            seen_cases.add(case_id)
            try:
                class_id = int(row['class_id'])
                label_weight = float(row['label_weight'])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{path}: class_id/label_weight sai tại dòng {line}') from exc
            if class_id not in mapping:
                raise ValueError(f'{path}: class_id {class_id} không có trong mapping')
            expected = mapping[class_id]
            label_en = (row.get('primary_label') or '').strip()
            label_vi = (row.get('label_vi') or '').strip()
            if label_en != expected['label_en'] or label_vi != expected['label_vi']:
                raise ValueError(f'{path}: nhãn không khớp mapping tại case_id {case_id}')
            if not 0.5 < label_weight <= 1:
                raise ValueError(f'{path}: label_weight ngoài khoảng (0.5, 1] tại case_id {case_id}')
            clean = {
                'case_id': case_id,
                'class_id': class_id,
                'label_en': label_en,
                'label_vi': label_vi,
                'label_weight': label_weight,
            }
            for column in IMAGE_COLS + LOCAL_IMAGE_COLS:
                clean[column] = (row.get(column) or '').strip()
            rows.append(clean)
    return rows


def project_relative(path, project_root):
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(f'Ảnh nằm ngoài project root: {resolved}') from exc
    return relative.as_posix()


def inspect_image(path):
    try:
        with Image.open(path) as image:
            detected_format = image.format or ''
            image.verify()
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            if width <= 0 or height <= 0:
                return None, 'invalid_dimensions', f'{width}x{height}'
            rgb = image.convert('RGB')
            rgb.load()
            digest = hashlib.sha256()
            digest.update(f'{width}x{height}:RGB:'.encode('ascii'))
            digest.update(rgb.tobytes())
        return {
            'width': width,
            'height': height,
            'format': detected_format,
            'content_sha256': digest.hexdigest(),
        }, None, None
    except FileNotFoundError:
        return None, 'file_not_found', None
    except UnidentifiedImageError as exc:
        return None, 'unidentified_image', str(exc)
    except (OSError, ValueError) as exc:
        return None, 'decode_error', str(exc)


def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    images_dir = (project_root / args.images_dir).resolve()
    output_dir = (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = load_mapping(project_root / args.mapping)
    cases = read_cases(project_root / args.cases, mapping)
    manifest = []
    rejected = []
    valid_images_by_case = defaultdict(int)
    seen_image_paths = set()

    for case in cases:
        seen_sources_in_case = set()
        for index, (source_column, local_column) in enumerate(
            zip(IMAGE_COLS, LOCAL_IMAGE_COLS),
            start=1,
        ):
            source_path = case[source_column]
            if not source_path:
                continue
            local_value = case[local_column]
            local_path = (
                (project_root / local_value).resolve()
                if local_value
                else images_dir / f"{case['case_id']}_{index}.jpg"
            )
            relative_path = project_relative(local_path, project_root)

            if source_path in seen_sources_in_case:
                rejected.append({
                    'case_id': case['case_id'],
                    'source_path': source_path,
                    'image_path': relative_path,
                    'reason': 'duplicate_source_within_case',
                    'detail': '',
                })
                continue
            seen_sources_in_case.add(source_path)

            if relative_path in seen_image_paths:
                rejected.append({
                    'case_id': case['case_id'],
                    'source_path': source_path,
                    'image_path': relative_path,
                    'reason': 'duplicate_local_path',
                    'detail': '',
                })
                continue

            info, reason, detail = inspect_image(local_path)
            if reason:
                rejected.append({
                    'case_id': case['case_id'],
                    'source_path': source_path,
                    'image_path': relative_path,
                    'reason': reason,
                    'detail': detail or '',
                })
                continue

            seen_image_paths.add(relative_path)
            valid_images_by_case[case['case_id']] += 1
            manifest.append({
                'case_id': case['case_id'],
                'image_path': relative_path,
                'source_path': source_path,
                'image_index': index,
                'label_en': case['label_en'],
                'label_vi': case['label_vi'],
                'class_id': case['class_id'],
                'label_weight': case['label_weight'],
                'width': info['width'],
                'height': info['height'],
                'format': info['format'],
                'content_sha256': info['content_sha256'],
            })

    manifest.sort(key=lambda row: (row['class_id'], row['case_id'], row['image_index']))
    write_csv(
        output_dir / 'dataset_images.csv',
        [
            'case_id', 'image_path', 'source_path', 'image_index', 'label_en',
            'label_vi', 'class_id', 'label_weight', 'width', 'height',
            'format', 'content_sha256',
        ],
        manifest,
    )
    write_csv(
        output_dir / 'rejected_images.csv',
        ['case_id', 'source_path', 'image_path', 'reason', 'detail'],
        rejected,
    )

    cases_without_images = []
    for case in cases:
        if valid_images_by_case[case['case_id']] == 0:
            cases_without_images.append({
                'case_id': case['case_id'],
                'class_id': case['class_id'],
                'label_en': case['label_en'],
                'label_vi': case['label_vi'],
                'label_weight': case['label_weight'],
                'reason': 'no_valid_images',
            })
    write_csv(
        output_dir / 'cases_without_valid_images.csv',
        ['case_id', 'class_id', 'label_en', 'label_vi', 'label_weight', 'reason'],
        cases_without_images,
    )

    content_groups = defaultdict(list)
    for row in manifest:
        content_groups[row['content_sha256']].append(row)
    duplicate_content = []
    for digest, items in content_groups.items():
        if len(items) < 2:
            continue
        duplicate_content.append({
            'content_sha256': digest,
            'image_count': len(items),
            'case_ids': ';'.join(item['case_id'] for item in items),
            'image_paths': ';'.join(item['image_path'] for item in items),
            'source_paths': ';'.join(item['source_path'] for item in items),
            'label_en_values': ';'.join(item['label_en'] for item in items),
            'class_id_values': ';'.join(str(item['class_id']) for item in items),
            'cross_case': len({item['case_id'] for item in items}) > 1,
            'cross_label': len({item['class_id'] for item in items}) > 1,
        })
    duplicate_content.sort(key=lambda row: (-row['image_count'], row['content_sha256']))
    write_csv(
        output_dir / 'duplicate_content_images.csv',
        [
            'content_sha256', 'image_count', 'case_ids', 'image_paths',
            'source_paths', 'label_en_values', 'class_id_values',
            'cross_case', 'cross_label',
        ],
        duplicate_content,
    )

    stats = []
    for class_id in sorted(mapping):
        class_cases = {
            row['case_id'] for row in manifest if row['class_id'] == class_id
        }
        class_images = [row for row in manifest if row['class_id'] == class_id]
        rejected_count = sum(
            1 for row in rejected
            if any(
                case['case_id'] == row['case_id'] and case['class_id'] == class_id
                for case in cases
            )
        )
        stats.append({
            'class_id': class_id,
            'label_en': mapping[class_id]['label_en'],
            'label_vi': mapping[class_id]['label_vi'],
            'valid_cases': len(class_cases),
            'valid_images': len(class_images),
            'rejected_images': rejected_count,
            'cases_without_valid_images': sum(
                1 for row in cases_without_images if row['class_id'] == class_id
            ),
            'avg_valid_images_per_case': (
                round(len(class_images) / len(class_cases), 4) if class_cases else 0
            ),
        })
    write_csv(
        output_dir / 'dataset_image_statistics.csv',
        [
            'class_id', 'label_en', 'label_vi', 'valid_cases', 'valid_images',
            'rejected_images', 'cases_without_valid_images',
            'avg_valid_images_per_case',
        ],
        stats,
    )

    print(f'Ca đầu vào: {len(cases)}')
    print(f'Ảnh hợp lệ: {len(manifest)}')
    print(f'Ảnh bị loại: {len(rejected)}')
    print(f'Ca không còn ảnh hợp lệ: {len(cases_without_images)}')
    print(f'Nhóm nội dung ảnh trùng: {len(duplicate_content)}')
    print(f'Đã ghi kết quả vào: {output_dir}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        sys.exit(1)

