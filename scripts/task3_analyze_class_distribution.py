#!/usr/bin/env python3
"""Phân tích phân bố lớp trên toàn bộ dataset_images.csv.

Task 3 chỉ thống kê dữ liệu toàn bộ. Script không chia dữ liệu, không tạo
class weights và không thay đổi cách lấy mẫu. Class weights chỉ được tính từ
tập train sau Task 4.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='data/metadata/dataset_images.csv')
    parser.add_argument('--mapping', default='data/metadata/class_mapping.json')
    parser.add_argument('--distribution', default='data/metadata/class_distribution.csv')
    parser.add_argument('--results-dir', default='results/data_analysis')
    return parser.parse_args()


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
    required = {
        'case_id', 'image_path', 'label_en', 'label_vi', 'class_id',
        'label_weight', 'content_sha256',
    }
    rows = []
    seen_paths = set()
    case_classes = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path}: thiếu cột {sorted(missing)}')
        for row in reader:
            line = reader.line_num
            case_id = (row.get('case_id') or '').strip()
            image_path = (row.get('image_path') or '').strip()
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
            expected = mapping[class_id]
            if row['label_en'] != expected['label_en'] or row['label_vi'] != expected['label_vi']:
                raise ValueError(f'{path}: nhãn không khớp mapping tại dòng {line}')
            if case_id in case_classes and case_classes[case_id] != class_id:
                raise ValueError(f'{path}: case_id {case_id} có nhiều class_id')
            case_classes[case_id] = class_id
            rows.append({
                'case_id': case_id,
                'image_path': image_path,
                'class_id': class_id,
                'content_sha256': content_hash,
            })
    if not rows:
        raise ValueError(f'{path}: manifest rỗng')
    return rows


def analyze(rows, mapping):
    by_class = defaultdict(list)
    for row in rows:
        by_class[row['class_id']].append(row)
    absent = [class_id for class_id in mapping if not by_class[class_id]]
    if absent:
        raise ValueError(f'Các lớp không có ảnh hợp lệ: {absent}')

    total_cases = len({row['case_id'] for row in rows})
    total_images = len(rows)
    total_unique_content = len({row['content_sha256'] for row in rows})
    distribution = []
    for class_id in sorted(mapping):
        class_rows = by_class[class_id]
        cases = {row['case_id'] for row in class_rows}
        unique_content = {row['content_sha256'] for row in class_rows}
        total_class_images = len(class_rows)
        distribution.append({
            'class_id': class_id,
            'label_en': mapping[class_id]['label_en'],
            'label_vi': mapping[class_id]['label_vi'],
            'total_cases': len(cases),
            'total_images': total_class_images,
            'unique_content_images': len(unique_content),
            'duplicate_content_images': total_class_images - len(unique_content),
            'case_percentage': round(len(cases) / total_cases * 100, 4),
            'image_percentage': round(total_class_images / total_images * 100, 4),
            'unique_content_percentage': round(
                len(unique_content) / total_unique_content * 100,
                4,
            ),
            'images_per_case': round(total_class_images / len(cases), 4),
        })

    case_counts = [row['total_cases'] for row in distribution]
    image_counts = [row['total_images'] for row in distribution]
    summary = {
        'total_classes': len(mapping),
        'total_cases': total_cases,
        'total_images': total_images,
        'total_unique_content_images': total_unique_content,
        'duplicate_content_images': total_images - total_unique_content,
        'max_case_count': max(case_counts),
        'min_case_count': min(case_counts),
        'case_imbalance_ratio': round(max(case_counts) / min(case_counts), 4),
        'max_image_count': max(image_counts),
        'min_image_count': min(image_counts),
        'image_imbalance_ratio': round(max(image_counts) / min(image_counts), 4),
        'majority_class_by_cases': max(distribution, key=lambda row: row['total_cases'])['label_en'],
        'minority_class_by_cases': min(distribution, key=lambda row: row['total_cases'])['label_en'],
        'majority_class_by_images': max(distribution, key=lambda row: row['total_images'])['label_en'],
        'minority_class_by_images': min(distribution, key=lambda row: row['total_images'])['label_en'],
        'majority_class_image_baseline_accuracy_percent': max(
            row['image_percentage'] for row in distribution
        ),
        'decision': (
            'Sau Task 4, tính class weights chỉ từ số ảnh train theo đúng thứ tự '
            'class_id. So sánh CrossEntropyLoss không trọng số và có trọng số '
            'trên cùng bộ chia bằng validation Macro F1 và Recall từng lớp. '
            'Không cân bằng validation/test và không dùng test để chọn phương pháp.'
        ),
    }
    return distribution, summary


def write_csv(path, rows):
    fieldnames = [
        'class_id', 'label_en', 'label_vi', 'total_cases', 'total_images',
        'unique_content_images', 'duplicate_content_images', 'case_percentage',
        'image_percentage', 'unique_content_percentage', 'images_per_case',
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_font(size, bold=False):
    candidates = [
        Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),
        Path('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_bar_chart(rows, value_key, title, y_label, output_path):
    width, height = 1600, 900
    margin_left, margin_right = 130, 70
    margin_top, margin_bottom = 110, 230
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    background = '#F7F9FC'
    navy = '#17324D'
    blue = '#3274A1'
    grid = '#D7DFE8'
    image = Image.new('RGB', (width, height), background)
    draw = ImageDraw.Draw(image)
    title_font = get_font(34, bold=True)
    label_font = get_font(20)
    value_font = get_font(18, bold=True)
    small_font = get_font(16)

    draw.text((margin_left, 35), title, fill=navy, font=title_font)
    values = [int(row[value_key]) for row in rows]
    maximum = max(values)
    tick_max = max(1, ((maximum + 49) // 50) * 50)
    for tick_index in range(6):
        value = tick_max * tick_index / 5
        y = margin_top + chart_height - chart_height * tick_index / 5
        draw.line((margin_left, y, width - margin_right, y), fill=grid, width=2)
        text = str(round(value))
        draw.text((margin_left - 70, y - 10), text, fill=navy, font=small_font)

    slot_width = chart_width / len(rows)
    bar_width = slot_width * 0.62
    for index, row in enumerate(rows):
        value = int(row[value_key])
        x0 = margin_left + index * slot_width + (slot_width - bar_width) / 2
        x1 = x0 + bar_width
        y1 = margin_top + chart_height
        y0 = y1 - chart_height * value / tick_max
        draw.rounded_rectangle((x0, y0, x1, y1), radius=8, fill=blue)
        value_text = str(value)
        value_box = draw.textbbox((0, 0), value_text, font=value_font)
        draw.text(
            ((x0 + x1 - (value_box[2] - value_box[0])) / 2, y0 - 30),
            value_text,
            fill=navy,
            font=value_font,
        )
        label = row['label_en']
        if len(label) > 23:
            label = label[:21] + '…'
        center = (x0 + x1) / 2
        draw.text((center - 8, y1 + 18), str(row['class_id']), fill=navy, font=value_font)
        draw.text((center - 60, y1 + 55), label, fill=navy, font=small_font)

    draw.text((18, margin_top + chart_height / 2), y_label, fill=navy, font=label_font)
    draw.text(
        (margin_left, height - 55),
        'Class ID and English label (full labels are preserved in class_distribution.csv)',
        fill=navy,
        font=small_font,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format='PNG')


def main():
    args = parse_args()
    mapping = load_mapping(args.mapping)
    rows = read_manifest(args.manifest, mapping)
    distribution, summary = analyze(rows, mapping)
    distribution_path = Path(args.distribution)
    results_dir = Path(args.results_dir)
    write_csv(distribution_path, distribution)
    results_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / 'imbalance_summary.json').open('w', encoding='utf-8') as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    draw_bar_chart(
        distribution,
        'total_cases',
        'Number of cases per class',
        'Cases',
        results_dir / 'cases_per_class.png',
    )
    draw_bar_chart(
        distribution,
        'total_images',
        'Number of valid images per class',
        'Images',
        results_dir / 'images_per_class.png',
    )
    print(f"Tổng lớp: {summary['total_classes']}")
    print(f"Tổng ca: {summary['total_cases']}")
    print(f"Tổng ảnh: {summary['total_images']}")
    print(f"Nội dung ảnh duy nhất: {summary['total_unique_content_images']}")
    print(f"R_case: {summary['case_imbalance_ratio']}")
    print(f"R_image: {summary['image_imbalance_ratio']}")
    print(f'Đã ghi: {distribution_path.resolve()}')
    print(f'Biểu đồ và tóm tắt: {results_dir.resolve()}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        sys.exit(1)

