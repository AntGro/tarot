"""
simple_card_pipeline.py — Low-value card renderer (1–10).

This is a 1:1 Python translation of the card-parameter-tuner artifact's
Canvas rendering logic.  Every variable name, computation order, and
rounding strategy matches the JS source so that a card rendered here at
W×H is pixel-identical (modulo font rasteriser differences) to the
artifact at W×H.

Usage:
    from simple_card_pipeline import render_simple_card
    render_simple_card(
        value=7,
        suit="hearts",
        symbol_path="path/to/heart.png",
        background_path="path/to/bg.png",   # or None for white
        output_path="seven_of_hearts.png",
        card_w=400, card_h=738,
        font_path="fonts/Newston Regular.ttf",
    )
"""

from __future__ import annotations
import math, os
from PIL import Image, ImageDraw, ImageFont

# ── Suit metadata ────────────────────────────────────────────
SUIT_COLORS = {
    "hearts": "red", "diamonds": "red",
    "spades": "black", "clubs": "black",
}

# ── Default parameters (from the tuner export) ──────────────
# All *_pct values are percentages; reference canvas is 200×369.
PARAMS = dict(
    corner_x_pct=3,
    corner_y_pct=5.5,
    font_size_pct=20,
    small_sym_pct=9.5,
    sym_y_offset_pct_fs=81,
    main_sym_pct=25,
    top_row_y_pct=10,
    col_inset_pct=5.5,
    letter_spacing_px=0.5,   # at 200w reference
    crop_pad_px=5,           # at 200w reference
)

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
DEFAULT_FONT = os.path.join(FONT_DIR, "Newston Regular.ttf")

# ── Helpers ──────────────────────────────────────────────────

def _px(pct: float, base: int) -> int:
    """Percentage → pixel, matching JS Math.round."""
    return round(base * pct / 100)


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _measure_text_spaced(draw, text, font, stroke_w, spacing):
    """Total pixel width of *text* rendered char-by-char with *spacing*."""
    total = 0
    for i, ch in enumerate(text):
        bbox = draw.textbbox((0, 0), ch, font=font, stroke_width=stroke_w)
        total += (bbox[2] - bbox[0])
        if i < len(text) - 1:
            total += spacing
    return total


def _draw_text_spaced(draw, pos, text, font, color, stroke_w, spacing):
    """Render *text* char-by-char with custom *spacing*."""
    x, y = pos
    for i, ch in enumerate(text):
        draw.text((x, y), ch, fill=color, font=font,
                  stroke_width=stroke_w, stroke_fill=color)
        bbox = draw.textbbox((0, 0), ch, font=font, stroke_width=stroke_w)
        x += (bbox[2] - bbox[0])
        if i < len(text) - 1:
            x += spacing


# ── Layout (mirrors JS getLayout exactly) ───────────────────

def _get_layout(value: int, W: int, H: int, p: dict):
    """Return symbol positions + derived metrics.

    Every line mirrors the artifact's getLayout() function.
    """
    sym   = _px(p["main_sym_pct"], W)
    margin  = _px(p["corner_x_pct"], W)
    marginY = _px(p["corner_y_pct"], W)      # note: pct of W, not H
    fs      = _px(p["font_size_pct"], W)
    smallS  = _px(p["small_sym_pct"], W)
    symOff  = round(fs * p["sym_y_offset_pct_fs"] / 100)
    cornerBottom = marginY + symOff + smallS

    if p["top_row_y_pct"] == 0:
        numBottom = marginY + round(fs * 0.75)
        symTop = marginY + symOff
        r1_center = round((numBottom + symTop) / 2)
    else:
        r1_center = _px(p["top_row_y_pct"], H)

    r1  = r1_center - math.floor(sym / 2)
    r7  = H - r1 - sym
    mid = math.floor(H / 2 - sym / 2)

    cLeft   = _px(p["col_inset_pct"], W)
    cRight  = W - _px(p["col_inset_pct"], W) - sym
    cCenter = math.floor(W / 2 - sym / 2)

    # positions: list of (x, y, up:bool)
    if value == 1:
        positions = [(cCenter, mid, True)]
    elif value == 2:
        positions = [(cCenter, r1, True), (cCenter, r7, False)]
    elif value == 3:
        positions = [(cCenter, r1, True), (cCenter, mid, True),
                     (cCenter, r7, False)]
    elif value == 4:
        positions = [(cLeft, r1, True), (cRight, r1, True),
                     (cLeft, r7, False), (cRight, r7, False)]
    elif value == 5:
        positions = [(cLeft, r1, True), (cRight, r1, True),
                     (cCenter, mid, True),
                     (cLeft, r7, False), (cRight, r7, False)]
    elif value == 6:
        positions = [(cLeft, r1, True), (cRight, r1, True),
                     (cLeft, mid, True), (cRight, mid, True),
                     (cLeft, r7, False), (cRight, r7, False)]
    elif value == 7:
        r12 = round((r1 + mid) / 2)
        positions = [(cLeft, r1, True), (cRight, r1, True),
                     (cLeft, mid, True), (cRight, mid, True),
                     (cLeft, r7, False), (cRight, r7, False),
                     (cCenter, r12, True)]
    elif value == 8:
        r12 = round((r1 + mid) / 2)
        r67 = H - r12 - sym
        positions = [(cLeft, r1, True), (cRight, r1, True),
                     (cLeft, mid, True), (cRight, mid, True),
                     (cLeft, r7, False), (cRight, r7, False),
                     (cCenter, r12, True), (cCenter, r67, False)]
    elif value == 9:
        sp = (r7 - r1) / 3
        re = [round(r1 + i * sp) for i in range(3)] + [r7]
        positions = []
        for i in range(4):
            up = re[i] + sym / 2 < H / 2
            positions.append((cLeft, re[i], up))
            positions.append((cRight, re[i], up))
        positions.append((cCenter, mid, True))
    elif value == 10:
        sp = (r7 - r1) / 3
        re = [round(r1 + i * sp) for i in range(3)] + [r7]
        positions = []
        for i in range(4):
            up = re[i] + sym / 2 < H / 2
            positions.append((cLeft, re[i], up))
            positions.append((cRight, re[i], up))
        r12mid = round((re[0] + re[1]) / 2)
        r67mid = H - r12mid - sym
        positions.append((cCenter, r12mid, True))
        positions.append((cCenter, r67mid, False))
    else:
        positions = []

    return dict(
        positions=positions, sym=sym,
        margin=margin, marginY=marginY,
        fs=fs, smallS=smallS, symOff=symOff,
        cornerBottom=cornerBottom,
        cLeft=cLeft, cRight=cRight,
    )


# ── Corner rendering (mirrors JS drawCorners / drawOneCorner) ──

def _draw_corners(card: Image.Image, value: int, suit: str,
                  symbol_img: Image.Image, font_path: str,
                  W: int, H: int, p: dict):
    """Draw number + small suit symbol in all 4 corners."""
    draw = ImageDraw.Draw(card)
    font_color = (220, 20, 60, 255) if SUIT_COLORS[suit] == "red" else (0, 0, 0, 255)

    margin  = _px(p["corner_x_pct"], W)
    marginY = _px(p["corner_y_pct"], W)
    fs      = _px(p["font_size_pct"], W)
    smallS  = _px(p["small_sym_pct"], W)
    symOff  = round(fs * p["sym_y_offset_pct_fs"] / 100)
    spacing = round(W * p["letter_spacing_px"] / 200)
    stroke_w = max(1, int(W * 0.003))

    font = _load_font(font_path, fs)
    text = "A" if value == 1 else str(value)

    # Measure text width (with letter spacing)
    tw = _measure_text_spaced(draw, text, font, stroke_w, spacing)

    # Small corner symbol
    small_heart = symbol_img.resize((smallS, smallS), Image.LANCZOS)

    # Build corner on a temp image (matches JS tmp canvas)
    cw = math.ceil(max(tw, smallS) + 4)
    ch = math.ceil(symOff + smallS + 4)
    tmp = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp)

    # Number centered horizontally
    textX = round((cw - tw) / 2)
    _draw_text_spaced(tmp_draw, (textX, 0), text, font,
                      font_color, stroke_w, spacing)

    # Small heart centered below number
    shx = round(textX + tw / 2 - smallS / 2)
    tmp.paste(small_heart, (shx, symOff), small_heart)

    # Rotated version for bottom corners
    rot = tmp.rotate(180)

    # Paste corners — exact same positions as JS:
    # Top-left
    card.paste(tmp, (margin, marginY), tmp)
    # Top-right
    card.paste(tmp, (W - margin - cw, marginY), tmp)
    # Bottom-right (180° of top-left)
    card.paste(rot, (W - margin - cw, H - marginY - ch), rot)
    # Bottom-left (180° of top-right)
    card.paste(rot, (margin, H - marginY - ch), rot)

    return card


# ── Main suit symbols with cropping (mirrors JS drawCard) ────

def _draw_symbols(card: Image.Image, positions, suit: str,
                  symbol_img: Image.Image, font_path: str,
                  W: int, H: int, p: dict):
    """Paste suit symbols at positions, with corner-zone cropping."""
    layout = _get_layout(1, W, H, p)  # just to get derived metrics
    sym      = layout["sym"]
    margin   = layout["margin"]
    marginY  = layout["marginY"]
    fs       = layout["fs"]
    smallS   = layout["smallS"]
    symOff   = layout["symOff"]
    cornerBottom = layout["cornerBottom"]
    cLeft    = layout["cLeft"]
    cRight   = layout["cRight"]

    spacing  = round(W * p["letter_spacing_px"] / 200)
    crop_pad = round(W * p["crop_pad_px"] / 200)
    stroke_w = max(1, int(W * 0.003))
    font     = _load_font(font_path, fs)
    draw     = ImageDraw.Draw(card)

    # Corner zone width (matches JS: margin + max(numTw, numTw/2 + smallS/2) + cropPad)
    numTw = _measure_text_spaced(draw, "10", font, stroke_w, spacing)
    cornerZoneW = margin + max(numTw, numTw // 2 + smallS // 2) + crop_pad
    cornerZoneR = W - cornerZoneW

    # Pre-render symbols
    center_sym = symbol_img.resize((sym, sym), Image.LANCZOS)
    center_sym_down = center_sym.rotate(180)

    for x, y, up in positions:
        s = center_sym if up else center_sym_down

        clipX = 0
        clipW = sym
        drawX = x

        symBottom = y + sym
        overlapTop = (y < cornerBottom and symBottom > marginY)
        overlapBot = (symBottom > (H - cornerBottom) and y < (H - marginY))

        # Left column near corner: crop LEFT side
        if x <= cLeft and (overlapTop or overlapBot) and x < cornerZoneW:
            ov = cornerZoneW - x
            if 0 < ov < sym:
                clipX = ov
                clipW = sym - ov
                drawX = cornerZoneW

        # Right column near corner: crop RIGHT side
        if x >= cRight and (overlapTop or overlapBot) and (x + sym) > cornerZoneR:
            ov = (x + sym) - cornerZoneR
            if 0 < ov < sym:
                clipW = sym - ov

        if clipW <= 0:
            continue

        # Crop the symbol image
        cropped = s.crop((clipX, 0, clipX + clipW, sym))
        card.paste(cropped, (drawX, y), cropped)

    return card


# ── Public API ───────────────────────────────────────────────

def render_simple_card(
    value: int,
    suit: str,
    symbol_path: str,
    output_path: str,
    background_path: str | None = None,
    card_w: int = 400,
    card_h: int = 738,
    font_path: str = DEFAULT_FONT,
    params: dict | None = None,
):
    """Render a simple card (1-10) and save to *output_path*.

    Parameters mirror the tuner artifact exactly.
    """
    p = {**PARAMS, **(params or {})}
    W, H = card_w, card_h

    # Layer 0: background (or white)
    if background_path:
        card = Image.open(background_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        card = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # Load symbol
    symbol = Image.open(symbol_path).convert("RGBA")

    # Layer 1: suit symbols at layout positions
    layout = _get_layout(value, W, H, p)
    card = _draw_symbols(card, layout["positions"], suit, symbol,
                         font_path, W, H, p)

    # Layer 2: corner numbers + small symbols
    card = _draw_corners(card, value, suit, symbol, font_path, W, H, p)

    card.save(output_path)
    print(f"✅ {value} of {suit}: {output_path}")
    return card
