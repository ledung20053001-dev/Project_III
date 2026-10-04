
from pathlib import Path
import requests

BASE_URL = (
    "https://storage.googleapis.com/"
    "dx-scin-public-data/dataset/"
)

FILES = [
    "scin_cases.csv",
    "scin_labels.csv"
]

SAVE_DIR = Path("data/metadata")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

for filename in FILES:
    url = BASE_URL + filename
    destination = SAVE_DIR / filename

    print(f"Downloading {filename}...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    destination.write_bytes(response.content)

    print(f"Saved: {destination}")

print("Metadata downloaded successfully!")
