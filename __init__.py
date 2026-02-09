"""
ComfyUI-PyPBR-Nodes — PyPBR 0.1.0b4+ wrapper nodes.
https://github.com/giuvecchio/PyPBR
"""

from .nodes import (
    PyPBRCreateMaterial,
    PyPBRCreateDiffuseSpecularMaterial,
    PyPBRImageToMaterial,
    PyPBRLoadMaterial,
    PyPBRSaveMaterial,
    PyPBRExtractMaps,
    PyPBRResize,
    PyPBRRotate,
    PyPBRCrop,
    PyPBRFlip,
    PyPBRTile,
    PyPBRRoll,
    PyPBRAdjustNormalStrength,
    PyPBRInvertNormal,
    PyPBRColorSpace,
    PyPBRConvertWorkflow,
    PyPBRBlendMask,
    PyPBRBlendHeight,
    PyPBRBlendGradient,
    PyPBRCookTorranceRender,
    PyPBRTransformCompose,
    PyPBRMaterialInfo,
)

NODE_CLASS_MAPPINGS = {
    "PyPBR_CreateMaterial":              PyPBRCreateMaterial,
    "PyPBR_CreateDiffuseSpecularMat":    PyPBRCreateDiffuseSpecularMaterial,
    "PyPBR_ImageToMaterial":             PyPBRImageToMaterial,
    "PyPBR_LoadMaterial":                PyPBRLoadMaterial,
    "PyPBR_SaveMaterial":                PyPBRSaveMaterial,
    "PyPBR_ExtractMaps":                 PyPBRExtractMaps,
    "PyPBR_Resize":                      PyPBRResize,
    "PyPBR_Rotate":                      PyPBRRotate,
    "PyPBR_Crop":                        PyPBRCrop,
    "PyPBR_Flip":                        PyPBRFlip,
    "PyPBR_Tile":                        PyPBRTile,
    "PyPBR_Roll":                        PyPBRRoll,
    "PyPBR_AdjustNormalStrength":        PyPBRAdjustNormalStrength,
    "PyPBR_InvertNormal":                PyPBRInvertNormal,
    "PyPBR_ColorSpace":                  PyPBRColorSpace,
    "PyPBR_ConvertWorkflow":             PyPBRConvertWorkflow,
    "PyPBR_BlendMask":                   PyPBRBlendMask,
    "PyPBR_BlendHeight":                 PyPBRBlendHeight,
    "PyPBR_BlendGradient":               PyPBRBlendGradient,
    "PyPBR_CookTorranceRender":          PyPBRCookTorranceRender,
    "PyPBR_TransformCompose":            PyPBRTransformCompose,
    "PyPBR_MaterialInfo":                PyPBRMaterialInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PyPBR_CreateMaterial":              "PyPBR Create Material (Metallic)",
    "PyPBR_CreateDiffuseSpecularMat":    "PyPBR Create Material (Specular)",
    "PyPBR_ImageToMaterial":             "PyPBR Image → Material",
    "PyPBR_LoadMaterial":                "PyPBR Load Material",
    "PyPBR_SaveMaterial":                "PyPBR Save Material",
    "PyPBR_ExtractMaps":                 "PyPBR Extract Maps",
    "PyPBR_Resize":                      "PyPBR Resize",
    "PyPBR_Rotate":                      "PyPBR Rotate",
    "PyPBR_Crop":                        "PyPBR Crop",
    "PyPBR_Flip":                        "PyPBR Flip",
    "PyPBR_Tile":                        "PyPBR Tile",
    "PyPBR_Roll":                        "PyPBR Roll (Offset)",
    "PyPBR_AdjustNormalStrength":        "PyPBR Adjust Normal Strength",
    "PyPBR_InvertNormal":                "PyPBR Invert Normal (DX↔GL)",
    "PyPBR_ColorSpace":                  "PyPBR Color Space Convert",
    "PyPBR_ConvertWorkflow":             "PyPBR Convert Workflow",
    "PyPBR_BlendMask":                   "PyPBR Mask Blend",
    "PyPBR_BlendHeight":                 "PyPBR Height Blend",
    "PyPBR_BlendGradient":               "PyPBR Gradient Blend",
    "PyPBR_CookTorranceRender":          "PyPBR Cook-Torrance Render",
    "PyPBR_TransformCompose":            "PyPBR Transform Compose",
    "PyPBR_MaterialInfo":                "PyPBR Material Info",
}

WEB_DIRECTORY = None
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
