import io
from pathlib import Path

import pandas as pd
from google.cloud import storage
from PIL import Image
from tqdm import tqdm


# ==============================
# CONFIG
# ==============================

CSV_PATH = "data/metadata/scin_cases.csv"
OUTPUT_DIR = Path("data/images_all")

BUCKET_NAME = "dx-scin-public-data"

IMAGE_COLUMNS = [
    "image_1_path",
    "image_2_path",
    "image_3_path",
]


# ==============================
# LOAD METADATA
# ==============================

df = pd.read_csv(
    CSV_PATH,
    dtype={"case_id": str}
)

print(f"Total cases: {len(df)}")


# ==============================
# CONNECT GCS
# ==============================

client = storage.Client.create_anonymous_client()
bucket = client.bucket(BUCKET_NAME)


# ==============================
# CREATE OUTPUT DIR
# ==============================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================
# DOWNLOAD
# ==============================

downloaded = []
failed = []

total_paths = df[IMAGE_COLUMNS].notna().sum().sum()

print(f"Total image paths: {total_paths}")


with tqdm(total=total_paths, desc="Downloading SCIN") as pbar:

    for _, row in df.iterrows():

        case_id = str(row["case_id"])

        for image_index, column in enumerate(
            IMAGE_COLUMNS,
            start=1
        ):

            image_path = row[column]

            if pd.isna(image_path):
                continue

            image_path = str(image_path).strip()

            if not image_path:
                continue

            # File name:
            # case_id_1.jpg
            # case_id_2.jpg
            # case_id_3.jpg
            filename = f"{case_id}_{image_index}.jpg"

            destination = OUTPUT_DIR / filename

            try:

                # Nếu file đã tồn tại thì bỏ qua
                if destination.exists():

                    downloaded.append({
                        "case_id": case_id,
                        "image_index": image_index,
                        "source_path": image_path,
                        "local_path": str(destination),
                        "status": "already_exists"
                    })

                    pbar.update(1)
                    continue


                # ==============================
                # DOWNLOAD FROM GOOGLE CLOUD
                # ==============================

                blob = bucket.blob(image_path)

                image_bytes = blob.download_as_bytes(
                    timeout=120
                )


                # ==============================
                # VALIDATE IMAGE
                # ==============================

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
                    "image_index": image_index,
                    "source_path": image_path,
                    "local_path": str(destination),
                    "status": "downloaded"
                })


            except Exception as e:

                failed.append({
                    "case_id": case_id,
                    "image_index": image_index,
                    "source_path": image_path,
                    "error": str(e)
                })


            pbar.update(1)


# ==============================
# SAVE MANIFEST
# ==============================

download_manifest = pd.DataFrame(downloaded)

download_manifest.to_csv(
    "data/metadata/all_images_manifest.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==============================
# SAVE FAILED DOWNLOADS
# ==============================

failed_df = pd.DataFrame(failed)

failed_df.to_csv(
    "data/metadata/failed_downloads.csv",
    index=False,
    encoding="utf-8-sig"
)


print()
print("==============================")
print("DOWNLOAD FINISHED")
print("==============================")

print(f"Successful / existing: {len(downloaded)}")
print(f"Failed: {len(failed)}")

print(
    "Manifest saved to: "
    "data/metadata/all_images_manifest.csv"
)

print(
    "Failed list saved to: "
    "data/metadata/failed_downloads.csv"
)