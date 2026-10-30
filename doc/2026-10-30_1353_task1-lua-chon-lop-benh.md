# Báo cáo task: Task 1 — Lựa chọn lớp bệnh

## Thông tin

- Thời gian bắt đầu: `2026-10-30 13:49 UTC+07:00`
- Thời gian hoàn thành: `2026-10-30 13:53:12 UTC+07:00`
- Trạng thái: `Hoàn thành, chờ Task 2 xác thực nội dung ảnh`

## Yêu cầu

Thống kê dữ liệu sau lọc single-label, chọn tập lớp có khả năng huấn luyện và đánh giá, cố định class_id, lưu mapping và danh sách ca cho Task 2. Không gộp nhãn chỉ vì tên gần nhau; phân biệt label_weight với class weight.

## Công việc đã thực hiện

1. Tạo dữ liệu single-label theo ngưỡng `label_weight > 0.5`.
2. Kiểm tra 1.910 `case_id` là duy nhất và mỗi ca chỉ có một `primary_label`.
3. Thống kê 167 lớp theo số ca, đường dẫn ảnh duy nhất và ảnh local tồn tại.
4. Chọn 8 lớp có ít nhất 50 ca; không gộp nhãn.
5. Cố định class_id từ 0 đến 7.
6. Bổ sung bốn bản dịch tiếng Việt còn thiếu.
7. Tạo script Task 1 có thể chạy lại và các file đầu ra.
8. Phát hiện 11 đường dẫn ảnh nguồn được nhiều ca tham chiếu và xuất danh sách riêng.
9. Xác định một ảnh Tinea được tham chiếu nhưng thiếu local.
10. Kiểm tra schema, tổng số ca, tỷ lệ phần trăm và khả năng chạy lại script.

## File và vị trí thay đổi

| Thao tác | File | Vị trí | Nội dung |
|---|---|---|---|
| Tạo | `scripts/task1_select_classes.py` | Toàn bộ file | Thống kê lớp, kiểm tra dữ liệu, chọn lớp và xuất mapping/case. |
| Sửa | `labels_vi.json` | Cuối mapping | Thêm Allergic Contact Dermatitis, Insect Bite, Tinea và Herpes Simplex. |
| Tạo | `data/metadata/scin_single_label_05.csv` | Toàn bộ file | 1.910 ca sau lọc ngưỡng 0.5. |
| Tạo | `data/metadata/class_statistics.csv` | Toàn bộ file | Thống kê 167 lớp. |
| Tạo | `data/metadata/selected_classes.csv` | Toàn bộ file | Thống kê tám lớp được chọn. |
| Tạo | `data/metadata/selected_cases.csv` | Toàn bộ file | Danh sách 1.046 ca được chọn. |
| Tạo | `data/metadata/class_mapping.json` | Toàn bộ file | Mapping class_id cố định. |
| Tạo | `data/metadata/duplicate_image_references.csv` | Toàn bộ file | 11 đường dẫn ảnh bị tham chiếu nhiều lần. |
| Tạo | `doc/task1_class_selection.md` | Toàn bộ file | Giải thích quyết định và hạn chế Task 1. |
| Sửa | `README.md` | Mục `Tiến độ thực hiện` | Cập nhật tiến độ Task 1 và việc còn lại ở Task 2. |
| Sửa | `doc/README.md` | Mục `Danh sách báo cáo` | Thêm báo cáo hoàn thành. |

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Cú pháp hai script | Đạt: `SYNTAX_OK`. |
| Chạy lại `task1_select_classes.py` | Đạt, exit code 0. |
| Tính duy nhất case_id được chọn | 1.046/1.046. |
| Tổng số lớp | 167 lớp sau lọc, 8 lớp được chọn. |
| Tổng số ảnh | 2.208 đường dẫn duy nhất, 2.207 có file local, 1 thiếu. |
| Tổng case percentage | 99,9999% do làm tròn. |
| Tổng image percentage | 100%. |
| Mapping | Có đủ class_id 0–7 và tên Anh/Việt. |
| Ảnh trùng metadata | 11 đường dẫn; 2 đường dẫn xuất hiện ở các nhãn khác nhau. |

## Kết quả

Đã chốt phạm vi ban đầu gồm Eczema, Allergic Contact Dermatitis, Urticaria, Insect Bite, Folliculitis, Psoriasis, Tinea và Herpes Simplex. Tổng cộng 1.046 ca và 2.207 ảnh local tồn tại, chưa xác thực nội dung ảnh.

## Lưu ý và bước tiếp theo

- Task 2 phải mở ảnh để kiểm tra tính hợp lệ trước khi chốt số ảnh sử dụng được.
- Các ca dùng chung đường dẫn ảnh phải được giữ cùng một bộ chia hoặc xử lý theo quy tắc rõ ràng.
- Chưa tạo train/validation/test và chưa tính class weight.
- Các lớp dưới 50 ca được giữ trong thống kê nhưng chưa thuộc phạm vi mô hình phiên bản đầu.

