# Nhật ký công việc dự án

Thư mục `doc/` lưu báo cáo của từng task sau khi hoàn thành. Mục đích là giúp theo dõi lịch sử thay đổi, vị trí mã nguồn đã chỉnh sửa và kết quả kiểm tra.

## Quy ước đặt tên

Mỗi báo cáo được đặt tên theo mẫu:

```text
YYYY-MM-DD_HHMM_<ten-task-ngan-gon>.md
```

Thời gian trong tên file và nội dung báo cáo sử dụng múi giờ `Asia/Bangkok` (`UTC+07:00`). Nếu có nhiều task trong cùng một phút, thêm hậu tố số thứ tự vào cuối tên file.

## Nội dung bắt buộc

Mỗi báo cáo cần có:

1. Thời gian bắt đầu và hoàn thành.
2. Tiêu đề và yêu cầu của task.
3. Các công việc đã thực hiện.
4. Danh sách file được tạo, sửa hoặc xóa.
5. Vị trí thay đổi trong file, ưu tiên tên mục, tên hàm hoặc số dòng.
6. Các lệnh kiểm tra hoặc kiểm thử đã chạy và kết quả.
7. Những vấn đề còn tồn tại hoặc bước tiếp theo nếu có.

## Danh sách báo cáo

| Thời gian hoàn thành | Task | Báo cáo |
|---|---|---|
| 2026-10-30 14:37 UTC+07:00 | Task 5 — Dataset, transform và DataLoader | [2026-10-30_1437_task5-dataset-dataloader.md](2026-10-30_1437_task5-dataset-dataloader.md) |
| 2026-10-30 14:24 UTC+07:00 | Task 4 — Chia train/validation/test theo nhóm ca | [2026-10-30_1424_task4-chia-du-lieu.md](2026-10-30_1424_task4-chia-du-lieu.md) |
| 2026-10-30 14:12 UTC+07:00 | Task 3 — Phân tích mất cân bằng lớp | [2026-10-30_1412_task3-phan-tich-mat-can-bang.md](2026-10-30_1412_task3-phan-tich-mat-can-bang.md) |
| 2026-10-30 14:03 UTC+07:00 | Task 2 — Xây dựng danh mục ảnh | [2026-10-30_1403_task2-xay-dung-danh-muc-anh.md](2026-10-30_1403_task2-xay-dung-danh-muc-anh.md) |
| 2026-10-30 13:53 UTC+07:00 | Task 1 — Lựa chọn lớp bệnh | [2026-10-30_1353_task1-lua-chon-lop-benh.md](2026-10-30_1353_task1-lua-chon-lop-benh.md) |
| 2026-10-30 13:48 UTC+07:00 | Sửa `loc_scin.py` với ngưỡng 0.5 | [2026-10-30_1348_sua-loc-scin-nguong-05.md](2026-10-30_1348_sua-loc-scin-nguong-05.md) |
| 2026-10-30 13:46 UTC+07:00 | Kiểm tra lỗi `loc_scin.py` | [2026-10-30_1346_kiem-tra-loi-loc-scin.md](2026-10-30_1346_kiem-tra-loi-loc-scin.md) |
| 2026-10-30 13:26 UTC+07:00 | Đọc cấu trúc dữ liệu và quy tắc đặt tên ảnh | [2026-10-30_1326_doc-cau-truc-du-lieu.md](2026-10-30_1326_doc-cau-truc-du-lieu.md) |
| 2026-10-30 13:20 UTC+07:00 | Tạo hệ thống nhật ký công việc | [2026-10-30_1320_tao-he-thong-nhat-ky-cong-viec.md](2026-10-30_1320_tao-he-thong-nhat-ky-cong-viec.md) |

## Cách cập nhật

Khi hoàn thành một task:

1. Sao chép `_template.md` thành một file báo cáo mới.
2. Điền đầy đủ thông tin dựa trên các thay đổi thực tế.
3. Thêm báo cáo mới lên đầu bảng **Danh sách báo cáo**.
4. Không ghi đè hoặc sửa nội dung báo cáo cũ, trừ khi cần sửa thông tin sai và phải nêu rõ lý do.

