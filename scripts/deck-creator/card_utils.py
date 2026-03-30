"""Shared utilities for card pipelines."""

import os
from PIL import Image, ImageFont
import numpy as np


# ── Font config ──
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
DEFAULT_FONT = os.path.join(FONT_DIR, "Newston Regular.ttf")
FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# Font size as percentage of card width (shared across all card types)
FONT_SIZE_PCT = 0.20

# Small corner symbol size as percentage of card width
SMALL_SYM_PCT = 0.095

# Vertical offset of small symbol below letter, as fraction of font size
SYM_Y_OFFSET_PCT = 0.81

# Main suit symbol size as percentage of card width
MAIN_SYM_PCT = 0.25

# Top row vertical position as percentage of card height (center of symbol)
TOP_ROW_Y_PCT = 0.10

# Column inset as percentage of card width (left edge of symbol)
COL_INSET_PCT = 0.055

# Corner x margin as percentage of card width
CORNER_X_PCT = 0.03

# Corner y margin as percentage of card width (note: pct of W, not H)
CORNER_Y_PCT = 0.055

# Crop padding at 200w reference
CROP_PAD_PX_REF = 5


def load_font(path: str = None, size: int = 20) -> ImageFont.FreeTypeFont:
    """Load a TrueType font, falling back gracefully."""
    font_path = path or DEFAULT_FONT
    if not os.path.exists(font_path):
        font_path = FALLBACK_FONT
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def corner_font_size(card_width: int) -> int:
    """Compute the corner font size for a given card width."""
    return max(14, int(card_width * FONT_SIZE_PCT))


def corner_small_sym_size(card_width: int) -> int:
    """Compute the small corner symbol size for a given card width."""
    return max(10, round(card_width * SMALL_SYM_PCT))


def corner_sym_offset(font_size: int) -> int:
    """Compute the vertical offset of the small symbol below the letter."""
    return round(font_size * SYM_Y_OFFSET_PCT)


def dominant_color(symbol: Image.Image) -> tuple:
    """Extract the dominant non-transparent color from a symbol image.
    
    Returns an RGBA tuple (r, g, b, 255).
    Falls back to black if no opaque pixels found.
    """
    img = symbol.convert("RGBA")
    data = np.array(img)
    # Only consider pixels with alpha > 128
    mask = data[:, :, 3] > 128
    if not mask.any():
        return (0, 0, 0, 255)
    
    opaque = data[mask][:, :3]  # RGB only
    avg = opaque.mean(axis=0).astype(int)
    return (int(avg[0]), int(avg[1]), int(avg[2]), 255)


def enforce_vertical_symmetry(img: Image.Image) -> Image.Image:
    """Enforce vertical (left-right) symmetry on a symbol image.
    
    Takes the left half of the image and mirrors it onto the right half.
    Blends a few pixels around the center for a seamless join.
    Preserves transparency.
    """
    img = img.convert("RGBA")
    w, h = img.size
    mid = w // 2
    
    # Take the left half (including center column)
    left_half = img.crop((0, 0, mid + 1, h))
    
    # Mirror it
    right_half = left_half.transpose(Image.FLIP_LEFT_RIGHT)
    
    # Start with original image
    result = img.copy()
    
    # Paste left half
    result.paste(left_half, (0, 0))
    
    # Paste mirrored right half (overlaps at center by 1px)
    result.paste(right_half, (mid, 0))
    
    # Blend a strip around the center (4px each side) for seamless join
    blend_width = min(4, mid)
    arr = np.array(result).astype(np.float64)
    for dx in range(blend_width):
        # Weight: 1.0 at edge, 0.0 at center
        t = dx / blend_width
        left_x = mid - 1 - dx
        right_x = mid + dx
        if left_x >= 0 and right_x < w:
            blended = arr[:, left_x] * (1 - t * 0.5) + arr[:, right_x] * (t * 0.5)
            blended_r = arr[:, right_x] * (1 - t * 0.5) + arr[:, left_x] * (t * 0.5)
            arr[:, left_x] = blended
            arr[:, right_x] = blended_r
    
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
