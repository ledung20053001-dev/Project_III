# Báo cáo task: Task 2 — Xây dựng danh mục ảnh

## Thông tin

- Thời gian bắt đầu: `2026-10-30 13:55 UTC+07:00`
- Thời gian hoàn thành: `2026-10-30 14:03:41 UTC+07:00`
- Trạng thái: `Hoàn thành`

## Yêu cầu

Chuyển `selected_cases.csv` từ một dòng cho mỗi ca thành `dataset_images.csv` một dòng cho mỗi ảnh; xác thực ảnh thực tế, giữ mapping Task 1, ghi ảnh bị loại, thống kê sau kiểm tra và phát hiện ảnh trùng nội dung. Không sao chép ảnh và chưa chia tập dữ liệu.

## Công việc đã thực hiện

1. Tạo script Task 2 có thể chạy lại.
2. Kiểm tra mapping liên tục từ 0 đến N-1 và đối chiếu nhãn Anh/Việt của từng ca.
3. Giữ `case_id` dạng chuỗi và dùng đường dẫn ảnh tương đối từ gốc dự án.
4. Kiểm tra tồn tại, PIL `verify()`, mở lại, `load()`, kích thước và chuyển RGB cho từng ảnh.
5. Tính hash nội dung pixel RGB để phát hiện ảnh giống nhau dù khác tên file.
6. Tạo manifest, danh sách ảnh bị loại, ca mất ảnh, thống kê lớp và nhóm ảnh trùng.
7. Kiểm tra tính duy nhất của đường dẫn ảnh, nhãn theo ca, kích thước và tổng thống kê.
8. Cập nhật README và tài liệu phân tích Task 2.

## File và vị trí thay đổi

| Thao tác | File | Vị trí | Nội dung |
|---|---|---|---|
| Tạo | `scripts/task2_build_image_manifest.py` | Toàn bộ file | Pipeline xác thực ảnh và tạo manifest. |
| Tạo | `data/metadata/dataset_images.csv` | Toàn bộ file | 2.214 ảnh hợp lệ, một dòng mỗi ảnh. |
| Tạo | `data/metadata/rejected_images.csv` | Toàn bộ file | Một ảnh bị loại và lý do. |
| Tạo | `data/metadata/cases_without_valid_images.csv` | Toàn bộ file | Header; không có ca nào mất toàn bộ ảnh. |
| Tạo | `data/metadata/dataset_image_statistics.csv` | Toàn bộ file | Thống kê theo 8 lớp sau kiểm tra. |
| Tạo | `data/metadata/duplicate_content_images.csv` | Toàn bộ file | 7 nhóm ảnh trùng nội dung. |
| Tạo | `doc/task2_image_manifest.md` | Toàn bộ file | Giải thích kết quả và ràng buộc bước chia dữ liệu. |
| Sửa | `README.md` | Mục `Tiến độ thực hiện` | Đánh dấu hoàn thành kiểm tra và lập manifest ảnh. |
| Sửa | `doc/README.md` | Mục `Danh sách báo cáo` | Thêm báo cáo Task 2. |

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Ca đầu vào | 1.046. |
| Ảnh hợp lệ | 2.214. |
| Đường dẫn manifest duy nhất | 2.214/2.214. |
| Ca có nhiều class_id | 0. |
| Ảnh bị loại | 1 ảnh Tinea, `file_not_found`. |
| Ca không còn ảnh hợp lệ | 0. |
| File manifest bị thiếu trên đĩa | 0. |
| Kích thước không hợp lệ | 0. |
| Hash nội dung bị thiếu | 0. |
| Định dạng PIL | 2.214 JPEG. |
| Nhóm trùng nội dung | 7 nhóm, đều khác ca nhưng cùng nhãn. |
| Tổng thống kê theo lớp | 1.046 ca, 2.214 ảnh. |

## Kết quả

`dataset_images.csv` đã sẵn sàng làm đầu vào cho bước chia dữ liệu. Mỗi dòng trỏ đến một ảnh đã giải mã hoàn chỉnh, có mapping nhãn cố định và truy ngược được về ca gốc.

## Lưu ý và bước tiếp theo

- Bước chia dữ liệu phải giữ các ca có ảnh trùng nội dung trong cùng một tập.
- Chưa tạo `train.csv`, `val.csv`, `test.csv`.
- Chưa resize hoặc đánh giá y khoa/chất lượng thị giác của ảnh; Task 2 chỉ xác nhận tính hợp lệ kỹ thuật.

