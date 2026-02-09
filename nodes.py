"""
ComfyUI custom nodes for PyPBR 0.1.0b4+
https://github.com/giuvecchio/PyPBR

API (b4):
  pypbr.materials  — BasecolorMetallicMaterial, DiffuseSpecularMaterial
  pypbr.transforms — Resize, Rotate, Crop, Tile, Roll, FlipHorizontal, FlipVertical,
                     ToLinear, ToSrgb, AdjustNormalStrength, InvertNormal, Compose
  pypbr.blending   — MaskBlend, HeightBlend, GradientBlend, PropertyBlend
  pypbr.io         — load_material_from_folder, save_material_to_folder
  pypbr.models     — CookTorranceBRDF (assumed)
"""

import os
import copy
import torch
import numpy as np
from PIL import Image

from .utils import (
    comfyui_to_pil,
    comfyui_to_pil_grayscale,
    pil_to_comfyui,
    comfyui_to_mask,
    material_map_to_comfyui,
)

CATEGORY = "PyPBR"


# ── Material Creation ────────────────────────────────────────────────────────

class PyPBRCreateMaterial:
    """Create a BasecolorMetallicMaterial from individual PBR maps."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"albedo": ("IMAGE",)},
            "optional": {
                "normal": ("IMAGE",),
                "roughness": ("IMAGE",),
                "metallic": ("IMAGE",),
                "height": ("IMAGE",),
                "displacement": ("IMAGE",),
                "ao": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "create_material"
    CATEGORY = CATEGORY

    def create_material(self, albedo, normal=None, roughness=None, metallic=None,
                        height=None, displacement=None, ao=None):
        from pypbr.materials import BasecolorMetallicMaterial
        kw = {"albedo": comfyui_to_pil(albedo)}
        if normal is not None:      kw["normal"] = comfyui_to_pil(normal)
        if roughness is not None:    kw["roughness"] = comfyui_to_pil_grayscale(roughness)
        if metallic is not None:     kw["metallic"] = comfyui_to_pil_grayscale(metallic)
        if height is not None:       kw["height"] = comfyui_to_pil_grayscale(height)
        if displacement is not None: kw["displacement"] = comfyui_to_pil_grayscale(displacement)
        if ao is not None:           kw["ao"] = comfyui_to_pil_grayscale(ao)
        return (BasecolorMetallicMaterial(**kw),)


class PyPBRCreateDiffuseSpecularMaterial:
    """Create a DiffuseSpecularMaterial from individual PBR maps."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"albedo": ("IMAGE",)},
            "optional": {
                "normal": ("IMAGE",),
                "specular": ("IMAGE",),
                "glossiness": ("IMAGE",),
                "height": ("IMAGE",),
                "displacement": ("IMAGE",),
                "ao": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "create_material"
    CATEGORY = CATEGORY

    def create_material(self, albedo, normal=None, specular=None, glossiness=None,
                        height=None, displacement=None, ao=None):
        from pypbr.materials import DiffuseSpecularMaterial
        kw = {"albedo": comfyui_to_pil(albedo)}
        if normal is not None:       kw["normal"] = comfyui_to_pil(normal)
        if specular is not None:     kw["specular"] = comfyui_to_pil(specular)
        if glossiness is not None:   kw["glossiness"] = comfyui_to_pil_grayscale(glossiness)
        if height is not None:       kw["height"] = comfyui_to_pil_grayscale(height)
        if displacement is not None: kw["displacement"] = comfyui_to_pil_grayscale(displacement)
        if ao is not None:           kw["ao"] = comfyui_to_pil_grayscale(ao)
        return (DiffuseSpecularMaterial(**kw),)


class PyPBRImageToMaterial:
    """Wrap a single image as a minimal BasecolorMetallicMaterial (albedo only)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "create"
    CATEGORY = CATEGORY

    def create(self, image):
        from pypbr.materials import BasecolorMetallicMaterial
        return (BasecolorMetallicMaterial(albedo=comfyui_to_pil(image)),)


# ── I/O ──────────────────────────────────────────────────────────────────────

class PyPBRLoadMaterial:
    """Load a PBR material from a folder of texture files."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "preferred_workflow": (["metallic", "specular"],),
            },
        }

    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "load_material"
    CATEGORY = CATEGORY

    def load_material(self, folder_path, preferred_workflow):
        from pypbr.io import load_material_from_folder
        return (load_material_from_folder(folder_path, preferred_workflow=preferred_workflow),)


class PyPBRSaveMaterial:
    """Save a PBR material to a folder as individual texture files."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "folder_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "format": (["png", "jpg", "tiff", "exr"],),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save_material"
    CATEGORY = CATEGORY

    def save_material(self, material, folder_path, format="png"):
        from pypbr.io import save_material_to_folder
        os.makedirs(folder_path, exist_ok=True)
        save_material_to_folder(material, folder_path, format=format)
        return {}


# ── Extract Maps ─────────────────────────────────────────────────────────────

class PyPBRExtractMaps:
    """Extract individual maps from a material as ComfyUI IMAGE tensors."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"material": ("PYPBR_MATERIAL",)}}

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("albedo", "normal", "roughness", "metallic", "height", "ao")
    FUNCTION = "extract_maps"
    CATEGORY = CATEGORY

    def extract_maps(self, material):
        names = ["albedo", "normal", "roughness", "metallic", "height", "ao"]
        results = []
        # determine fallback size from albedo
        albedo_t = material_map_to_comfyui(material, "albedo")
        if albedo_t is not None:
            h, w = albedo_t.shape[1], albedo_t.shape[2]
        else:
            h, w = 512, 512

        for name in names:
            tensor = material_map_to_comfyui(material, name)
            if tensor is None:
                tensor = torch.zeros(1, h, w, 3)
            results.append(tensor)
        return tuple(results)


# ── Transforms (class-based in b4) ──────────────────────────────────────────

class PyPBRResize:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "width": ("INT", {"default": 512, "min": 32, "max": 8192, "step": 32}),
                "height": ("INT", {"default": 512, "min": 32, "max": 8192, "step": 32}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, width, height):
        from pypbr.transforms import Resize
        return (Resize((height, width))(copy.deepcopy(material)),)


class PyPBRRotate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "angle": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "expand": ("BOOLEAN", {"default": False}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, angle, expand):
        from pypbr.transforms import Rotate
        return (Rotate(angle, expand=expand)(copy.deepcopy(material)),)


class PyPBRCrop:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "top": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "left": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "height": ("INT", {"default": 256, "min": 1, "max": 8192}),
                "width": ("INT", {"default": 256, "min": 1, "max": 8192}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, top, left, height, width):
        from pypbr.transforms import Crop
        return (Crop(top=top, left=left, height=height, width=width)(copy.deepcopy(material)),)


class PyPBRFlip:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "direction": (["horizontal", "vertical"],),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, direction):
        from pypbr.transforms import FlipHorizontal, FlipVertical
        T = FlipHorizontal if direction == "horizontal" else FlipVertical
        return (T()(copy.deepcopy(material)),)


class PyPBRTile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "num_tiles": ("INT", {"default": 2, "min": 1, "max": 16}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, num_tiles):
        from pypbr.transforms import Tile
        return (Tile(num_tiles=num_tiles)(copy.deepcopy(material)),)


class PyPBRRoll:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "shift_height": ("INT", {"default": 0, "min": -8192, "max": 8192}),
                "shift_width": ("INT", {"default": 0, "min": -8192, "max": 8192}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, shift_height, shift_width):
        from pypbr.transforms import Roll
        return (Roll(shift=(shift_height, shift_width))(copy.deepcopy(material)),)


# ── Normal Map ───────────────────────────────────────────────────────────────

class PyPBRAdjustNormalStrength:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0, "step": 0.05}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, strength):
        from pypbr.transforms import AdjustNormalStrength
        return (AdjustNormalStrength(strength)(copy.deepcopy(material)),)


class PyPBRInvertNormal:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"material": ("PYPBR_MATERIAL",)}}
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material):
        from pypbr.transforms import InvertNormal
        return (InvertNormal()(copy.deepcopy(material)),)


# ── Color Space ──────────────────────────────────────────────────────────────

class PyPBRColorSpace:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "conversion": (["to_linear", "to_srgb"],),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, conversion):
        from pypbr.transforms import ToLinear, ToSrgb
        T = ToLinear if conversion == "to_linear" else ToSrgb
        return (T()(copy.deepcopy(material)),)


# ── Workflow Conversion ──────────────────────────────────────────────────────

class PyPBRConvertWorkflow:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "target_workflow": (["metallic", "specular"],),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, target_workflow):
        from pypbr.materials import BasecolorMetallicMaterial, DiffuseSpecularMaterial
        if target_workflow == "specular" and isinstance(material, BasecolorMetallicMaterial):
            return (material.to_diffuse_specular_material(),)
        elif target_workflow == "metallic" and isinstance(material, DiffuseSpecularMaterial):
            return (material.to_basecolor_metallic_material(),)
        return (material,)


# ── Blending ─────────────────────────────────────────────────────────────────

class PyPBRBlendMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material_a": ("PYPBR_MATERIAL",),
                "material_b": ("PYPBR_MATERIAL",),
                "mask": ("IMAGE",),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material_a, material_b, mask):
        from pypbr.blending import MaskBlend
        return (MaskBlend(comfyui_to_mask(mask))(material_a, material_b),)


class PyPBRBlendHeight:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material_a": ("PYPBR_MATERIAL",),
                "material_b": ("PYPBR_MATERIAL",),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material_a, material_b):
        from pypbr.blending import HeightBlend
        return (HeightBlend()(material_a, material_b),)


class PyPBRBlendGradient:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material_a": ("PYPBR_MATERIAL",),
                "material_b": ("PYPBR_MATERIAL",),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material_a, material_b):
        from pypbr.blending import GradientBlend
        return (GradientBlend()(material_a, material_b),)


# ── BRDF Rendering ───────────────────────────────────────────────────────────

class PyPBRCookTorranceRender:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "material": ("PYPBR_MATERIAL",),
                "light_type": (["point", "directional"],),
                "view_x": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "view_y": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "view_z": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "light_x": ("FLOAT", {"default": 0.1, "min": -10.0, "max": 10.0, "step": 0.01}),
                "light_y": ("FLOAT", {"default": 0.1, "min": -10.0, "max": 10.0, "step": 0.01}),
                "light_z": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "intensity_r": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "intensity_g": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "intensity_b": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
            },
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("rendered",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, light_type, view_x, view_y, view_z,
            light_x, light_y, light_z, intensity_r, intensity_g, intensity_b):
        from pypbr.models import CookTorranceBRDF

        brdf = CookTorranceBRDF(light_type=light_type)
        view_dir = torch.tensor([view_x, view_y, view_z])
        light_dir = torch.tensor([light_x, light_y, light_z])
        intensity = torch.tensor([intensity_r, intensity_g, intensity_b])

        color = brdf(material, view_dir, light_dir, intensity)

        if isinstance(color, torch.Tensor):
            if color.dim() == 3 and color.shape[0] == 3:
                color = color.permute(1, 2, 0)
            return (color.clamp(0, 1).cpu().unsqueeze(0),)
        return (pil_to_comfyui(color),)


# ── Compose ──────────────────────────────────────────────────────────────────

class PyPBRTransformCompose:
    """Chain multiple transforms in one node. Set width/height or tile to 0 to skip."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"material": ("PYPBR_MATERIAL",)},
            "optional": {
                "resize_w": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 32}),
                "resize_h": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 32}),
                "rotate_angle": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0}),
                "tile_count": ("INT", {"default": 0, "min": 0, "max": 16}),
                "flip_h": ("BOOLEAN", {"default": False}),
                "flip_v": ("BOOLEAN", {"default": False}),
                "to_linear": ("BOOLEAN", {"default": False}),
                "to_srgb": ("BOOLEAN", {"default": False}),
            },
        }
    RETURN_TYPES = ("PYPBR_MATERIAL",)
    RETURN_NAMES = ("material",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material, resize_w=0, resize_h=0, rotate_angle=0.0,
            tile_count=0, flip_h=False, flip_v=False, to_linear=False, to_srgb=False):
        from pypbr.transforms import (
            Compose, Resize, Rotate, Tile,
            FlipHorizontal, FlipVertical, ToLinear, ToSrgb,
        )
        tfms = []
        if resize_w > 0 and resize_h > 0:
            tfms.append(Resize((resize_h, resize_w)))
        if rotate_angle != 0.0:
            tfms.append(Rotate(rotate_angle))
        if tile_count > 0:
            tfms.append(Tile(num_tiles=tile_count))
        if flip_h: tfms.append(FlipHorizontal())
        if flip_v: tfms.append(FlipVertical())
        if to_linear: tfms.append(ToLinear())
        if to_srgb:   tfms.append(ToSrgb())

        if not tfms:
            return (material,)
        return (Compose(tfms)(copy.deepcopy(material)),)


# ── Material Info ────────────────────────────────────────────────────────────

class PyPBRMaterialInfo:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"material": ("PYPBR_MATERIAL",)}}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, material):
        lines = [f"Type: {type(material).__name__}"]
        for name in ["albedo", "normal", "roughness", "metallic", "height",
                      "displacement", "ao", "specular", "glossiness", "diffuse"]:
            val = getattr(material, name, None)
            if val is not None:
                if isinstance(val, torch.Tensor):
                    lines.append(f"  {name}: tensor {list(val.shape)}")
                elif isinstance(val, Image.Image):
                    lines.append(f"  {name}: PIL {val.size} {val.mode}")
                else:
                    lines.append(f"  {name}: {type(val).__name__}")
        return ("\n".join(lines),)
