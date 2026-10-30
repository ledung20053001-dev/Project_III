#!/usr/bin/env python3
"""Lọc SCIN: một ca, một nhãn có trọng số > 0.5, các đường dẫn ảnh.

Python 3.9+, không cần cài thư viện.
Đặt cạnh scin_cases.csv và scin_labels.csv rồi chạy: python loc_scin.py
Hoặc: python loc_scin.py --cases DUONG_DAN/scin_cases.csv --labels DUONG_DAN/scin_labels.csv
Kết quả: scin_single_label.csv (UTF-8 BOM để mở bằng Excel).
Chỉ xuất đường dẫn ảnh gốc, không tải hoặc nhúng ảnh.
case_id được đọc nguyên dạng chuỗi, không chuyển sang số thực.
Nhãn là nhãn cấp ca; các ảnh cùng ca phải ở cùng tập train/validation/test.
Trọng số không phải xác suất chẩn đoán đã được hiệu chuẩn.
"""
import argparse
import ast
import csv
import math
import sys
from collections import Counter
from pathlib import Path

IMAGE_COLS = ['image_1_path', 'image_2_path', 'image_3_path']

# Bảo đảm các thông báo tiếng Việt không lỗi trên terminal Windows.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


def read_rows(path, required):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path}: thiếu cột {sorted(missing)}')
        rows = {}
        for row in reader:
            cid = (row.get('case_id') or '').strip()
            if not cid or cid in rows:
                raise ValueError(f'{path}: case_id trống hoặc trùng tại dòng {reader.line_num}')
            rows[cid] = row
        return rows


def select_label(raw):
    if not raw or raw.strip().lower() in ('nan', 'null', 'none', '{}'):
        return None, None, 'không có nhãn'
    try:
        labels = ast.literal_eval(raw)
        if not isinstance(labels, dict) or not labels:
            raise ValueError()
        for name, weight in labels.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError()
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                raise ValueError()
            if not math.isfinite(weight) or not 0 <= weight <= 1:
                raise ValueError()
        # Cho phép sai lệch nhỏ do trọng số trong CSV được làm tròn.
        if abs(sum(labels.values()) - 1) > 0.05:
            raise ValueError()
    except (ValueError, SyntaxError, TypeError):
        return None, None, 'nhãn sai định dạng/trọng số không hợp lệ'
    selected = [
        (name.strip(), float(weight))
        for name, weight in labels.items()
        if weight > 0.5
    ]
    if len(selected) != 1:
        return None, None, 'không có đúng một nhãn > 0.5'
    primary_label, label_weight = selected[0]
    return primary_label, label_weight, None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--cases', default='scin_cases.csv')
    parser.add_argument('--labels', default='scin_labels.csv')
    parser.add_argument('--output', default='scin_single_label.csv')
    args = parser.parse_args()
    output = Path(args.output)
    if output.resolve() in (Path(args.cases).resolve(), Path(args.labels).resolve()):
        raise ValueError('File đầu ra không được trùng file đầu vào.')
    if output.exists():
        raise ValueError('File đầu ra đã tồn tại. Hãy chọn tên mới bằng --output để tránh ghi đè.')
    cases = read_rows(args.cases, ['case_id'] + IMAGE_COLS)
    labels = read_rows(args.labels, ['case_id', 'weighted_skin_condition_label'])
    selected_rows, skipped = [], Counter()
    for cid, case in cases.items():
        if cid not in labels:
            skipped['không tìm thấy case_id trong file nhãn'] += 1
            continue
        primary_label, label_weight, reason = select_label(
            labels[cid]['weighted_skin_condition_label']
        )
        if reason:
            skipped[reason] += 1
            continue
        images = {col: (case.get(col) or '').strip() for col in IMAGE_COLS}
        images = {col: '' if value.lower() in ('nan', 'none', 'null') else value for col, value in images.items()}
        if not any(images.values()):
            skipped['không có đường dẫn ảnh'] += 1
            continue
        selected_rows.append({
            'case_id': cid,
            'primary_label': primary_label,
            'label_weight': label_weight,
            **images,
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['case_id', 'primary_label', 'label_weight'] + IMAGE_COLS)
        writer.writeheader()
        writer.writerows(selected_rows)
    print(f'Tổng ca đầu vào: {len(cases)}')
    print(f'Ca giữ lại: {len(selected_rows)}')
    print(f'Số đường dẫn ảnh: {sum(bool(r[c]) for r in selected_rows for c in IMAGE_COLS)}')
    for reason, count in skipped.items():
        print(f'Bỏ qua {count} ca: {reason}')
    unmatched = len(set(labels) - set(cases))
    print(f'Ca trong file nhãn nhưng không có trong file ca: {unmatched}')
    print(f'Đã tạo: {output.resolve()}')
    print('Đường dẫn ảnh được giữ nguyên; chưa kiểm tra ảnh tồn tại hoặc chất lượng ảnh.')
    print('Khi mở Excel, nhập case_id dưới dạng Text để tránh mất chính xác mã ca.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        sys.exit(1)
