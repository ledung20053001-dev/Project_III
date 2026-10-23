# Mô tả bộ dữ liệu SCIN

Phần dưới đây mô tả các trường trong những tệp CSV khác nhau.

## `scin_cases.csv`

* **case_id** (`string`, luôn có): Mã định danh của ca bệnh.
  * Mã này thường được giữ ổn định giữa các phiên bản phát hành.

* **source** (`string`, luôn có): Giá trị là `"SCIN"`.

* **release** (`string`, luôn có): Mã phiên bản phát hành chứa ca bệnh này.
  * Chuỗi phiên bản có định dạng `major.minor.patch`:
    * Major: Bổ sung một số lượng lớn ca bệnh mới.
    * Minor: Bổ sung một số ít danh mục hoặc nhãn mới cho các ảnh hiện có.
    * Patch: Sửa lỗi.
  * Phiên bản đầu tiên là `"1.0.0"`.

* **year** (`int`, luôn có): Năm gần nhất với thời điểm phần lớn dữ liệu được phát hành.

* **age_group** (`enum`, đôi khi có): Tuổi do người dùng cung cấp ban đầu là một số nguyên.
  * Giá trị này được ánh xạ vào các nhóm tuổi sau:
    * `AGE_18_TO_29`: Từ 18 đến 29 tuổi.
    * `AGE_30_TO_39`: Từ 30 đến 39 tuổi.
    * `AGE_40_TO_49`: Từ 40 đến 49 tuổi.
    * `AGE_50_TO_59`: Từ 50 đến 59 tuổi.
    * `AGE_60_TO_69`: Từ 60 đến 69 tuổi.
    * `AGE_70_TO_79`: Từ 70 đến 79 tuổi.
    * `AGE_80_OR_ABOVE`: Từ 80 tuổi trở lên.

* **sex_at_birth** (`enum`, đôi khi có): Giới tính khi sinh do người dùng tự khai báo.
  * Các giá trị trong bộ dữ liệu:
    * `FEMALE`: Nữ.
    * `MALE`: Nam.
    * `OTHER_OR_UNSPECIFIED`: Khác hoặc không xác định.
  * Giao diện SCIN cũng có các lựa chọn `OTHER` và `PREFER_NOT_TO_SAY`. Do không có đủ câu trả lời trong hai nhóm này để công bố riêng, các ca đó được gộp vào nhóm `OTHER_OR_UNSPECIFIED`.

* **fitzpatrick_skin_type** (`enum`, đôi khi có): Loại da do người dùng tự khai báo.
  * Các giá trị có thể có: `FST1`–`FST6`, `NONE_SELECTED`.
  * Trong ứng dụng, người dùng được hỏi da phản ứng như thế nào khi tiếp xúc với ánh nắng. Các câu trả lời sau được ánh xạ sang giá trị FST:
    * `NEVER_TANS`: Không bao giờ rám nắng.
    * `TANS_MINIMALLY`: Rám nắng rất ít.
    * `TANS_UNIFORMLY`: Rám nắng đồng đều.
    * `ALWAYS_TANS_WELL`: Luôn rám nắng tốt.
    * `TANS_EASILY`: Dễ rám nắng.
    * `ALWAYS_TANS`: Luôn rám nắng.
    * `NONE_OF_THE_ABOVE`: Không thuộc các trường hợp trên.
  * `NONE_SELECTED` có nghĩa là người dùng nhận thấy không lựa chọn nào có sẵn phù hợp với loại da của họ. Điều này có thể cho thấy người dùng khó tự đánh giá loại da Fitzpatrick khi chỉ được cung cấp lượng thông tin hạn chế. Xem `scin_questions.csv` để biết toàn bộ nội dung câu hỏi.

* **race_ethnicity_\*** (`bool`, đôi khi có): Chủng tộc và/hoặc dân tộc do người dùng tự khai báo.
  * Các hậu tố của tên cột:
    * `AMERICAN_INDIAN_OR_ALASKA_NATIVE`: Người Mỹ bản địa hoặc người bản địa Alaska.
    * `ASIAN`: Người châu Á.
    * `BLACK_OR_AFRICAN_AMERICAN`: Người da đen hoặc người Mỹ gốc Phi.
    * `HISPANIC_LATINO_OR_SPANISH_ORIGIN`: Người Hispanic, Latino hoặc có nguồn gốc Tây Ban Nha.
    * `MIDDLE_EASTERN_OR_NORTH_AFRICAN`: Người Trung Đông hoặc Bắc Phi.
    * `NATIVE_HAWAIIAN_OR_PACIFIC_ISLANDER`: Người Hawaii bản địa hoặc người dân đảo Thái Bình Dương.
    * `WHITE`: Người da trắng.
    * `OTHER_RACE`: Chủng tộc khác.
    * `PREFER_NOT_TO_ANSWER`: Không muốn trả lời.
    * `TWO_OR_MORE_AFTER_MITIGATION`: Trong quá trình xử lý dữ liệu, một số tổ hợp chủng tộc/dân tộc có ít mẫu đóng góp được gộp vào nhóm này.
  * Người dùng có thể chọn nhiều hơn một nhóm trong danh sách trên.

* **textures_\*** (`bool`, đôi khi có): Đặc điểm bề mặt của tình trạng da do người dùng tự khai báo.
  * Các hậu tố của tên cột:
    * `TEXTURE_UNSPECIFIED`: Không xác định đặc điểm bề mặt.
    * `RAISED_OR_BUMPY`: Nổi hoặc có u/cục.
    * `FLAT`: Phẳng.
    * `ROUGH_OR_FLAKY`: Thô ráp hoặc bong vảy.
    * `FLUID_FILLED`: Chứa dịch.

* **body_parts_\*** (`bool`, đôi khi có): Bộ phận cơ thể bị ảnh hưởng bởi tình trạng da, do người dùng tự khai báo.
  * Các hậu tố của tên cột:
    * `HEAD_OR_NECK`: Đầu hoặc cổ.
    * `ARM`: Cánh tay.
    * `PALM`: Lòng bàn tay.
    * `BACK_OF_HAND`: Mu bàn tay.
    * `TORSO_FRONT`: Phía trước thân mình.
    * `TORSO_BACK`: Phía sau thân mình.
    * `GENITALIA_OR_GROIN`: Cơ quan sinh dục hoặc vùng bẹn.
    * `BUTTOCKS`: Mông.
    * `LEG`: Chân.
    * `FOOT_TOP_OR_SIDE`: Mu hoặc cạnh bàn chân.
    * `FOOT_SOLE`: Lòng bàn chân.
    * `OTHER`: Vị trí khác.

* **condition_symptoms_\*** (`bool`, đôi khi có): Triệu chứng về biểu hiện và cảm giác của tình trạng da do người dùng tự khai báo.
  * Các hậu tố của tên cột:
    * `BOTHERSOME_APPEARANCE`: Ngoại quan gây khó chịu.
    * `BLEEDING`: Chảy máu.
    * `INCREASING_SIZE`: Tăng kích thước.
    * `DARKENING`: Sẫm màu hơn.
    * `ITCHING`: Ngứa.
    * `BURNING`: Cảm giác bỏng rát.
    * `PAIN`: Đau.
    * `NO_RELEVANT_EXPERIENCE`: Không có biểu hiện liên quan.

* **other_symptoms_\*** (`bool`, đôi khi có): Các triệu chứng khác có thể liên quan đến tình trạng da, do người dùng tự khai báo.
  * Các hậu tố của tên cột:
    * `FEVER`: Sốt.
    * `CHILLS`: Ớn lạnh.
    * `FATIGUE`: Mệt mỏi.
    * `JOINT_PAIN`: Đau khớp.
    * `MOUTH_SORES`: Loét miệng.
    * `SHORTNESS_OF_BREATH`: Khó thở.
    * `NO_RELEVANT_SYMPTOMS`: Không có triệu chứng liên quan.

* **related_category** (`enum`, đôi khi có): Nhóm vấn đề có thể liên quan, do người dùng tự khai báo.
  * Các giá trị có thể có:
    * `ACNE`: Mụn trứng cá.
    * `GROWTH_OR_MOLE`: Khối phát triển hoặc nốt ruồi.
    * `HAIR_LOSS`: Rụng tóc.
    * `OTHER_HAIR_PROBLEM`: Vấn đề khác về tóc.
    * `NAIL_PROBLEM`: Vấn đề về móng.
    * `PIGMENTARY_PROBLEM`: Vấn đề sắc tố.
    * `RASH`: Phát ban.
    * `LOOKS_HEALTHY`: Trông khỏe mạnh/bình thường.
    * `OTHER_ISSUE_DESCRIPTION`: Mô tả vấn đề khác.

* **condition_duration** (`enum`, đôi khi có): Thời gian tồn tại của tình trạng da, do người dùng tự khai báo.
  * Các giá trị dựa trên câu hỏi hiện tại trong giao diện:
    * `ONE_DAY`: Một ngày.
    * `LESS_THAN_ONE_WEEK`: Dưới một tuần.
    * `ONE_TO_FOUR_WEEKS`: Từ một đến bốn tuần.
    * `ONE_TO_THREE_MONTHS`: Từ một đến ba tháng.
    * `THREE_TO_TWELVE_MONTHS`: Từ ba đến mười hai tháng.
    * `MORE_THAN_ONE_YEAR`: Hơn một năm.
    * `MORE_THAN_FIVE_YEARS`: Hơn năm năm.
    * `SINCE_CHILDHOOD`: Từ thời thơ ấu.
    * `UNKNOWN`: Không rõ.

* **image_\d_path** (`string`, đôi khi có): Đường dẫn đến vị trí lưu ảnh. Mỗi ca có tối đa ba ảnh.

* **image_\d_shot_type** (`enum`, đôi khi có): Giá trị enum cho biết ảnh được người dùng gửi ở câu hỏi chụp ảnh nào.
  * Các giá trị có thể có:
    * `CLOSE_UP`: Ảnh cận cảnh.
    * `AT_AN_ANGLE`: Ảnh chụp từ một góc nghiêng.
    * `AT_DISTANCE`: Ảnh chụp từ xa.

## `scin_labels.csv`

### Ví dụ về quá trình gán nhãn

Trong quá trình gán nhãn tình trạng da, mỗi người gán nhãn cung cấp tối đa ba chẩn đoán, với mức độ tin cậy từ 1 đến 5 cho từng chẩn đoán. Một ca có thể được tối đa ba người gán nhãn. Danh sách cuối cùng gồm tên tình trạng và mức độ tin cậy được tổng hợp thành một danh sách các tình trạng. Mỗi tình trạng có thứ hạng và trọng số; các giá trị này được kết hợp trong cột `weighted_skin_condition_label`.

**Ví dụ giả định:**

Nhãn của các bác sĩ da liễu:

* Nhãn của bác sĩ da liễu 1: Chàm đồng tiền (`Nummular eczema`) với độ tin cậy 3, viêm da cấp và mạn tính (`Acute and chronic dermatitis`) với độ tin cậy 2, vảy nến thể thông thường (`Psoriasis vulgaris`) với độ tin cậy 1.
* Nhãn của bác sĩ da liễu 2: Viêm da dạng chàm (`Eczematous dermatitis`) với độ tin cậy 3.
* Nhãn của bác sĩ da liễu 3: Viêm da dạng chàm với độ tin cậy 4, tăng sắc tố sau viêm (`Post-inflammatory hyperpigmentation`) với độ tin cậy 3.

Các cột nhãn sẽ có dạng:

* `dermatologist_skin_condition_label_name`: `Nummular eczema, Acute and chronic dermatitis, Psoriasis vulgaris, Eczematous dermatitis, Eczematous dermatitis, Post-inflammatory hyperpigmentation`
* `dermatologist_skin_condition_confidence`: `[3, 2, 1, 3, 4, 3]`
* `weighted_skin_condition_label`: `{'Eczema': 0.69, 'Acute and chronic dermatitis': 0.11, 'Post-Inflammatory hyperpigmentation': 0.11, 'Psoriasis': 0.08}`

Lưu ý rằng tên tình trạng đã thay đổi. Cụ thể, cả `Nummular eczema` và `Eczematous dermatitis` đều được ánh xạ thành `Eczema`. Xem phần mô tả `weighted_skin_condition_label` dưới đây để biết thêm chi tiết.

### Cấu trúc CSV

* **case_id**: Cùng mã định danh với trường `case_id` trong `scin_cases.csv`.

* **dermatologist_gradable_for_skin_condition_\d** (`bool`, đôi khi có): Nhãn của bác sĩ da liễu cho biết có thể xác định tình trạng da từ các ảnh của ca bệnh hay không.
  * Chữ số cuối nằm trong khoảng `[1, 3]` (bao gồm cả 1 và 3), tương ứng với một trong ba bác sĩ da liễu.
  * Trường này có thể là `false` vì nhiều lý do, bao gồm: không có bệnh lý có thể nhận biết (ví dụ da bình thường), không đủ thông tin, có nhiều tình trạng xuất hiện cùng lúc hoặc chất lượng ảnh có vấn đề.

* **dermatologist_skin_condition_label_name** (`List[string]`, đôi khi có): Danh sách tên tình trạng được tổng hợp từ các nhãn do bác sĩ da liễu cung cấp về những tình trạng có thể xuất hiện trong ca bệnh.
  * Những tên tình trạng này là giá trị gốc được dùng trong quá trình gán nhãn.
  * Danh sách có thể có phần tử trùng lặp. Một phần tử trùng lặp có nghĩa là nhiều hơn một bác sĩ đã đưa tình trạng đó vào câu trả lời.
  * Ví dụ: `[Nummular eczema, Psoriasis vulgaris, ...]`.

* **dermatologist_skin_condition_confidence** (`List[int]`, đôi khi có): Danh sách điểm tin cậy. Mỗi điểm nằm trong khoảng `[1, 5]` (bao gồm cả 1 và 5); 1 là mức tin cậy thấp nhất và 5 là cao nhất.
  * Mỗi phần tử trong danh sách này là độ tin cậy của phần tử tương ứng trong cột `dermatologist_skin_condition_label_name`.
  * Ví dụ: `[1, 3, ...]`.
    * Khi kết hợp với cột `dermatologist_skin_condition_label_name`, ví dụ này có nghĩa là bác sĩ gán nhãn `Nummular eczema` với độ tin cậy 1 và `Psoriasis vulgaris` với độ tin cậy 3.

* **weighted_skin_condition_label** (`Dict[string, float]`, đôi khi có): Cột này biểu diễn nhãn chẩn đoán phân biệt cuối cùng, được tạo như sau:
  * Với danh sách nhãn của từng bác sĩ gồm tên tình trạng và mức độ tin cậy, nhãn được gán lại trọng số theo nghịch đảo thứ hạng trong danh sách của người đó. Ví dụ, danh sách `'Condition A': 4, 'Condition B': 3, 'Condition C': 1` sẽ được gán lại thành `'Condition A': 1, 'Condition B': 0.5, 'Condition C': 0.3`.
  * Sau đó, trọng số của cùng một tình trạng từ tất cả bác sĩ được cộng lại.
  * Cuối cùng, kết quả được chuẩn hóa sao cho tổng các trọng số bằng 1.

* **dermatologist_gradable_for_fitzpatrick_skin_type_\d** (`string`, đôi khi có): Nhãn của bác sĩ da liễu cho biết có thể ước tính loại da Fitzpatrick từ ca bệnh hay không.
  * Các giá trị: `"YES"`, `"NO"`.
  * Mỗi ca có thể có tối đa ba nhãn như vậy.

* **dermatologist_fitzpatrick_skin_type_label_\d** (`enum`, đôi khi có): Nhãn ước tính loại da Fitzpatrick do bác sĩ da liễu cung cấp.
  * Mỗi ca có thể có tối đa ba nhãn như vậy. (da sáng màu/ trung bình / nâu / tối màu )

* **gradable_for_monk_skin_tone_india** (`bool`, đôi khi có): Nhãn từ một người không chuyên đã qua đào tạo, thuộc nhóm đánh giá tại Ấn Độ, cho biết có thể xác định nhãn tông màu da Monk từ ảnh của ca bệnh hay không.

* **gradable_for_monk_skin_tone_us** (`bool`, đôi khi có): Nhãn từ một người không chuyên đã qua đào tạo, thuộc nhóm đánh giá tại Hoa Kỳ, cho biết có thể xác định nhãn tông màu da Monk từ ảnh của ca bệnh hay không.

* **monk_skin_tone_label_india** (`enum`, đôi khi có): Giá trị tông màu da Monk do một người không chuyên đã qua đào tạo thuộc nhóm đánh giá tại Ấn Độ cung cấp.
  * Các giá trị có thể có: từ 1 đến 10.

* **monk_skin_tone_label_us** (`enum`, đôi khi có): Giá trị tông màu da Monk do một người không chuyên đã qua đào tạo thuộc nhóm đánh giá tại Hoa Kỳ cung cấp.
  * Các giá trị có thể có: từ 1 đến 10.
