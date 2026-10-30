# Báo cáo task: Task 5 — Dataset, transform và DataLoader

## Thông tin

- Thời gian bắt đầu: `2026-10-30 14:27 UTC+07:00`
- Thời gian hoàn thành: `2026-10-30 14:37:50 UTC+07:00`
- Trạng thái: `Hoàn thành`

## Yêu cầu

Biến ba CSV split thành PyTorch Dataset/DataLoader, thiết kế transform train và evaluation, kiểm tra toàn bộ ảnh, shape, dtype, nhãn, tính hữu hạn, batch cuối, tính ngẫu nhiên/xác định và xem preview đủ tám lớp. Chưa huấn luyện mô hình.

## Công việc đã thực hiện

1. Tạo package `src` và Dataset đọc class_id trực tiếp từ CSV.
2. Kiểm tra nhãn Anh/Việt với class mapping khi khởi tạo Dataset.
3. Thiết kế resize giữ tỷ lệ và padding để tránh crop mất tổn thương.
4. Tạo augmentation train nhẹ và transform validation/test cố định.
5. Lưu normalization ImageNet, batch size, seed và tham số DataLoader trong YAML.
6. Tạo DataLoader có shuffle chỉ cho train, không drop batch cuối.
7. Cài PyTorch, torchvision và PyYAML để kiểm thử thực tế.
8. Chạy toàn bộ train/validation/test DataLoader trên CPU.
9. Kiểm tra shape, dtype, NaN/Inf, khoảng nhãn và đủ lớp.
10. Kiểm tra train có augmentation, validation/test xác định.
11. Tạo và xem preview sau khi đảo normalization, sửa nhãn chồng lấn.
12. Thêm requirements và cập nhật README/tài liệu.

## File và vị trí thay đổi

| Thao tác | File | Vị trí | Nội dung |
|---|---|---|---|
| Tạo | `src/dataset.py` | Toàn bộ file | Dataset và factory DataLoader. |
| Tạo | `src/transforms.py` | Toàn bộ file | ResizeWithPadding, transform và denormalize. |
| Tạo | `src/utils.py` | Toàn bộ file | Seed, worker seed và pin_memory. |
| Tạo | `src/__init__.py` | Toàn bộ file | Khai báo package. |
| Tạo | `configs/data.yaml` | Toàn bộ file | Cấu hình transform/DataLoader. |
| Tạo | `scripts/task5_validate_dataloaders.py` | Toàn bộ file | Kiểm thử toàn bộ và tạo preview. |
| Tạo | `requirements.txt` | Toàn bộ file | Phụ thuộc dự án. |
| Tạo | `results/data_analysis/task5_dataloader_validation.json` | Toàn bộ file | Kết quả kiểm thử có cấu trúc. |
| Tạo | `results/data_analysis/task5_train_transform_preview.png` | Toàn bộ file | Preview đủ tám lớp. |
| Tạo | `doc/task5_dataset_dataloader.md` | Toàn bộ file | Tài liệu thiết kế và kết quả. |
| Sửa | `README.md` | Mục `Tiến độ thực hiện` | Đánh dấu hoàn thành Task 5. |
| Sửa | `doc/README.md` | Mục `Danh sách báo cáo` | Thêm báo cáo Task 5. |

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Train | 1.551 ảnh, 97 batch, batch cuối 15. |
| Validation | 333 ảnh, 21 batch, batch cuối 13. |
| Test | 330 ảnh, 21 batch, batch cuối 10. |
| Shape | `[B, 3, 224, 224]`. |
| Dtype ảnh | `torch.float32`. |
| Dtype nhãn | `torch.int64`. |
| Nhãn | 0–7, đủ tám lớp trong từng split. |
| NaN/Inf | Không có. |
| Validation/test xác định | Đạt. |
| Train augmentation | Quan sát được. |
| Cú pháp bốn file Python | Đạt: `SYNTAX_OK`. |
| Preview | Đã xem; tổn thương được giữ, màu và hình dạng hợp lý. |

## Kết quả

Dataset/DataLoader đã sẵn sàng cho CNN baseline và transfer learning. Môi trường kiểm tra dùng PyTorch 2.15.0 CPU, batch size 16 và num_workers 0.

## Lưu ý và bước tiếp theo

- Máy hiện không có CUDA nên huấn luyện sẽ chạy CPU nếu không chuyển sang môi trường GPU.
- Có thể tăng num_workers sau khi đo hiệu năng trên môi trường huấn luyện thực tế.
- Transform inference phải dùng đúng transform evaluation trong `src/transforms.py`.
- Class weights thuộc loss, không thuộc DataLoader.

