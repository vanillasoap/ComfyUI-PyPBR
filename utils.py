"""
Utility functions for converting between ComfyUI image tensors and PyPBR materials.

ComfyUI images: torch.Tensor [B, H, W, C] float32, range [0, 1], RGB
PyPBR materials: use torch.Tensor [C, H, W] float32, range [0, 1] internally
"""

import torch
import numpy as np
from PIL import Image


def comfyui_to_pil(tensor: torch.Tensor) -> Image.Image:
    """Convert a ComfyUI image tensor [B, H, W, C] to a PIL Image (first batch item)."""
    if tensor.dim() == 4:
        tensor = tensor[0]  # Take first batch item
    img_np = (tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    if img_np.shape[-1] == 1:
        img_np = img_np.squeeze(-1)
        return Image.fromarray(img_np, mode="L")
    return Image.fromarray(img_np, mode="RGB")


def comfyui_to_pil_grayscale(tensor: torch.Tensor) -> Image.Image:
    """Convert a ComfyUI image tensor to a grayscale PIL Image.
    If input is RGB, averages channels. If single-channel, uses directly."""
    if tensor.dim() == 4:
        tensor = tensor[0]
    if tensor.shape[-1] == 3:
        tensor = tensor.mean(dim=-1)
    elif tensor.shape[-1] == 1:
        tensor = tensor.squeeze(-1)
    img_np = (tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(img_np, mode="L")


def pil_to_comfyui(image: Image.Image) -> torch.Tensor:
    """Convert a PIL Image to a ComfyUI image tensor [1, H, W, C]."""
    if image is None:
        return None
    if image.mode == "L":
        img_np = np.array(image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np).unsqueeze(-1)  # [H, W, 1]
        tensor = tensor.expand(-1, -1, 3)  # [H, W, 3] - broadcast to RGB
    elif image.mode == "LA":
        img_np = np.array(image.convert("L")).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np).unsqueeze(-1).expand(-1, -1, 3)
    elif image.mode == "RGBA":
        img_np = np.array(image.convert("RGB")).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np)
    else:
        image = image.convert("RGB")
        img_np = np.array(image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_np)
    return tensor.unsqueeze(0)  # [1, H, W, C]


def comfyui_to_mask(tensor: torch.Tensor) -> torch.Tensor:
    """Convert a ComfyUI image tensor [B, H, W, C] to a PyPBR-compatible mask [1, H, W]."""
    if tensor.dim() == 4:
        tensor = tensor[0]  # [H, W, C]
    if tensor.shape[-1] == 3:
        tensor = tensor.mean(dim=-1)  # [H, W]
    elif tensor.shape[-1] == 1:
        tensor = tensor.squeeze(-1)  # [H, W]
    return tensor.unsqueeze(0)  # [1, H, W]


def material_map_to_comfyui(material, map_name: str) -> torch.Tensor:
    """Extract a named map from a PyPBR material and return as ComfyUI tensor."""
    map_tensor = getattr(material, map_name, None)
    if map_tensor is None:
        return None

    # PyPBR stores maps as [C, H, W] tensors
    if isinstance(map_tensor, torch.Tensor):
        if map_tensor.dim() == 3:
            t = map_tensor.permute(1, 2, 0).cpu()  # [H, W, C]
            if t.shape[-1] == 1:
                t = t.expand(-1, -1, 3)
            return t.unsqueeze(0)  # [1, H, W, C]
        elif map_tensor.dim() == 2:
            t = map_tensor.cpu().unsqueeze(-1).expand(-1, -1, 3)
            return t.unsqueeze(0)
    elif isinstance(map_tensor, Image.Image):
        return pil_to_comfyui(map_tensor)

    return None
