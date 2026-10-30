"""Transform ảnh dùng chung cho train, validation, test và inference."""

from pathlib import Path

import yaml
from PIL import Image, ImageOps
from torchvision import transforms


class ResizeWithPadding:
    """Resize giữ tỷ lệ và padding để không cắt mất vùng tổn thương."""

    def __init__(self, size, fill=(128, 128, 128)):
        self.size = (int(size), int(size))
        self.fill = tuple(fill)

    def __call__(self, image):
        image = ImageOps.contain(image, self.size, method=Image.Resampling.BILINEAR)
        canvas = Image.new('RGB', self.size, self.fill)
        left = (self.size[0] - image.width) // 2
        top = (self.size[1] - image.height) // 2
        canvas.paste(image, (left, top))
        return canvas

    def __repr__(self):
        return f'{self.__class__.__name__}(size={self.size[0]}, fill={self.fill})'


def load_data_config(path='configs/data.yaml'):
    with Path(path).open(encoding='utf-8') as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f'{path}: cấu hình phải là mapping YAML')
    return config


def build_transforms(config):
    """Trả về transform train và evaluation từ cấu hình đã chốt."""

    image_size = int(config['image_size'])
    normalization = config['normalization']
    mean = normalization['mean']
    std = normalization['std']
    augmentation = config['augmentation']
    fill = augmentation['padding_fill_rgb']

    common_tail = [
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ]
    train_transform = transforms.Compose([
        ResizeWithPadding(image_size, fill=fill),
        transforms.RandomHorizontalFlip(
            p=float(augmentation['horizontal_flip_probability'])
        ),
        transforms.RandomRotation(
            degrees=float(augmentation['rotation_degrees']),
            interpolation=transforms.InterpolationMode.BILINEAR,
            fill=tuple(fill),
        ),
        transforms.ColorJitter(
            brightness=float(augmentation['color_jitter']['brightness']),
            contrast=float(augmentation['color_jitter']['contrast']),
            saturation=float(augmentation['color_jitter']['saturation']),
            hue=float(augmentation['color_jitter']['hue']),
        ),
        *common_tail,
    ])
    eval_transform = transforms.Compose([
        ResizeWithPadding(image_size, fill=fill),
        *common_tail,
    ])
    return train_transform, eval_transform


def denormalize_tensor(tensor, config):
    """Đảo normalization để hiển thị tensor với màu gần ảnh đầu vào."""

    mean = tensor.new_tensor(config['normalization']['mean']).view(3, 1, 1)
    std = tensor.new_tensor(config['normalization']['std']).view(3, 1, 1)
    return (tensor * std + mean).clamp(0, 1)

