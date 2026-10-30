# Task 2 — Xây dựng danh mục ảnh

## Kết quả

Task 2 chuyển dữ liệu từ một dòng cho mỗi ca thành một dòng cho mỗi ảnh hợp lệ. Không sao chép ảnh, không tạo ảnh mới và chưa chia train/validation/test.

| Chỉ số | Kết quả |
|---|---:|
| Ca đầu vào | 1.046 |
| Ảnh metadata tham chiếu theo từng ca | 2.215 |
| Ảnh hợp lệ | 2.214 |
| Ảnh bị loại | 1 |
| Ca không còn ảnh hợp lệ | 0 |
| Đường dẫn ảnh trong manifest bị trùng | 0 |
| Nhóm ảnh trùng nội dung | 7 |
| Nhóm trùng nội dung khác nhãn | 0 |

## Kiểm tra ảnh

Mỗi ảnh trong `dataset_images.csv` đã vượt qua các bước:

1. File tồn tại tại đường dẫn local.
2. PIL nhận diện được định dạng.
3. `verify()` không phát hiện cấu trúc file hỏng.
4. Mở lại ảnh và gọi `load()` để giải mã toàn bộ pixel.
5. Chiều rộng và chiều cao lớn hơn 0.
6. Chuyển sang RGB và tải dữ liệu RGB thành công.
7. Tính SHA-256 trên kích thước và dữ liệu pixel RGB để phát hiện nội dung trùng.

Tất cả 2.214 ảnh hợp lệ được PIL nhận diện là JPEG. Kích thước nhỏ nhất là 139 × 199 pixel theo từng chiều tối thiểu quan sát được; kích thước lớn nhất là 1080 × 1080 pixel theo từng chiều tối đa. Task 2 không áp dụng ngưỡng loại ảnh nhỏ và không resize ảnh.

## Ảnh bị loại

Một ảnh không tồn tại:

- `case_id`: `-1834609919572055750`
- Nhãn: Tinea, class_id 6.
- Nguồn: `dataset/images/-2243186711511406658.png`.
- Local dự kiến: `data/images_all/-1834609919572055750_1.jpg`.
- Lý do: `file_not_found`.

Ca này vẫn còn hai ảnh hợp lệ nên tiếp tục xuất hiện trong manifest.

## Phân bố sau kiểm tra

| class_id | Nhãn | Ca hợp lệ | Ảnh hợp lệ | Ảnh bị loại |
|---:|---|---:|---:|---:|
| 0 | Eczema | 319 | 695 | 0 |
| 1 | Allergic Contact Dermatitis | 196 | 412 | 0 |
| 2 | Urticaria | 165 | 332 | 0 |
| 3 | Insect Bite | 120 | 262 | 0 |
| 4 | Folliculitis | 85 | 185 | 0 |
| 5 | Psoriasis | 55 | 108 | 0 |
| 6 | Tinea | 55 | 121 | 1 |
| 7 | Herpes Simplex | 51 | 99 | 0 |

Số ảnh ở đây đếm từng file local hợp lệ gắn với từng ca. Con số 2.214 lớn hơn 2.207 của Task 1 vì Task 1 đếm đường dẫn nguồn duy nhất theo lớp, còn Task 2 giữ từng file local/case và đánh dấu nội dung trùng để xử lý khi chia dữ liệu.

## Ảnh trùng nội dung

Có 7 nhóm ảnh trùng pixel giữa các ca:

- 2 nhóm thuộc Allergic Contact Dermatitis.
- 2 nhóm thuộc Folliculitis.
- 3 nhóm thuộc Herpes Simplex.

Không có nhóm nào chứa nhiều nhãn trong phạm vi 8 lớp được chọn. Task chia dữ liệu phải coi các ca trong cùng nhóm trùng là một nhóm ràng buộc và đưa chúng vào cùng train, validation hoặc test.

## Đầu ra

- `data/metadata/dataset_images.csv`: manifest chính, một dòng cho mỗi ảnh hợp lệ.
- `data/metadata/rejected_images.csv`: ảnh bị loại và lý do.
- `data/metadata/cases_without_valid_images.csv`: ca không còn ảnh hợp lệ.
- `data/metadata/dataset_image_statistics.csv`: số ca và ảnh theo lớp sau kiểm tra.
- `data/metadata/duplicate_content_images.csv`: nhóm ảnh có nội dung pixel giống nhau.
- `scripts/task2_build_image_manifest.py`: script tạo lại toàn bộ đầu ra Task 2.

## Lưu ý cho bước chia dữ liệu

- Chia theo `case_id`, không chia theo từng dòng ảnh.
- Gộp các `case_id` có chung `content_sha256` thành cùng một nhóm trước khi chia.
- Không tạo lại class_id; luôn đọc `class_mapping.json`.
- `label_weight` chỉ được lưu để truy vết, chưa được dùng tự động trong loss.

