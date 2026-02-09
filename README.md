# ComfyUI-PyPBR-Nodes

Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that wrap the [PyPBR](https://github.com/giuvecchio/PyPBR) library for PBR material creation, manipulation, blending, and rendering.

## Installation

1. Clone or copy this folder into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone <this-repo> comfyui-pypbr-nodes
   ```

2. Install dependencies:
   ```bash
   cd comfyui-pypbr-nodes
   pip install -r requirements.txt
   ```

3. Restart ComfyUI. The nodes will appear under the **PyPBR** category.

## Nodes

All nodes use a shared `PYPBR_MATERIAL` type that flows between them. This type wraps PyPBR's material classes and carries all texture maps together.

### Material Creation

| Node | Description |
|---|---|
| **PyPBR Create Material (Metallic)** | Build a `BasecolorMetallicMaterial` from albedo + optional normal, roughness, metallic, height, displacement, AO maps |
| **PyPBR Create Material (Specular)** | Build a `DiffuseSpecularMaterial` from albedo + optional normal, specular, glossiness, height, displacement, AO maps |
| **PyPBR Image → Material** | Quick shortcut — wraps a single image as an albedo-only material |

### I/O

| Node | Description |
|---|---|
| **PyPBR Load Material from Folder** | Load a material from a folder of texture files (auto-detects map names). Choose `metallic` or `specular` workflow |
| **PyPBR Save Material to Folder** | Save all maps to a folder as PNG/JPG/TIFF/EXR |

### Map Extraction

| Node | Description |
|---|---|
| **PyPBR Extract Maps** | Output individual maps (albedo, normal, roughness, metallic, height, AO) as standard ComfyUI IMAGE tensors |

### Transforms

All transforms operate on every map in the material simultaneously.

| Node | Description |
|---|---|
| **PyPBR Resize** | Resize to target width × height |
| **PyPBR Rotate** | Rotate by angle (degrees), optional canvas expansion |
| **PyPBR Crop** | Crop by top/left/height/width |
| **PyPBR Flip** | Flip horizontal or vertical |
| **PyPBR Tile** | Tile N×N times |
| **PyPBR Roll (Offset)** | Cyclic shift by pixel amount (useful for seamless testing) |

### Color Space & Workflow

| Node | Description |
|---|---|
| **PyPBR Color Space Convert** | Convert albedo between sRGB ↔ Linear |
| **PyPBR Convert Workflow** | Convert between Metallic ↔ Specular workflows |

### Blending

| Node | Description |
|---|---|
| **PyPBR Blend Materials** | Blend two materials using `mask`, `height`, or `linear` methods |
| **PyPBR Mask Blend** | Dedicated mask-based blend (class-based, takes mask input) |

### Rendering

| Node | Description |
|---|---|
| **PyPBR Cook-Torrance Render** | Evaluate Cook-Torrance BRDF with configurable view/light direction and intensity. Outputs a rendered IMAGE |

### Utility

| Node | Description |
|---|---|
| **PyPBR Material Info** | Outputs a string describing the material type, available maps, and their dimensions |

## Example Workflow

```
[Load Image: albedo] ──┐
[Load Image: normal] ──┤
[Load Image: rough]  ──┼──▶ [PyPBR Create Material] ──▶ [PyPBR Resize 1024×1024] ──┬──▶ [PyPBR Extract Maps] ──▶ [Preview]
[Load Image: metal]  ──┘                                                           │
                                                                                   └──▶ [PyPBR Cook-Torrance Render] ──▶ [Preview]
```

## Notes

- PyPBR uses **PyTorch** internally, so GPU acceleration is available when CUDA is present.
- The `PYPBR_MATERIAL` custom type carries all maps as a bundle — you don't need to wire individual maps between transform/blend/render nodes.
- Maps that don't exist on a material will output as black images from the Extract node.
- All transform nodes create deep copies, so the original material is never modified.

## License

This node pack is MIT licensed. [PyPBR](https://github.com/giuvecchio/PyPBR) is also MIT licensed.
