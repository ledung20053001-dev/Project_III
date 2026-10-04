
import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/metadata")

df = pd.read_csv(
    DATA_DIR / "eligible_cases.csv",
    dtype={"case_id": str}
)

with open("labels_vi.json", encoding="utf-8") as f:
    translations = json.load(f)

# Danh sách ứng viên lấy từ labels_vi.json
selected = list(translations.keys())

# Chỉ chọn nhãn trùng khớp chính xác
selected_df = df[
    df["primary_label"].isin(selected)
].copy()

# Kiểm tra nhãn nào thực sự xuất hiện
available = set(selected_df["primary_label"])

missing = set(selected) - available

print("Selected diseases:")
print(
    selected_df["primary_label"]
    .value_counts()
)

print("\nLabels not found or ineligible:")
print(sorted(missing))

if selected_df.empty:
    raise ValueError(
        "No matching cases. "
        "Check exact label names in label_statistics.csv."
    )

# Lưu tên tiếng Việt
selected_df["label_vi"] = (
    selected_df["primary_label"]
    .map(lambda name: translations[name]["vi"])
)

# Lưu danh sách ca được chọn
selected_df.to_csv(
    DATA_DIR / "selected_cases.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved selected_cases.csv")
