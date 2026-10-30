# Task 1 — Lựa chọn lớp bệnh

## Quyết định

Phiên bản đầu tiên của mô hình sử dụng 8 lớp. Tiêu chí định lượng ban đầu là mỗi lớp có ít nhất 50 ca sau khi lọc single-label với `label_weight > 0.5`. Không có nhãn nào được gộp để tăng số mẫu.

| class_id | Nhãn tiếng Anh | Nhãn tiếng Việt | Số ca | Ảnh local tồn tại | Train ước tính | Validation ước tính | Test ước tính |
|---:|---|---|---:|---:|---:|---:|---:|
| 0 | Eczema | Chàm (viêm da dạng chàm) | 319 | 695 | 223 | 48 | 48 |
| 1 | Allergic Contact Dermatitis | Viêm da tiếp xúc dị ứng | 196 | 410 | 137 | 29 | 30 |
| 2 | Urticaria | Mề đay | 165 | 332 | 115 | 25 | 25 |
| 3 | Insect Bite | Vết côn trùng cắn | 120 | 262 | 84 | 18 | 18 |
| 4 | Folliculitis | Viêm nang lông | 85 | 183 | 59 | 13 | 13 |
| 5 | Psoriasis | Vảy nến | 55 | 108 | 38 | 8 | 9 |
| 6 | Tinea | Nhiễm nấm da | 55 | 121 | 38 | 8 | 9 |
| 7 | Herpes Simplex | Herpes simplex (mụn rộp) | 51 | 96 | 36 | 8 | 7 |
| **Tổng** |  |  | **1.046** | **2.207** | **730** | **157** | **159** |

Các số lượng train/validation/test chỉ là ước tính theo tỷ lệ 70/15/15. Task 1 chưa tạo bộ chia chính thức.

## Căn cứ lựa chọn

- Dữ liệu đầu vào có 1.910 ca, 3.945 đường dẫn ảnh và 167 nhãn sau lọc.
- Chỉ 8 lớp có ít nhất 50 ca. Đây là ngưỡng thực hành ban đầu, không phải khẳng định 50 ca là đủ cho mọi lớp.
- Danh sách gồm tám lớp đứng đầu theo số ca; class_id được ghi cố định, không sắp xếp lại động khi huấn luyện.
- Không gộp Eczema với Allergic Contact Dermatitis và không gộp các nhãn nấm/herpes khác.
- Herpes Zoster (45 ca) và Acne (42 ca) chưa được chọn: với test 15%, mỗi lớp chỉ có khoảng 6–7 ca nên recall theo lớp dễ dao động mạnh.
- Class weighting, nếu dùng, chỉ được tính từ tập train sau khi chia và không được xem là giải pháp thay thế dữ liệu thiếu.

## Ý nghĩa số ảnh

`total_images` trong `selected_classes.csv` là số đường dẫn ảnh nguồn duy nhất có ít nhất một file local tồn tại. Giá trị này chưa xác nhận ảnh mở được hoặc có chất lượng phù hợp; trường `image_count_type` được đặt là `local_exists_not_content_validated`.

Một ảnh Tinea được metadata tham chiếu nhưng không tồn tại local:

- Ca: `-1834609919572055750`
- Ảnh: `dataset/images/-2243186711511406658.png`
- File local dự kiến: `data/images_all/-1834609919572055750_1.jpg`

## Trùng đường dẫn ảnh

Có 11 đường dẫn nguồn được nhiều ca single-label tham chiếu, trong đó 2 đường dẫn xuất hiện ở các ca mang nhãn khác nhau. Chín đường dẫn trùng có liên quan đến ít nhất một lớp được chọn.

`duplicate_image_references.csv` lưu đầy đủ đường dẫn, ca, nhãn và file local liên quan. Task 2 phải bảo đảm các ca có chung ảnh nằm cùng một bộ chia hoặc loại ảnh/ca theo quy tắc được ghi nhận. Không được chia ngẫu nhiên độc lập các ca này.

## Đầu ra

- `data/metadata/scin_single_label_05.csv`: dữ liệu cấp ca sau lọc `label_weight > 0.5`.
- `data/metadata/class_statistics.csv`: thống kê toàn bộ 167 lớp.
- `data/metadata/selected_classes.csv`: tám lớp được chọn và thống kê.
- `data/metadata/selected_cases.csv`: 1.046 ca thuộc tám lớp.
- `data/metadata/class_mapping.json`: mapping class_id cố định.
- `data/metadata/duplicate_image_references.csv`: các đường dẫn ảnh bị tham chiếu nhiều lần.

## Việc cần xác nhận ở Task 2

1. Mở và xác thực ảnh, phát hiện ảnh hỏng hoặc không phù hợp.
2. Xử lý ảnh nguồn trùng và các ca liên quan trước khi chia dữ liệu.
3. Xác nhận lại số ảnh sử dụng được cho từng lớp.
4. Chia theo `case_id`, đồng thời giữ các nhóm ca có ảnh trùng trong cùng một tập.
5. Chỉ tính class weight từ tập train sau khi bộ chia đã cố định.

