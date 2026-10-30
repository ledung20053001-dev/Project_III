# Task 4 — Chia train, validation và test

## Kết quả tổng quan

Dữ liệu được chia theo nhóm ca với tỷ lệ mục tiêu 70/15/15 và seed 42. Các ca có ảnh trùng nội dung được nối thành thành phần liên thông và nhận cùng một `group_id`; group là đơn vị không được tách khi chia.

| Split | Số ca | Tỷ lệ ca | Số ảnh | Tỷ lệ ảnh | Số group |
|---|---:|---:|---:|---:|---:|
| Train | 732 | 69,98% | 1.551 | 70,05% | 729 |
| Validation | 158 | 15,11% | 333 | 15,04% | 158 |
| Test | 156 | 14,91% | 330 | 14,91% | 156 |
| **Tổng** | **1.046** | **100%** | **2.214** | **100%** | **1.043** |

Validation có nhiều hơn test hai ca do làm tròn tỷ lệ độc lập trong từng lớp. Mỗi lớp đạt đúng số ca mục tiêu đã tính và cả ba tập đều có đủ tám lớp.

## Phân bố ca theo lớp

| ID | Nhãn | Train | Validation | Test | Tổng |
|---:|---|---:|---:|---:|---:|
| 0 | Eczema | 223 | 48 | 48 | 319 |
| 1 | Allergic Contact Dermatitis | 137 | 30 | 29 | 196 |
| 2 | Urticaria | 115 | 25 | 25 | 165 |
| 3 | Insect Bite | 84 | 18 | 18 | 120 |
| 4 | Folliculitis | 59 | 13 | 13 | 85 |
| 5 | Psoriasis | 39 | 8 | 8 | 55 |
| 6 | Tinea | 39 | 8 | 8 | 55 |
| 7 | Herpes Simplex | 36 | 8 | 7 | 51 |

## Phân bố ảnh theo lớp

| ID | Nhãn | Train | Validation | Test | Tổng |
|---:|---|---:|---:|---:|---:|
| 0 | Eczema | 489 | 99 | 107 | 695 |
| 1 | Allergic Contact Dermatitis | 301 | 57 | 54 | 412 |
| 2 | Urticaria | 230 | 56 | 46 | 332 |
| 3 | Insect Bite | 183 | 40 | 39 | 262 |
| 4 | Folliculitis | 118 | 34 | 33 | 185 |
| 5 | Psoriasis | 77 | 16 | 15 | 108 |
| 6 | Tinea | 86 | 18 | 17 | 121 |
| 7 | Herpes Simplex | 67 | 13 | 19 | 99 |

Tỷ lệ ảnh không được ép chính xác vì mục tiêu chia đặt theo số ca và mỗi ca có số ảnh khác nhau.

## Nhóm ca có ảnh trùng

Ba nhóm gồm hai ca được phát hiện và đều được giữ nguyên trong train:

- Allergic Contact Dermatitis: `1754947382186897051`, `7151606719275056352`.
- Folliculitis: `-2051363250643774652`, `-5913922383533072974`.
- Herpes Simplex: `-4149065585657858240`, `-8373370638802672214`.

Bảy hash ảnh trùng của Task 3 tạo thành ba nhóm liên thông trên. Không có nhóm chứa nhiều class_id.

## Kiểm tra rò rỉ

Tất cả giao nhau theo cặp train–validation, train–test và validation–test đều bằng 0 đối với:

- `case_id`;
- `group_id`;
- `image_path` đã chuẩn hóa;
- `content_sha256`.

Mỗi ảnh được gán đúng một split, tổng ảnh ba tập bằng 2.214 và mọi split đều có class_id 0–7.

## Class weights từ train

Class weights được tính duy nhất từ 1.551 ảnh train theo công thức `N / (K × n_c)`:

| ID | Nhãn | Ảnh train | Class weight |
|---:|---|---:|---:|
| 0 | Eczema | 489 | 0,39647239 |
| 1 | Allergic Contact Dermatitis | 301 | 0,64410299 |
| 2 | Urticaria | 230 | 0,84293478 |
| 3 | Insect Bite | 183 | 1,05942623 |
| 4 | Folliculitis | 118 | 1,64300847 |
| 5 | Psoriasis | 77 | 2,51785714 |
| 6 | Tinea | 86 | 2,25436047 |
| 7 | Herpes Simplex | 67 | 2,89365672 |

Các trọng số được lưu đúng thứ tự class_id. Đây là `class_weight`, không phải `label_weight` của từng ca.

## Khả năng tái lập

- Seed: 42.
- Manifest đầu vào và class mapping được lưu kèm SHA-256.
- Thuật toán dùng Python standard library, không phụ thuộc sklearn.
- Bảng `case_split_assignments.csv` là nguồn phân công cố định cho mọi mô hình.
- Chạy lại script tạo ra các file train/val/test và bảng phân công có SHA-256 giống hệt.

## Đầu ra

- `data/metadata/train.csv`.
- `data/metadata/val.csv`.
- `data/metadata/test.csv`.
- `data/metadata/case_split_assignments.csv`.
- `data/metadata/split_summary.csv`.
- `data/metadata/split_validation.json`.
- `data/metadata/split_config.json`.
- `data/metadata/train_class_weights.json`.
- `scripts/task4_split_dataset.py`.

Validation được dùng để chọn checkpoint và so sánh weighted/unweighted loss. Test chỉ được dùng một lần để đánh giá cuối sau khi chốt cấu hình.

