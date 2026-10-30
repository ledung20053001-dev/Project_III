# Task 3 — Phân tích mất cân bằng lớp

## Kết luận

Dữ liệu có mất cân bằng đáng kể giữa các lớp. Lớp lớn nhất có số ca gấp 6,25 lần và số ảnh gấp 7,02 lần lớp nhỏ nhất. Tuy nhiên, Task 3 chưa tạo class weights vì trọng số huấn luyện phải được tính lại từ riêng tập train sau Task 4.

## Phân bố toàn bộ manifest

| ID | Nhãn | Số ca | Tỷ lệ ca | Số ảnh | Tỷ lệ ảnh | Nội dung ảnh duy nhất | Ảnh/ca |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | Eczema | 319 | 30,50% | 695 | 31,39% | 695 | 2,18 |
| 1 | Allergic Contact Dermatitis | 196 | 18,74% | 412 | 18,61% | 410 | 2,10 |
| 2 | Urticaria | 165 | 15,77% | 332 | 15,00% | 332 | 2,01 |
| 3 | Insect Bite | 120 | 11,47% | 262 | 11,83% | 262 | 2,18 |
| 4 | Folliculitis | 85 | 8,13% | 185 | 8,36% | 183 | 2,18 |
| 5 | Psoriasis | 55 | 5,26% | 108 | 4,88% | 108 | 1,96 |
| 6 | Tinea | 55 | 5,26% | 121 | 5,47% | 121 | 2,20 |
| 7 | Herpes Simplex | 51 | 4,88% | 99 | 4,47% | 96 | 1,94 |
| **Tổng** |  | **1.046** | **100%** | **2.214** | **100%** | **2.207** |  |

Tỷ lệ phần trăm trong CSV có thể cộng thành 99,9999% do làm tròn bốn chữ số thập phân.

## Mức chênh lệch

- Lớp nhiều ca nhất: Eczema, 319 ca.
- Lớp ít ca nhất: Herpes Simplex, 51 ca.
- `R_case = 319 / 51 = 6,2549`.
- Lớp nhiều ảnh nhất: Eczema, 695 ảnh.
- Lớp ít ảnh nhất: Herpes Simplex, 99 ảnh.
- `R_image = 695 / 99 = 7,0202`.
- Nếu luôn dự đoán lớp nhiều ảnh nhất là Eczema, accuracy trên toàn bộ manifest chỉ đạt khoảng 31,39%; đây là majority-class baseline, không phải mô hình hữu ích.

## Ảnh trùng nội dung

Manifest có 2.214 file hợp lệ nhưng chỉ có 2.207 nội dung pixel duy nhất:

- Allergic Contact Dermatitis: 412 file, 410 nội dung duy nhất.
- Folliculitis: 185 file, 183 nội dung duy nhất.
- Herpes Simplex: 99 file, 96 nội dung duy nhất.

Task 3 giữ cả hai con số để minh bạch. Task 4 phải giữ các ca có ảnh trùng trong cùng một tập. Trước khi huấn luyện, pipeline cần quyết định có loại bản sao khỏi tập train hay giữ chúng nhưng ràng buộc nhóm; quyết định đó phải áp dụng nhất quán và được ghi nhận.

## Quyết định huấn luyện

Sau Task 4:

1. Tính lại số ảnh mỗi lớp trong riêng tập train.
2. Tạo class weights theo thứ tự class_id bằng công thức `N / (K × n_c)`.
3. Huấn luyện ít nhất hai cấu hình trên cùng bộ chia:
   - CrossEntropyLoss không trọng số — baseline.
   - CrossEntropyLoss có class weights tính từ train.
4. Chọn cấu hình bằng validation Macro F1 và kiểm tra Recall từng lớp.
5. Không dùng test để chọn cấu hình.
6. Không oversample hoặc cân bằng validation/test.
7. Chưa kết hợp class weighting và oversampling mạnh trong vòng thử nghiệm đầu tiên.

`label_weight` của ca không phải `class_weight` và không được tự động dùng làm trọng số loss.

## Đầu ra

- `data/metadata/class_distribution.csv`: phân bố toàn bộ dữ liệu.
- `results/data_analysis/cases_per_class.png`: biểu đồ số ca.
- `results/data_analysis/images_per_class.png`: biểu đồ số ảnh.
- `results/data_analysis/imbalance_summary.json`: các tỷ lệ và quyết định xử lý.
- `scripts/task3_analyze_class_distribution.py`: script tái tạo kết quả.

