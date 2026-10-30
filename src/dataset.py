"""PyTorch Dataset và DataLoader cho các CSV cố định của Task 4."""

import csv
import json
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from src.utils import resolve_pin_memory, seed_worker


class SkinDiseaseDataset(Dataset):
    """Đọc ảnh từ manifest và lấy target trực tiếp từ class_id."""

    def __init__(self, csv_path, mapping_path, project_root='.', transform=None):
        self.project_root = Path(project_root).resolve()
        self.csv_path = (self.project_root / csv_path).resolve()
        self.mapping_path = (self.project_root / mapping_path).resolve()
        self.transform = transform
        self.mapping = self._load_mapping()
        self.samples = self._load_samples()

    def _load_mapping(self):
        with self.mapping_path.open(encoding='utf-8') as handle:
            raw = json.load(handle)
        mapping = {int(key): value for key, value in raw.items()}
        if sorted(mapping) != list(range(len(mapping))):
            raise ValueError('class_id trong mapping phải liên tục từ 0 đến N-1')
        return mapping

    def _load_samples(self):
        required = {'case_id', 'image_path', 'class_id', 'label_en', 'label_vi'}
        samples = []
        with self.csv_path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f'{self.csv_path}: thiếu cột {sorted(missing)}')
            for row in reader:
                try:
                    class_id = int(row['class_id'])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f'{self.csv_path}: class_id sai tại dòng {reader.line_num}'
                    ) from exc
                if class_id not in self.mapping:
                    raise ValueError(f'class_id {class_id} không có trong mapping')
                expected = self.mapping[class_id]
                if row['label_en'] != expected['label_en'] or row['label_vi'] != expected['label_vi']:
                    raise ValueError(
                        f'{self.csv_path}: nhãn không khớp mapping tại dòng {reader.line_num}'
                    )
                image_path = (self.project_root / row['image_path']).resolve()
                try:
                    image_path.relative_to(self.project_root)
                except ValueError as exc:
                    raise ValueError(f'Ảnh nằm ngoài project root: {image_path}') from exc
                if not image_path.is_file():
                    raise FileNotFoundError(image_path)
                samples.append({
                    'image_path': image_path,
                    'relative_image_path': Path(row['image_path']).as_posix(),
                    'case_id': str(row['case_id']),
                    'class_id': class_id,
                    'label_en': row['label_en'],
                    'label_vi': row['label_vi'],
                })
        if not samples:
            raise ValueError(f'{self.csv_path}: dataset rỗng')
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample = self.samples[index]
        with Image.open(sample['image_path']) as image:
            image = image.convert('RGB')
            image.load()
            if self.transform is not None:
                image = self.transform(image)
        return {
            'image': image,
            'label': torch.tensor(sample['class_id'], dtype=torch.long),
            'case_id': sample['case_id'],
            'image_path': sample['relative_image_path'],
        }


def create_dataloader(dataset, config, split):
    if split not in {'train', 'val', 'test'}:
        raise ValueError(f'split không hợp lệ: {split}')
    generator = torch.Generator()
    generator.manual_seed(int(config['seed']))
    return DataLoader(
        dataset,
        batch_size=int(config['batch_size']),
        shuffle=(split == 'train'),
        num_workers=int(config['num_workers']),
        pin_memory=resolve_pin_memory(config['pin_memory']),
        drop_last=bool(config['drop_last_train']) if split == 'train' else False,
        worker_init_fn=seed_worker,
        generator=generator,
        persistent_workers=(int(config['num_workers']) > 0),
    )

