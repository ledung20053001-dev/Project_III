"""Các tiện ích tái lập thí nghiệm và DataLoader."""

import os
import random

import torch


def set_seed(seed):
    seed = int(seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, 'cudnn'):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def seed_worker(worker_id):
    del worker_id
    worker_seed = torch.initial_seed() % (2**32)
    random.seed(worker_seed)


def resolve_pin_memory(value):
    if isinstance(value, bool):
        return value
    if str(value).lower() == 'auto':
        return torch.cuda.is_available()
    raise ValueError("pin_memory phải là true, false hoặc 'auto'")

