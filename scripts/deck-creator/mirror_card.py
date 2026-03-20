#!/usr/bin/env python3
"""
Card Assembly Script — Deck Creator
Takes a top-half card image, mirrors it with 180° rotation, 
stacks top + rotated bottom, and resizes to standard card dimensions.

Usage:
    python mirror_card.py <input_top_half> <output_card> [--width 400] [--height 738]

Example:
    python mirror_card.py top_king_hearts.png ../../images/decks/refn/king_of_hearts.png
"""

import argparse
from PIL import Image


def assemble_card(input_path, output_path, width=400, height=738):
    """
    1. Open the top-half image
    2. Crop to top 50%
    3. Rotate 180° to create bottom half
    4. Stack top + bottom
    5. Resize to target dimensions
    """
    img = Image.open(input_path)
    w, h = img.size

    # Crop top half
    top = img.crop((0, 0, w, h // 2))

    # Rotate 180° for bottom half
    bottom = top.rotate(180)

    # Stack
    full = Image.new("RGB", (w, h))
    full.paste(top, (0, 0))
    full.paste(bottom, (0, h // 2))

    # Resize to standard card dimensions
    full = full.resize((width, height), Image.LANCZOS)
    full.save(output_path)
    print(f"✅ Card assembled: {output_path} ({width}×{height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble a playing card from a top-half image")
    parser.add_argument("input", help="Path to the top-half image")
    parser.add_argument("output", help="Output path for the assembled card")
    parser.add_argument("--width", type=int, default=400, help="Card width (default: 400)")
    parser.add_argument("--height", type=int, default=738, help="Card height (default: 738)")
    args = parser.parse_args()
    assemble_card(args.input, args.output, args.width, args.height)
