
import ast
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/metadata")

cases = pd.read_csv(
    DATA_DIR / "scin_cases.csv",
    dtype={"case_id": str}
)

labels = pd.read_csv(
    DATA_DIR / "scin_labels.csv",
    dtype={"case_id": str}
)

# Gộp 2 bảng theo mã ca bệnh
df = cases.merge(
    labels,
    on="case_id",
    how="inner",
    validate="one_to_one"
)

IMAGE_COLS = [
    "image_1_path",
    "image_2_path",
    "image_3_path"
]

def parse_labels(value):
    if pd.isna(value):
        return {}

    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, SyntaxError):
        return {}

def get_primary_label(value):
    weights = parse_labels(value)

    if not weights:
        return pd.Series([None, 0.0])

    name, weight = max(
        weights.items(),
        key=lambda item: item[1]
    )

    return pd.Series([name, float(weight)])

# Xác định nhãn chính
df[["primary_label", "label_weight"]] = (
    df["weighted_skin_condition_label"]
    .apply(get_primary_label)
)

# Đếm số ảnh theo ca bệnh
df["image_count"] = (
    df[IMAGE_COLS].notna().sum(axis=1)
)

# Chỉ giữ nhãn đủ rõ ràng
MIN_WEIGHT = 0.70

filtered = df[
    (df["label_weight"] >= MIN_WEIGHT) &
    (df["image_count"] > 0)
].copy()

# Thống kê theo tên bệnh
stats = (
    filtered.groupby("primary_label")
    .agg(
        total_cases=("case_id", "nunique"),
        total_images=("image_count", "sum"),
        avg_label_weight=("label_weight", "mean")
    )
    .sort_values(
        "total_cases",
        ascending=False
    )
    .reset_index()
)

stats.to_csv(
    DATA_DIR / "label_statistics.csv",
    index=False,
    encoding="utf-8-sig"
)

filtered.to_csv(
    DATA_DIR / "eligible_cases.csv",
    index=False,
    encoding="utf-8-sig"
)

print(stats.to_string(index=False))
print("\nSaved label_statistics.csv")
print("Saved eligible_cases.csv")
