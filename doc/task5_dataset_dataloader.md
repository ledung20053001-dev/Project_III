# Task 5 — Dataset, transform và DataLoader

## Thiết kế

Task 5 đọc trực tiếp `class_id` từ CSV cố định của Task 4. Không suy ra nhãn từ thư mục, không tạo lại mapping và chưa huấn luyện mô hình.

Mỗi mẫu Dataset trả về:

- `image`: tensor `float32`, kích thước `[3, 224, 224]`;
- `label`: tensor scalar `torch.long`, giá trị 0–7;
- `case_id`: chuỗi dùng để truy vết;
- `image_path`: đường dẫn tương đối từ gốc dự án.

Mỗi batch là dictionary có `image` dạng `[B, 3, 224, 224]` và `label` dạng `[B]`.

## Transform

### Train

1. Chuyển ảnh sang RGB khi Dataset đọc file.
2. Resize giữ tỷ lệ và padding xám trung tính về 224 × 224.
3. Lật ngang ngẫu nhiên với xác suất 0,5.
4. Xoay ngẫu nhiên trong khoảng ±8° với nội suy bilinear.
5. ColorJitter nhẹ: brightness 0,10; contrast 0,10; saturation 0,08; hue 0,02.
6. Chuyển tensor.
7. Normalize theo ImageNet.

Không dùng RandomResizedCrop vì vùng tổn thương có thể nằm sát rìa ảnh. Augmentation chạy trong bộ nhớ khi đọc ảnh và không tạo file mới.

### Validation, test và inference

1. RGB.
2. Resize giữ tỷ lệ và padding về 224 × 224.
3. Chuyển tensor.
4. Normalize ImageNet.

Không có phép biến đổi ngẫu nhiên. Hai lần đọc cùng một ảnh validation/test tạo tensor giống hệt.

## Normalize

- Mean: `[0.485, 0.456, 0.406]`.
- Standard deviation: `[0.229, 0.224, 0.225]`.
- Lý do: phù hợp vòng thử nghiệm transfer learning với backbone pretrained ImageNet.

Nếu một weights cụ thể yêu cầu preprocessing khác, cấu hình mô hình phải ghi rõ và transform inference phải khớp transform đánh giá.

## Cấu hình DataLoader

| Tham số | Giá trị |
|---|---|
| Batch size | 16 |
| Seed | 42 |
| Train shuffle | Có |
| Validation/test shuffle | Không |
| num_workers | 0 |
| pin_memory | Tự động; hiện false vì không có CUDA |
| drop_last | false cho cả ba tập |

Class weights không được đưa vào DataLoader; chúng sẽ được truyền cho loss ở bước huấn luyện weighted.

## Kết quả kiểm tra toàn bộ

| Split | Ảnh | Batch | Batch cuối | Lớp xuất hiện |
|---|---:|---:|---:|---|
| Train | 1.551 | 97 | 15 | 0–7 |
| Validation | 333 | 21 | 13 | 0–7 |
| Test | 330 | 21 | 10 | 0–7 |

Các kiểm tra đều đạt:

- Toàn bộ 2.214 ảnh đọc được qua DataLoader.
- Shape mỗi ảnh đúng `[3, 224, 224]`.
- Tensor ảnh là `torch.float32`.
- Tensor nhãn là `torch.int64` (`torch.long`).
- Không có NaN hoặc vô hạn.
- Nhãn nằm trong 0–7 và khớp mapping.
- Validation/test không bỏ batch cuối.
- Train quan sát được augmentation ngẫu nhiên.
- Validation/test xác định giữa các lần đọc.

## Kiểm tra trực quan

Preview gồm một ảnh đã transform của mỗi lớp được lưu tại `results/data_analysis/task5_train_transform_preview.png`. Tensor đã được đảo normalization trước khi hiển thị.

Quan sát preview cho thấy:

- Tổn thương vẫn nằm trong ảnh sau transform.
- Ảnh không bị kéo méo vì resize giữ tỷ lệ.
- Xoay nhẹ không loại vùng tổn thương.
- ColorJitter không làm thay đổi màu quá mạnh.
- Padding xám có thể xuất hiện ở cạnh/góc nhưng không lấn át nội dung.

## Môi trường kiểm tra

- PyTorch `2.15.0+cpu`.
- torchvision `0.29.2+cpu`.
- CUDA không khả dụng trong môi trường hiện tại.

## Đầu ra

- `src/dataset.py`.
- `src/transforms.py`.
- `src/utils.py`.
- `configs/data.yaml`.
- `scripts/task5_validate_dataloaders.py`.
- `requirements.txt`.
- `results/data_analysis/task5_dataloader_validation.json`.
- `results/data_analysis/task5_train_transform_preview.png`.

