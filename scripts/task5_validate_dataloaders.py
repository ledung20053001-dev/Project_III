#!/usr/bin/env python3
"""Kiểm tra Dataset/DataLoader Task 5 và tạo preview transform train."""

import argparse
import json
import math
import sys
import textwrap
from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dataset import SkinDiseaseDataset, create_dataloader
from src.transforms import build_transforms, denormalize_tensor, load_data_config
from src.utils import set_seed


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/data.yaml')
    parser.add_argument('--output-dir', default='results/data_analysis')
    return parser.parse_args()


def get_font(size, bold=False):
    candidates = [
        Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),
        Path('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def tensor_to_pil(tensor, config):
    tensor = denormalize_tensor(tensor.detach().cpu(), config)
    array = (tensor.permute(1, 2, 0).numpy() * 255).round().astype('uint8')
    return Image.fromarray(array, mode='RGB')


def validate_loader(loader, split, expected_size, num_classes):
    total = 0
    batch_count = 0
    labels_seen = set()
    last_batch_size = None
    for batch in loader:
        images = batch['image']
        labels = batch['label']
        if images.ndim != 4 or tuple(images.shape[1:]) != (3, expected_size, expected_size):
            raise ValueError(f'{split}: shape ảnh sai: {tuple(images.shape)}')
        if images.dtype != torch.float32:
            raise ValueError(f'{split}: dtype ảnh sai: {images.dtype}')
        if labels.ndim != 1 or labels.dtype != torch.long:
            raise ValueError(f'{split}: shape/dtype nhãn sai: {labels.shape}, {labels.dtype}')
        if not torch.isfinite(images).all():
            raise ValueError(f'{split}: tensor có NaN hoặc vô hạn')
        if labels.min().item() < 0 or labels.max().item() >= num_classes:
            raise ValueError(f'{split}: nhãn ngoài khoảng 0..{num_classes - 1}')
        labels_seen.update(labels.tolist())
        total += labels.numel()
        batch_count += 1
        last_batch_size = labels.numel()
    if total != len(loader.dataset):
        raise ValueError(f'{split}: đọc {total}/{len(loader.dataset)} ảnh')
    if labels_seen != set(range(num_classes)):
        raise ValueError(f'{split}: thiếu lớp, chỉ có {sorted(labels_seen)}')
    return {
        'images': total,
        'batches': batch_count,
        'last_batch_size': last_batch_size,
        'classes_seen': sorted(labels_seen),
        'image_shape': [3, expected_size, expected_size],
        'image_dtype': 'torch.float32',
        'label_dtype': 'torch.int64',
        'finite': True,
    }


def verify_transform_behavior(datasets):
    val_first = datasets['val'][0]['image']
    val_second = datasets['val'][0]['image']
    test_first = datasets['test'][0]['image']
    test_second = datasets['test'][0]['image']
    if not torch.equal(val_first, val_second) or not torch.equal(test_first, test_second):
        raise ValueError('Transform validation/test không xác định')

    train_variants = [datasets['train'][0]['image'] for _ in range(4)]
    augmentation_changes = any(
        not torch.equal(train_variants[0], variant)
        for variant in train_variants[1:]
    )
    if not augmentation_changes:
        raise ValueError('Không quan sát được augmentation ngẫu nhiên trên train')
    return {
        'train_augmentation_observed': True,
        'validation_deterministic': True,
        'test_deterministic': True,
    }


def create_preview(dataset, config, output_path):
    by_class = {}
    for index, sample in enumerate(dataset.samples):
        by_class.setdefault(sample['class_id'], index)
    if sorted(by_class) != list(range(len(dataset.mapping))):
        raise ValueError('Không đủ lớp để tạo preview')

    tile_size = int(config['image_size'])
    label_height = 72
    columns = 4
    rows = math.ceil(len(by_class) / columns)
    canvas = Image.new(
        'RGB',
        (columns * tile_size, rows * (tile_size + label_height)),
        (245, 247, 250),
    )
    draw = ImageDraw.Draw(canvas)
    title_font = get_font(18, bold=True)
    small_font = get_font(14)
    for position, class_id in enumerate(sorted(by_class)):
        item = dataset[by_class[class_id]]
        preview = tensor_to_pil(item['image'], config)
        x = (position % columns) * tile_size
        y = (position // columns) * (tile_size + label_height)
        canvas.paste(preview, (x, y))
        label_lines = textwrap.wrap(
            f"{class_id}: {dataset.mapping[class_id]['label_en']}",
            width=20,
        )[:2]
        draw.multiline_text(
            (x + 6, y + tile_size + 4),
            '\n'.join(label_lines),
            fill='#17324D',
            font=small_font,
            spacing=2,
        )
        draw.text(
            (x + 6, y + tile_size + 48),
            f"case: {item['case_id']}",
            fill='#37536D',
            font=small_font,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format='PNG')


def main():
    args = parse_args()
    config = load_data_config(PROJECT_ROOT / args.config)
    set_seed(config['seed'])
    train_transform, eval_transform = build_transforms(config)
    paths = config['paths']
    datasets = {
        'train': SkinDiseaseDataset(
            paths['train'], paths['mapping'], PROJECT_ROOT, train_transform
        ),
        'val': SkinDiseaseDataset(
            paths['val'], paths['mapping'], PROJECT_ROOT, eval_transform
        ),
        'test': SkinDiseaseDataset(
            paths['test'], paths['mapping'], PROJECT_ROOT, eval_transform
        ),
    }
    loaders = {
        split: create_dataloader(dataset, config, split)
        for split, dataset in datasets.items()
    }
    num_classes = len(datasets['train'].mapping)
    checks = {
        split: validate_loader(
            loaders[split], split, int(config['image_size']), num_classes
        )
        for split in ('train', 'val', 'test')
    }
    checks['transform_behavior'] = verify_transform_behavior(datasets)
    output_dir = PROJECT_ROOT / args.output_dir
    preview_path = output_dir / 'task5_train_transform_preview.png'
    create_preview(datasets['train'], config, preview_path)
    result = {
        'status': 'passed',
        'config': str((PROJECT_ROOT / args.config).relative_to(PROJECT_ROOT)).replace('\\', '/'),
        'seed': config['seed'],
        'batch_size': config['batch_size'],
        'num_workers': config['num_workers'],
        'pin_memory': loaders['train'].pin_memory,
        'drop_last_train': loaders['train'].drop_last,
        'checks': checks,
        'preview': str(preview_path.relative_to(PROJECT_ROOT)).replace('\\', '/'),
        'torch_version': torch.__version__,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / 'task5_dataloader_validation.json').open('w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    for split in ('train', 'val', 'test'):
        item = checks[split]
        print(
            f"{split}: {item['images']} ảnh, {item['batches']} batch, "
            f"batch cuối {item['last_batch_size']}"
        )
    print('Kiểm tra DataLoader: PASSED')
    print(f'Preview: {preview_path}')


if __name__ == '__main__':
    main()

