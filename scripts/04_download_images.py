
import io
from pathlib import Path

import pandas as pd
from google.cloud import storage
from PIL import Image
from tqdm import tqdm

# Metadata sau khi chọn bệnh
df = pd.read_csv(
    "data/metadata/selected_cases.csv",
    dtype={"case_id": str}
)

# Public Google Cloud Storage bucket
client = storage.Client.create_anonymous_client()
bucket = client.bucket("dx-scin-public-data")

OUTPUT_DIR = Path("data/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_COLS = [
    "image_1_path",
    "image_2_path",
    "image_3_path"
]

downloaded = []
failed = []

for _, row in tqdm(
    df.iterrows(),
    total=len(df),
    desc="Downloading cases"
):
    case_id = str(row["case_id"])
    label = row["primary_label"]
    label_vi = row["label_vi"]

    # Dùng tên gốc để tránh lỗi đường dẫn Unicode
    class_dir = OUTPUT_DIR / label
    class_dir.mkdir(parents=True, exist_ok=True)

    for index, col in enumerate(IMAGE_COLS, 1):
        image_path = row[col]

        if pd.isna(image_path):
            continue

        image_path = str(image_path).strip()

        if not image_path:
            continue

        filename = f"{case_id}_{index}.jpg"
        destination = class_dir / filename

        try:
            if not destination.exists():
                blob = bucket.blob(image_path)
                image_bytes = blob.download_as_bytes(
                    timeout=60
                )

                # Kiểm tra ảnh hợp lệ
                with Image.open(
                    io.BytesIO(image_bytes)
                ) as img:
                    img = img.convert("RGB")
                    img.save(
                        destination,
                        format="JPEG",
                        quality=95
                    )

            downloaded.append({
                "case_id": case_id,
                "image_path": str(destination),
                "source_path": image_path,
                "label_en": label,
                "label_vi": label_vi,
                "label_weight": row["label_weight"]
            })

        except Exception as e:
            failed.append({
                "case_id": case_id,
                "source_path": image_path,
                "error": str(e)
            })

# Lưu danh sách ảnh huấn luyện
manifest = pd.DataFrame(downloaded)

manifest.to_csv(
    "data/metadata/train_manifest.csv",
    index=False,
    encoding="utf-8-sig"
)

# Lưu ảnh tải thất bại để xử lý sau
pd.DataFrame(failed).to_csv(
    "data/metadata/failed_downloads.csv",
    index=False,
    encoding="utf-8-sig"
)

print(f"Downloaded: {len(downloaded)} images")
print(f"Failed: {len(failed)} images")
