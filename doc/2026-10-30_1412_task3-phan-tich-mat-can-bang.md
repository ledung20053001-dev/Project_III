# Báo cáo task: Task 3 — Phân tích mất cân bằng lớp

## Thông tin

- Thời gian bắt đầu: `2026-10-30 14:08 UTC+07:00`
- Thời gian hoàn thành: `2026-10-30 14:12:42 UTC+07:00`
- Trạng thái: `Hoàn thành`

## Yêu cầu

Thống kê số ca và số ảnh mỗi lớp từ `dataset_images.csv`, tính mức chênh lệch, tạo hai biểu đồ riêng và ghi quyết định xử lý mất cân bằng. Không tính class weights trước khi có tập train ở Task 4.

## Công việc đã thực hiện

1. Kiểm tra manifest, mapping, tính duy nhất của `image_path` và một class_id cho mỗi ca.
2. Tính số ca, file ảnh, nội dung ảnh duy nhất, tỷ lệ và ảnh trung bình trên ca cho tám lớp.
3. Tính `R_case`, `R_image` và majority-class baseline.
4. Tạo `class_distribution.csv` và tóm tắt JSON.
5. Tạo hai biểu đồ PNG bằng Pillow vì môi trường chưa có matplotlib.
6. Kiểm tra trực quan hai biểu đồ.
7. Ghi quyết định so sánh unweighted/weighted loss sau Task 4.
8. Cập nhật README và tài liệu Task 3.

## File và vị trí thay đổi

| Thao tác | File | Vị trí | Nội dung |
|---|---|---|---|
| Tạo | `scripts/task3_analyze_class_distribution.py` | Toàn bộ file | Phân tích phân bố và sinh biểu đồ. |
| Tạo | `data/metadata/class_distribution.csv` | Toàn bộ file | Phân bố tám lớp. |
| Tạo | `results/data_analysis/imbalance_summary.json` | Toàn bộ file | Tóm tắt tỷ lệ và quyết định. |
| Tạo | `results/data_analysis/cases_per_class.png` | Toàn bộ file | Biểu đồ số ca theo lớp. |
| Tạo | `results/data_analysis/images_per_class.png` | Toàn bộ file | Biểu đồ số ảnh theo lớp. |
| Tạo | `doc/task3_class_imbalance.md` | Toàn bộ file | Phân tích và quyết định xử lý. |
| Sửa | `README.md` | Mục `Tiến độ thực hiện` | Đánh dấu hoàn thành phân tích mất cân bằng. |
| Sửa | `doc/README.md` | Mục `Danh sách báo cáo` | Thêm báo cáo Task 3. |

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Cú pháp script | Đạt: `SYNTAX_OK`. |
| Chạy lại script | Đạt, exit code 0. |
| Tổng lớp | 8. |
| Tổng ca | 1.046. |
| Tổng file ảnh | 2.214. |
| Nội dung ảnh duy nhất | 2.207. |
| Tổng tỷ lệ ca | 99,9999% do làm tròn. |
| Tổng tỷ lệ ảnh | 99,9999% do làm tròn. |
| `R_case` | 6,2549. |
| `R_image` | 7,0202. |
| Kiểm tra biểu đồ | Đạt; tiêu đề, trục, nhãn lớp và giá trị hiển thị rõ. |

## Kết quả

Dữ liệu mất cân bằng đáng kể: Eczema chiếm 31,39% số ảnh, còn Herpes Simplex chiếm 4,47%. Chưa tạo class weights. Sau Task 4 sẽ tính trọng số từ riêng tập train và so sánh weighted với unweighted loss bằng validation Macro F1 và Recall từng lớp.

## Lưu ý và bước tiếp theo

- Task 4 phải chia theo ca và giữ các ca có ảnh trùng nội dung trong cùng tập.
- Validation/test không được oversample hoặc cân bằng nhân tạo.
- Không sử dụng test để quyết định có dùng weighted loss hay không.

