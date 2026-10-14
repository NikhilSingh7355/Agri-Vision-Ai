"""Demo-mode image analysis (NOT a trained classifier).

Estimates the share of a leaf photo that shows yellow/brown lesion colours.
Used only when no trained model file (model.keras) is present.
"""
import numpy as np
from PIL import Image


def lesion_share(img: Image.Image):
    im = img.convert("RGB").resize((256, 256))
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    plant = (s > 0.25) & (v > 0.12) & (h > 15) & (h < 170)
    healthy_green = plant & (h >= 75)
    lesion = plant & (h < 75)
    total = plant.sum()
    if total < 500:
        return None
    return float(lesion.sum() / total)


def severity(share: float):
    if share < 0.05:
        return "none"
    if share < 0.20:
        return "mild"
    if share < 0.45:
        return "moderate"
    return "severe"
