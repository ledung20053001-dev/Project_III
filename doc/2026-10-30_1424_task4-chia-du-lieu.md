# Báo cáo task: Task 4 — Chia train/validation/test theo nhóm ca

## Thông tin

- Thời gian bắt đầu: `2026-10-30 14:15 UTC+07:00`
- Thời gian hoàn thành: `2026-10-30 14:24:53 UTC+07:00`
- Trạng thái: `Hoàn thành`

## Yêu cầu

Chia dữ liệu 70/15/15 theo ca, giữ tỷ lệ lớp, tạo group_id cho các ca có ảnh trùng nội dung, ngăn mọi dạng rò rỉ đã kiểm tra, lưu cấu hình tái lập và tính class weights từ riêng tập train.

## Công việc đã thực hiện

1. Tạo các thành phần liên thông của case_id theo content SHA-256.
2. Kiểm tra mỗi nhóm chỉ chứa một class_id.
3. Gán group_id xác định từ danh sách case_id đã sắp xếp.
4. Chia phân tầng theo từng lớp và group với seed 42.
5. Gán toàn bộ ảnh của ca về split của group.
6. Xuất train, validation, test, bảng phân công ca và thống kê.
7. Kiểm tra giao nhau theo case, group, đường dẫn và nội dung ảnh.
8. Lưu hash manifest/mapping, seed, tỷ lệ, thuật toán và số lượng mục tiêu.
9. Tính class weights từ số ảnh train theo đúng class_id.
10. Chạy lại và so sánh SHA-256 để kiểm tra khả năng tái lập.
11. Cập nhật README và tài liệu Task 4.

## File và vị trí thay đổi

| Thao tác | File | Vị trí | Nội dung |
|---|---|---|---|
| Tạo | `scripts/task4_split_dataset.py` | Toàn bộ file | Thuật toán grouped stratified split và kiểm tra rò rỉ. |
| Tạo | `data/metadata/train.csv` | Toàn bộ file | 732 ca, 1.551 ảnh. |
| Tạo | `data/metadata/val.csv` | Toàn bộ file | 158 ca, 333 ảnh. |
| Tạo | `data/metadata/test.csv` | Toàn bộ file | 156 ca, 330 ảnh. |
| Tạo | `data/metadata/case_split_assignments.csv` | Toàn bộ file | Phân công cố định case/group/split. |
| Tạo | `data/metadata/split_summary.csv` | Toàn bộ file | Phân bố lớp trong từng split. |
| Tạo | `data/metadata/split_validation.json` | Toàn bộ file | Kết quả kiểm tra rò rỉ. |
| Tạo | `data/metadata/split_config.json` | Toàn bộ file | Cấu hình và hash tái lập. |
| Tạo | `data/metadata/train_class_weights.json` | Toàn bộ file | Class weights tính từ train. |
| Tạo | `doc/task4_dataset_split.md` | Toàn bộ file | Phân tích kết quả Task 4. |
| Sửa | `README.md` | Mục `Tiến độ thực hiện` | Đánh dấu hoàn thành chia dữ liệu. |
| Sửa | `doc/README.md` | Mục `Danh sách báo cáo` | Thêm báo cáo Task 4. |

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Tổng ảnh ba tập | 2.214, bằng manifest. |
| Giao case_id theo từng cặp | 0. |
| Giao group_id theo từng cặp | 0. |
| Giao image_path theo từng cặp | 0. |
| Giao content_sha256 theo từng cặp | 0. |
| Mỗi ảnh được gán đúng một tập | Đạt. |
| Lớp hiện diện trong mỗi tập | Đủ class_id 0–7. |
| Nhãn khớp mapping | Đạt. |
| Nhóm trùng bị tách | 0. |
| Chạy lại với seed 42 | Bốn file chính có SHA-256 giống hệt. |
| Cú pháp script | Đạt: `SYNTAX_OK`. |

## Kết quả

Split hoàn chỉnh gồm train 732 ca/1.551 ảnh, validation 158 ca/333 ảnh và test 156 ca/330 ảnh. Ba cặp ca có nội dung ảnh trùng được giữ trong cùng group và cùng nằm ở train. Không phát hiện rò rỉ theo các định danh hoặc hash đã kiểm tra.

## Lưu ý và bước tiếp theo

- Dùng chung các CSV split này cho mọi mô hình để so sánh công bằng.
- Chọn checkpoint và weighted/unweighted loss bằng validation Macro F1, không dùng test.
- Psoriasis và Tinea chỉ có 8 ca ở mỗi validation/test; Herpes Simplex có 8 ca validation và 7 ca test nên Recall theo lớp có thể dao động mạnh.

