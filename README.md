# Phân loại bệnh ngoài da từ hình ảnh sử dụng Deep Learning

## 1. Giới thiệu

Dự án nghiên cứu và xây dựng hệ thống **phân loại một số tình trạng da từ hình ảnh** bằng các thuật toán Deep Learning. Nguồn dữ liệu chính là **SCIN (Skin Condition Image Network)** do Google Research công bố. Hệ thống hướng tới khả năng **huấn luyện và dự đoán trên máy local**, đồng thời **hiển thị tên tình trạng da bằng tiếng Việt** để người dùng Việt Nam dễ tiếp cận.

Trọng tâm dự án là quy trình xử lý dữ liệu, lựa chọn và huấn luyện mô hình phân loại, đánh giá chất lượng dự đoán và so sánh các phương pháp. Giao diện sử dụng (nếu triển khai) đóng vai trò minh họa kết quả của mô hình.


## 2. Mục tiêu

- Xây dựng bộ dữ liệu ảnh da đã chọn lọc từ SCIN, tập trung vào các nhóm bệnh/tình trạng da có nhãn và số mẫu phù hợp.
- Xây dựng và thử nghiệm mô hình phân loại ảnh sử dụng Deep Learning.
- Đánh giá mô hình bằng các chỉ số phù hợp, đặc biệt chú ý đến mất cân bằng giữa các lớp.
- Hướng tới dự đoán **Top 3** tình trạng da có điểm mô hình cao nhất, hiển thị bằng tiếng Việt trên máy local.

## 3. Phạm vi và dữ liệu

### Nguồn dữ liệu SCIN

SCIN là bộ dữ liệu về tình trạng da gồm ảnh và thông tin nhãn liên quan. Một ca có thể có nhiều ảnh và nhiều nhận định nhãn. Vì vậy, dự án cần xây dựng **quy tắc chọn nhãn** trước khi huấn luyện, thay vì mặc định tất cả ca đều có một nhãn duy nhất.

- Trang giới thiệu: https://research.google/blog/scin-a-new-resource-for-representative-dermatology-images/
- Kho dữ liệu và tài liệu: https://github.com/google-research-datasets/scin


### Phạm vi bài toán

Phiên bản đầu tiên dự kiến thực hiện **phân loại một nhãn (single-label classification)** trên các ca có nhãn chính đủ rõ ràng. Đầu ra là điểm dự đoán trên các lớp đã huấn luyện và danh sách Top 3. Trường hợp dữ liệu được giữ nguyên nhiều nhãn cho một ca, cần chuyển sang thiết kế **multi-label classification** và thay đổi hàm mất mát/cách đánh giá cho phù hợp.

Mô hình chỉ nhận biết những lớp thuộc phạm vi huấn luyện; ảnh không thuộc các lớp này có thể vẫn bị gán vào một lớp đã biết. Cơ chế cảnh báo hoặc từ chối dự đoán ngoài phạm vi là hướng phát triển tiếp theo.

## 4. Quy trình xử lý

```text
Ảnh và metadata SCIN
        |
        v
Kiểm tra dữ liệu, lọc ảnh và nhãn
        |
        v
Chọn nhóm bệnh / chuẩn hóa nhãn tiếng Việt
        |
        v
Chia train / validation / test theo case_id
        |
        v
Tiền xử lý và tăng cường dữ liệu train
        |
        v
Huấn luyện, tinh chỉnh mô hình
        |
        v
Đánh giá trên tập test độc lập
        |
        v
Dự đoán ảnh mới → Top 3 → Hiển thị tiếng Việt
```

**Nguyên tắc quan trọng:** Các ảnh thuộc cùng một `case_id` phải nằm trong cùng một tập dữ liệu nhằm giảm nguy cơ rò rỉ dữ liệu giữa tập huấn luyện và tập kiểm thử. Cũng cần rà soát ảnh trùng lặp giữa các ca.

## 5. Cấu trúc thư mục đề xuất


```text
skin-disease-classification/
├── data/
│   ├── metadata/          # Metadata, thống kê nhãn, danh sách ảnh
│   └── images/            # Ảnh SCIN đã tải về
├── notebooks/             # Khám phá và trực quan hóa dữ liệu
├── src/
│   ├── dataset.py         # Đọc dữ liệu, tạo DataLoader
│   ├── preprocessing.py   # Tiền xử lý và augmentation
│   ├── model.py           # Định nghĩa/khởi tạo mô hình
│   ├── train.py           # Huấn luyện mô hình
│   ├── evaluate.py        # Đánh giá mô hình
│   └── predict.py         # Dự đoán ảnh mới
├── models/                # Checkpoint mô hình
├── results/               # Chỉ số, biểu đồ, confusion matrix
├── labels_vi.json         # Ánh xạ nhãn tiếng Anh → tiếng Việt
├── app.py                 # Giao diện local (nếu triển khai)
├── requirements.txt       # Phụ thuộc Python
└── README.md
```

**Khuyến nghị:** Không đưa toàn bộ ảnh, dữ liệu nhạy cảm hoặc checkpoint dung lượng lớn lên Git nếu chưa kiểm tra điều kiện sử dụng và quyền chia sẻ.

## 6. Chạy dự án trên máy local

Các bước sau là **hướng dẫn chuẩn bị môi trường**. Lệnh huấn luyện và chạy giao diện chỉ sử dụng được sau khi những file tương ứng đã được triển khai.

**1. Tạo môi trường ảo (Windows):**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**2. Cài đặt thư viện:**

Khi đã có `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Với PyTorch, lựa chọn bản cài đặt phù hợp CPU hoặc GPU tại https://pytorch.org/get-started/locally/.

**3. Chuẩn bị dữ liệu:**

Đặt ảnh và metadata SCIN vào đường dẫn mà chương trình đọc dữ liệu được cấu hình sử dụng; xác nhận danh sách các lớp, ánh xạ tiếng Việt và chia dữ liệu theo mã ca bệnh trước khi huấn luyện.

**4. Huấn luyện và dự đoán (sau khi triển khai):**

Dự kiến cung cấp lệnh CLI để huấn luyện, đánh giá và chạy giao diện. Cú pháp chính xác sẽ được cập nhật khi các script hoàn thành.

## 7. Quản lý nhãn tiếng Việt

Tên bệnh bằng tiếng Việt được quản lý tập trung, không thay đổi tùy tiện theo từng màn hình. Ví dụ cấu trúc file `labels_vi.json`:

```json
{
  "Eczema": "Chàm (viêm da dạng chàm)",
  "Acne": "Mụn trứng cá",
  "Psoriasis": "Vảy nến"
}
```

**Đây chỉ là ví dụ ánh xạ**, không xác nhận các lớp trên đã được chọn hoặc đủ mẫu trong dữ liệu hiện có. Khi triển khai, cần dùng **đúng tên nhãn gốc trong metadata**, rà soát thuật ngữ y khoa và lưu thứ tự `class_id` nhất quán với checkpoint mô hình.

## 8. Tiến độ thực hiện

- [x] Xác định chủ đề, nguồn dữ liệu SCIN và định hướng phân loại ảnh.
- [x] Tải dữ liệu ảnh về máy local.
- [ ] Kiểm tra ảnh, thống kê số ca và phân bố các nhãn đã chọn.
- [ ] Chuẩn hóa từ điển nhãn tiếng Việt và chốt danh sách lớp.
- [ ] Tạo tập train/validation/test theo `case_id`.
- [ ] Xây dựng mô hình baseline.
- [ ] Thử nghiệm transfer learning và tối ưu siêu tham số.
- [ ] Đánh giá trên tập test độc lập.
- [ ] Tích hợp chức năng dự đoán Top 3 vào giao diện local.

## 9. Hạn chế và lưu ý

- Phân bố nhãn và chất lượng ảnh trong SCIN có thể không đồng đều.
- Một ca có thể mang nhiều nhãn hoặc nhãn chưa chắc chắn; cách xây dựng nhãn mục tiêu ảnh hưởng trực tiếp đến kết quả.
- Kết quả trên SCIN không bảo đảm hiệu quả tương đương trên ảnh chụp trong điều kiện khác hoặc trên người dùng Việt Nam.
- Một số bệnh có biểu hiện trực quan tương tự nhau; chỉ dựa vào ảnh có thể không đủ để phân biệt chính xác.
- Dữ liệu và kết quả cần được sử dụng tuân thủ điều khoản của nguồn SCIN.

## 10. Tài liệu tham khảo

1. [Google Research – SCIN: A new resource for representative dermatology images](https://research.google/blog/scin-a-new-resource-for-representative-dermatology-images/).
2. [Google Research Datasets – SCIN (GitHub)](https://github.com/google-research-datasets/scin).
3. [PyTorch Documentation](https://docs.pytorch.org/).
4. [Torchvision Models](https://docs.pytorch.org/vision/stable/models.html).

---

*README được xây dựng theo định hướng dự án và sẽ được cập nhật theo cấu trúc mã nguồn, danh sách nhãn và kết quả thực nghiệm thực tế.*
