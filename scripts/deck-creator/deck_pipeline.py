#!/usr/bin/env python3
"""
Deck Creator Pipeline — Full Tarot Deck Generation

Card types:
- 40 low-value simple cards (1-10 × 4 suits)
- 16 high-value face cards (V/C/D/R × 4 suits)
- 21 trumps (atouts)
- 1 excuse (joker)

PIPELINE RULES:
1. ALL simple cards (low + high value) share ONE background.
   Background asset = top-half only → mirrored for 180° rotational symmetry.
2. Face cards: single figure with TRANSPARENT background (complete character).
   Asset = top-half figure only → mirrored programmatically.
3. Excuse/joker asset = top-half figure only → mirrored programmatically.
4. Trump number ornaments at TOP and BOTTOM (Grimaud style), NOT center band.
5. Trump top & bottom illustrations: same size (each half card height).
6. Stack order for simple cards: background → symbols/figures → corners.
7. Low-value symbol directions: upward in top half, downward in bottom half,
   upward on the horizontal middle line.
8. AI PROMPT RULES for figure/excuse images:
   a. Always specify "plain solid color background" (white, black, or flat color).
      This ensures rembg can cleanly remove the background.
   b. All figures (V/C/D/R) and excuse must be HALF-LENGTH PORTRAITS:
      "half-length portrait, from the waist up, no legs visible, full head
      visible with space above, showing hands, centered".
   c. Knights (cavalier) must also show the horse head:
      "knight mounted on horse, half-length portrait showing rider from waist up
      with hands visible and horse head and neck, no legs visible, no hooves,
      full head visible with space above, plain solid color background, centered".
   d. Avoid textured, gradient, or scenic backgrounds — they cause artifacts.
   e. Do NOT use "close-up" or "zoomed in" — it crops too tight.
   f. The pipeline includes automatic leg detection (detect_legs) which warns
      if the bottom 30% of the figure has <30% fill (thin content = legs).
      If triggered, regenerate with a better prompt.

ASSET ORIENTATION (for imagine --orientation):
- Background top-half: square (card top is ~400×369, nearly 1:1)
- Face card figures: square (single character portrait)
- Trump illustrations: square
- Suit symbols: square"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont

try:
    from rembg import remove as remove_bg
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

# Card dimensions
DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 738

# Suits
SUITS = ["hearts", "diamonds", "clubs", "spades"]
SUIT_SYMBOLS = {
    "hearts": "♥", "diamonds": "♦",
    "clubs": "♣", "spades": "♠"
}
SUIT_COLORS = {
    "hearts": "red", "diamonds": "red",
    "clubs": "black", "spades": "black"
}

# Ranks
LOW_VALUES = list(range(1, 11))  # 1-10
HIGH_RANKS = {
    "valet": "V",
    "knight": "C",  # Cavalier
    "queen": "D",   # Dame
    "king": "R",    # Roi
}
TRUMP_COUNT = 21


FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
DEFAULT_FONT = os.path.join(FONT_DIR, "EBGaramond.ttf")
FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


class DeckCreator:
    def __init__(self, deck_name, card_width=DEFAULT_WIDTH, card_height=DEFAULT_HEIGHT,
                 font_path=None):
        self.deck_name = deck_name
        self.w = card_width
        self.h = card_height
        self.deck_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "images", "decks", deck_name
        )
        os.makedirs(self.deck_dir, exist_ok=True)
        # Font selection: custom > EB Garamond > DejaVu Serif > default
        self.font_path = font_path or DEFAULT_FONT
        if not os.path.exists(self.font_path):
            self.font_path = FALLBACK_FONT

    def _load_font(self, size):
        """Load the deck font at the given size."""
        try:
            return ImageFont.truetype(self.font_path, size)
        except (OSError, IOError):
            return ImageFont.load_default()

    # ─────────────────────────────────────────────
    # UTILITY: Remove background from AI-generated images
    # Used for figure cards and joker — imagine can't generate
    # transparent backgrounds natively, so we use rembg.
    # ─────────────────────────────────────────────

    @staticmethod
    def remove_background(input_path, output_path=None):
        """
        Remove background from an image, producing RGBA with transparency.
        Requires rembg (pip install rembg onnxruntime).
        
        Args:
            input_path: source image (any format)
            output_path: where to save (PNG). If None, overwrites input.
        
        Returns:
            PIL Image in RGBA mode
        """
        if not HAS_REMBG:
            raise ImportError("rembg not installed. Run: pip install rembg onnxruntime")
        
        img = Image.open(input_path).convert("RGBA")
        result = remove_bg(img)
        
        save_path = output_path or input_path
        # Ensure PNG extension for transparency
        if not save_path.lower().endswith('.png'):
            save_path = os.path.splitext(save_path)[0] + '.png'
        result.save(save_path)
        print(f"✅ Background removed: {save_path}")
        return result

    # ─────────────────────────────────────────────
    # STEP 1: Background assembly (top-half → mirror → full)
    # ONE background for ALL simple cards (low + high value)
    # Asset must be top-half only.
    # ─────────────────────────────────────────────

    def assemble_background(self, top_half_path, output_path):
        """
        Create a full card background from a TOP-HALF-ONLY image.
        The asset IS the top half — we mirror it 180° for the bottom.
        """
        top = Image.open(top_half_path).convert("RGBA")
        tw, th = top.size

        # The asset is the top half — resize to card width × half height
        top = top.resize((self.w, self.h // 2), Image.LANCZOS)
        bottom = top.rotate(180)

        full = Image.new("RGBA", (self.w, self.h))
        full.paste(top, (0, 0))
        full.paste(bottom, (0, self.h // 2))

        # Blend the seam (4px gradient at the middle)
        mid = self.h // 2
        blend_zone = 4
        for y in range(max(0, mid - blend_zone), min(self.h, mid + blend_zone)):
            alpha = (y - (mid - blend_zone)) / (2 * blend_zone)
            for x in range(self.w):
                top_px = top.getpixel((x, min(y, mid - 1)))
                bot_px = bottom.getpixel((x, max(y - mid, 0)))
                blended = tuple(int(top_px[c] * (1 - alpha) + bot_px[c] * alpha) for c in range(4))
                full.putpixel((x, y), blended)

        full.save(output_path)
        print(f"✅ Background assembled: {output_path}")
        return full

    # ─────────────────────────────────────────────
    # STEP 2: Low-value card assembly (1-10)
    #
    # Stack: background → suit symbols → corner numbers
    # Symbol directions: upward top half, downward bottom half,
    #                    upward on the middle horizontal line.
    # ─────────────────────────────────────────────

    def assemble_low_value(self, suit, value, background_path, symbol_path,
                           output_path):
        """
        Create a low-value card (1-10).
        Stack order: background → symbols → corners.
        """
        # Layer 1: Background
        card = Image.open(background_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)

        # Layer 2: Suit symbols at standard positions
        symbol = Image.open(symbol_path).convert("RGBA")
        center_size = int(self.w * 0.20)
        center_sym = symbol.resize((center_size, center_size), Image.LANCZOS)
        center_sym_down = center_sym.rotate(180)

        positions = self._get_symbol_positions(value, center_size)
        for x, y, direction in positions:
            # direction: "up" or "down"
            s = center_sym_down if direction == "down" else center_sym
            card.paste(s, (x, y), s)

        # Layer 3: Corner value + symbol
        corner_size = max(16, int(self.w * 0.07))
        corner_sym = symbol.resize((corner_size, corner_size), Image.LANCZOS)
        card = self._add_corners(card, str(value), corner_sym, suit)

        card.save(output_path)
        print(f"✅ {value} of {suit}: {output_path}")
        return card

    def _get_symbol_positions(self, value, sym_size):
        """
        Grimaud-standard French Tarot symbol positions for values 1-10.
        Returns list of (x, y, direction) where direction is "up" or "down".

        Layout reference: Standard Grimaud French playing cards.
        - Two columns (left/right) at ~27% from edges
        - Center column for odd extras
        - 180° rotational symmetry (top ↔ bottom)
        - Top half: "up", Bottom half: "down", Middle line: "up"

        Card proportions based on 400×738 (standard French Tarot ratio).
        All positions account for corner labels (~12% top/bottom margin).
        """
        cx = self.w // 2 - sym_size // 2
        # Two columns — Grimaud uses ~27% inset from card edge
        col_inset = int(self.w * 0.22)
        lx = col_inset - sym_size // 2
        rx = self.w - col_inset - sym_size // 2

        # Vertical rows — measured from Grimaud reference cards
        # Row positions as fraction of card height (from top edge)
        # Corner area ends at ~12%, playable area ~12%-88%
        r1 = int(self.h * 0.10)   # Row 1: top
        r2 = int(self.h * 0.23)   # Row 2: upper-mid
        r3 = int(self.h * 0.36)   # Row 3: upper-center
        mid = self.h // 2 - sym_size // 2  # Exact middle
        r5 = self.h - int(self.h * 0.36) - sym_size  # Row 5: lower-center (mirror r3)
        r6 = self.h - int(self.h * 0.23) - sym_size  # Row 6: lower-mid (mirror r2)
        r7 = self.h - int(self.h * 0.10) - sym_size  # Row 7: bottom (mirror r1)

        # Between rows for 7/8/10 extra symbols
        # r1_2 for 7/8: midpoint between r1 and mid
        r1_2_mid = (r1 + mid) // 2
        r6_7_mid = self.h - (r1 + mid) // 2 - sym_size

        # Evenly spaced 4 rows for 9/10 layouts
        gap_4 = (r7 - r1) // 3
        r_e2 = r1 + gap_4       # Even row 2
        r_e3 = r1 + 2 * gap_4   # Even row 3

        # Center extras: midpoint between nearest side rows
        r1_2 = (r1 + r_e2) // 2       # Between row 1 and row 2
        r6_7 = (r_e3 + r7) // 2       # Between row 3 and row 4

        layouts = {
            # Ace: single large centered symbol (handled by caller or here as regular)
            1: [(cx, mid, "up")],

            # 2: one top, one bottom (center column)
            2: [(cx, r1, "up"),
                (cx, r7, "down")],

            # 3: top, middle, bottom (center column)
            3: [(cx, r1, "up"),
                (cx, mid, "up"),
                (cx, r7, "down")],

            # 4: 2×2 grid
            4: [(lx, r1, "up"), (rx, r1, "up"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 5: 2×2 + center
            5: [(lx, r1, "up"), (rx, r1, "up"),
                (cx, mid, "up"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 6: 2×3 grid (three rows of two)
            6: [(lx, r1, "up"), (rx, r1, "up"),
                (lx, mid, "up"), (rx, mid, "up"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 7: like 6 but with one extra centered between r1 and mid
            7: [(lx, r1, "up"), (rx, r1, "up"),
                (cx, r1_2_mid, "up"),
                (lx, mid, "up"), (rx, mid, "up"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 8: like 6 but with two extras centered (one upper, one lower)
            8: [(lx, r1, "up"), (rx, r1, "up"),
                (cx, r1_2_mid, "up"),
                (lx, mid, "up"), (rx, mid, "up"),
                (cx, r6_7_mid, "down"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 9: 4 rows on sides (evenly spaced) + center
            9: [(lx, r1, "up"), (rx, r1, "up"),
                (lx, r_e2, "up"), (rx, r_e2, "up"),
                (cx, mid, "up"),
                (lx, r_e3, "down"), (rx, r_e3, "down"),
                (lx, r7, "down"), (rx, r7, "down")],

            # 10: like 9 but with two extras centered between row pairs
            10: [(lx, r1, "up"), (rx, r1, "up"),
                 (cx, r1_2, "up"),
                 (lx, r_e2, "up"), (rx, r_e2, "up"),
                 (lx, r_e3, "down"), (rx, r_e3, "down"),
                 (cx, r6_7, "down"),
                 (lx, r7, "down"), (rx, r7, "down")],
        }
        return layouts.get(value, [])

    # ─────────────────────────────────────────────
    # STEP 3: High-value face card assembly (V/C/D/R)
    #
    # Asset: single figure image with TRANSPARENT background.
    #        Asset is the TOP-HALF of the figure → mirrored for bottom.
    # Stack: background → figure (mirrored) → corner letters
    # Uses the SAME background as low-value cards.
    #
    # PROMPT RULE: When generating figure images with AI (imagine),
    # always specify "plain solid color background" so rembg can cleanly
    # remove it. All figures must be HALF-LENGTH PORTRAITS (waist up,
    # no legs). Knights must also show the horse head.
    # Avoid textured/gradient/scenic backgrounds — they cause artifacts.
    # ─────────────────────────────────────────────

    def assemble_high_value(self, suit, rank, figure_top_path,
                            background_path, output_path,
                            symbol_path=None):
        """
        Assemble a high-value face card.
        
        Args:
            figure_top_path: TOP-HALF of the figure (transparent bg).
                             This is a complete character from waist up —
                             NOT separate garment + head.
                             Mirrored 180° for the bottom half.
            background_path: shared background (same as low-value cards)
            output_path: where to save
            symbol_path: suit symbol image (optional; falls back to text)
        
        Stack: background → figure (mirrored) → corners
        """
        # Layer 1: Shared background
        card = Image.open(background_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)

        # Layer 2: Figure — auto-fit to card's top half
        # 
        # Pipeline: raw figure (any size) → crop to bounding box →
        # crop bottom until reaching a row where >45% is non-blank →
        # anchor to bottom of half-canvas → mirror → paste.
        # This guarantees halves touch at center with solid content.
        #
        raw_figure = Image.open(figure_top_path).convert("RGBA")
        
        # Step A: Crop to content bounding box (trim all transparent edges)
        content_bbox = raw_figure.getbbox()
        if content_bbox:
            raw_figure = raw_figure.crop(content_bbox)
        
        # Step A.5: Leg detection — if legs found, cut image in half
        has_legs, avg_fill = self.detect_legs(raw_figure)
        if has_legs:
            fw, fh = raw_figure.size
            raw_figure = raw_figure.crop((0, 0, fw, fh // 2))
            print(f"⚠️  Legs detected (bottom 30% fill: {avg_fill:.1%}). "
                  f"Cut image in half horizontally.")
        
        # Step B: Crop bottom — scan upward until finding a row where:
        #   1. >50% of pixels are non-blank, AND
        #   2. >40% of pixels are contiguously non-blank
        alpha = raw_figure.split()[3]
        fw, fh = raw_figure.size
        bottom_row = fh - 1
        for y in range(fh - 1, -1, -1):
            row_pixels = list(alpha.crop((0, y, fw, y + 1)).getdata())
            non_blank = sum(1 for p in row_pixels if p > 10) / fw
            # Check contiguous run
            max_run = 0
            current_run = 0
            for p in row_pixels:
                if p > 10:
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
            contiguous = max_run / fw
            if non_blank >= 0.50 and contiguous >= 0.40:
                bottom_row = y
                break
        raw_figure = raw_figure.crop((0, 0, fw, bottom_row + 1))
        
        fw, fh = raw_figure.size
        half_h = self.h // 2
        
        # Scale figure to FIT within the top-half canvas (preserve full figure)
        scale_w = self.w / fw
        scale_h = half_h / fh
        scale = min(scale_w, scale_h)  # fit, don't fill
        
        scaled_w = int(fw * scale)
        scaled_h = int(fh * scale)
        
        scaled_figure = raw_figure.resize((scaled_w, scaled_h), Image.LANCZOS)
        
        # Create top-half canvas and paste figure:
        # - horizontally centered
        # - anchored to BOTTOM of canvas (so it meets the mirror at center)
        top_canvas = Image.new("RGBA", (self.w, half_h), (0, 0, 0, 0))
        paste_x = (self.w - scaled_w) // 2
        paste_y = half_h - scaled_h  # anchor to bottom edge
        top_canvas.paste(scaled_figure, (paste_x, paste_y), scaled_figure)
        
        # Mirror for bottom half
        bottom_canvas = top_canvas.rotate(180)
        
        # Combine into full card figure
        full_figure = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        full_figure.paste(top_canvas, (0, 0))
        full_figure.paste(bottom_canvas, (0, half_h))
        
        card.paste(full_figure, (0, 0), full_figure)

        # Layer 3: Corner letter + suit (ON TOP of figure)
        letter = HIGH_RANKS[rank]
        if symbol_path:
            symbol = Image.open(symbol_path).convert("RGBA")
            card = self._add_corners_face(card, letter, symbol, suit)
        else:
            card = self._add_corners_text(card, letter, suit)

        card.save(output_path)
        print(f"✅ {rank} of {suit}: {output_path}")
        return card

    # ─────────────────────────────────────────────
    # STEP 4: Trump (atout) assembly
    #
    # Top and bottom illustrations: SAME SIZE.
    # Number ornaments at TOP and BOTTOM (Grimaud style),
    # NOT in a center band.
    # ─────────────────────────────────────────────

    def assemble_trump(self, number, top_image_path, bottom_image_path,
                       background_path, output_path):
        """
        Assemble a trump card.

        Layout (top to bottom):
        - Number zone: top strip (card_h - 2 * scene_h) / 2
        - Top scene: 3:2 landscape crop, scaled to card_w × scene_h
        - Bottom scene: 3:2 landscape crop, rotated 180°, meets top at center
        - Number zone: bottom strip (rotated 180°)

        Input images should be landscape (1440×810 from imagine).
        They are center-cropped to 3:2 ratio, then scaled to card width.
        If bottom_image_path is None, top scene is rotated 180° for bottom.
        """
        # Scene dimensions: 3:2 ratio → height = card_w / 1.5
        scene_h = int(self.w / 1.5)  # 400/1.5 = 267
        number_zone_h = (self.h - 2 * scene_h) // 2  # (738 - 534) / 2 = 102

        def crop_landscape_to_3_2(img_path):
            """Center-crop a landscape image to 3:2 ratio, scale to card width."""
            img = Image.open(img_path).convert("RGBA")
            iw, ih = img.size
            # Target 3:2 from the image
            target_w = int(ih * 1.5)
            if target_w <= iw:
                # Crop width (center)
                left = (iw - target_w) // 2
                img = img.crop((left, 0, left + target_w, ih))
            else:
                # Crop height (center)
                target_h = int(iw / 1.5)
                top = (ih - target_h) // 2
                img = img.crop((0, top, iw, top + target_h))
            # Scale to card width × scene height
            img = img.resize((self.w, scene_h), Image.LANCZOS)
            return img

        # Load and crop scenes
        top_scene = crop_landscape_to_3_2(top_image_path)
        if bottom_image_path:
            bottom_scene = crop_landscape_to_3_2(bottom_image_path)
            bottom_scene = bottom_scene.rotate(180)
        else:
            bottom_scene = top_scene.rotate(180)

        # Create canvas with background
        if background_path:
            canvas = Image.open(background_path).convert("RGBA").resize(
                (self.w, self.h), Image.LANCZOS)
        else:
            canvas = Image.new("RGBA", (self.w, self.h), (255, 255, 255, 255))

        # Place scenes — they meet at the center
        canvas.paste(top_scene, (0, number_zone_h), top_scene)
        canvas.paste(bottom_scene, (0, number_zone_h + scene_h), bottom_scene)

        # Add number text in the top and bottom zones
        canvas = self._add_trump_number_grimaud(canvas, number)

        canvas.save(output_path)
        print(f"✅ Trump {number}: {output_path}")
        return canvas

    # ─────────────────────────────────────────────
    # STEP 5: Excuse (joker) assembly
    #
    # Joker asset = TOP-HALF figure only → mirrored programmatically.
    # Uses shared background.
    # ─────────────────────────────────────────────

    def assemble_excuse(self, joker_top_half_path, background_path, output_path):
        """
        Assemble the Excuse (joker) card.
        Joker asset is the TOP-HALF figure — we mirror it for the bottom.
        Uses the shared background.

        Stack: background → joker figure (mirrored) → "EXCUSE" text
        """
        # Layer 1: Background
        card = Image.open(background_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)

        # Layer 2: Joker figure (asset IS the top half)
        raw_joker = Image.open(joker_top_half_path).convert("RGBA")
        
        # Step A: Crop to content bounding box
        content_bbox = raw_joker.getbbox()
        if content_bbox:
            raw_joker = raw_joker.crop(content_bbox)
        
        # Step A.5: Leg detection — if legs found, cut image in half
        has_legs, avg_fill = self.detect_legs(raw_joker)
        if has_legs:
            jw, jh = raw_joker.size
            raw_joker = raw_joker.crop((0, 0, jw, jh // 2))
            print(f"⚠️  Legs detected on excuse figure (bottom 30% fill: {avg_fill:.1%}). "
                  f"Cut image in half horizontally.")
        
        # Step B: Crop bottom — scan upward until finding a row where:
        #   1. >50% of pixels are non-blank, AND
        #   2. >40% of pixels are contiguously non-blank
        alpha = raw_joker.split()[3]
        jw, jh = raw_joker.size
        bottom_row = jh - 1
        for y in range(jh - 1, -1, -1):
            row_pixels = list(alpha.crop((0, y, jw, y + 1)).getdata())
            non_blank = sum(1 for p in row_pixels if p > 10) / jw
            max_run = 0
            current_run = 0
            for p in row_pixels:
                if p > 10:
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
            contiguous = max_run / jw
            if non_blank >= 0.50 and contiguous >= 0.40:
                bottom_row = y
                break
        raw_joker = raw_joker.crop((0, 0, jw, bottom_row + 1))
        
        jw, jh = raw_joker.size
        half_h = self.h // 2
        
        # Scale to fit top half
        scale_w = self.w / jw
        scale_h = half_h / jh
        scale = min(scale_w, scale_h)
        scaled_w = int(jw * scale)
        scaled_h = int(jh * scale)
        scaled_joker = raw_joker.resize((scaled_w, scaled_h), Image.LANCZOS)
        
        # Create top-half canvas, anchored to bottom so halves touch
        top_canvas = Image.new("RGBA", (self.w, half_h), (0, 0, 0, 0))
        paste_x = (self.w - scaled_w) // 2
        paste_y = half_h - scaled_h
        top_canvas.paste(scaled_joker, (paste_x, paste_y), scaled_joker)
        
        # Mirror for bottom half
        bottom_canvas = top_canvas.rotate(180)
        
        # Combine
        full_joker = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        full_joker.paste(top_canvas, (0, 0))
        full_joker.paste(bottom_canvas, (0, half_h))
        
        card.paste(full_joker, (0, 0), full_joker)

        # Layer 3: "EXCUSE" text (on top of everything)
        card = self._add_excuse_text(card)

        card.save(output_path)
        print(f"✅ Excuse: {output_path}")
        return card

    # ─────────────────────────────────────────────
    # Helper: Detect if figure likely has legs
    # ─────────────────────────────────────────────

    @staticmethod
    def detect_legs(img_rgba):
        """
        Heuristic leg detection on a transparent-bg figure.
        
        Two checks:
        1. Bottom 30% fill < 40% (thin content = legs)
        2. Aspect ratio: if height > 1.2 * width after bbox crop,
           the figure is likely full-body (half-length should be ~square)
        
        Returns: (has_legs: bool, avg_fill: float)
        """
        alpha = img_rgba.split()[3]
        fw, fh = img_rgba.size
        
        # Check 1: bottom fill
        start_y = int(fh * 0.7)
        total_fill = 0.0
        rows = 0
        for y in range(start_y, fh):
            row_pixels = list(alpha.crop((0, y, fw, y + 1)).getdata())
            total_fill += sum(1 for p in row_pixels if p > 10) / fw
            rows += 1
        avg_fill = total_fill / max(rows, 1)
        
        # Check 2: aspect ratio (full-body figures are tall and narrow)
        too_tall = fh > fw * 1.2
        
        has_legs = avg_fill < 0.40 or too_tall
        return has_legs, avg_fill

    # ─────────────────────────────────────────────
    # Helper: Add corner text (value + suit symbol image)
    # ─────────────────────────────────────────────

    def _add_corners(self, img, value_text, symbol_img, suit):
        """Add value text and suit symbol to top-left and bottom-right corners."""
        draw = ImageDraw.Draw(img)
        color = SUIT_COLORS[suit]
        font_color = (200, 0, 0, 255) if color == "red" else (0, 0, 0, 255)

        font_size = max(16, int(self.w * 0.10))
        font = self._load_font(font_size)
        stroke_w = max(1, int(self.w * 0.003))

        margin = max(6, int(self.w * 0.03))
        sym_w = symbol_img.width

        # Measure text width for centering
        bbox = draw.textbbox((0, 0), value_text, font=font, stroke_width=stroke_w)
        tw = bbox[2] - bbox[0]

        # Center axis = middle of the symbol
        center_x = margin + sym_w // 2
        text_x = center_x - tw // 2
        sym_x = margin

        sym_offset = int(font_size * 1.15)
        # Top-left: value centered over symbol
        draw.text((text_x, margin), value_text, fill=font_color, font=font,
                  stroke_width=stroke_w, stroke_fill=font_color)
        # Top-left: suit symbol below value
        img.paste(symbol_img, (sym_x, margin + sym_offset), symbol_img)

        # Bottom-right: rotated
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((text_x, margin), value_text, fill=font_color, font=font,
                       stroke_width=stroke_w, stroke_fill=font_color)
        temp.paste(symbol_img, (sym_x, margin + sym_offset), symbol_img)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_corners_face(self, img, letter, symbol_img, suit):
        """Add face card corner: letter + suit symbol side by side.
        Symbol is 110% of font size, slightly cropped, placed next to the letter.
        Letter is positioned a bit lower than simple card corners."""
        draw = ImageDraw.Draw(img)
        color = SUIT_COLORS[suit]
        font_color = (200, 0, 0, 255) if color == "red" else (0, 0, 0, 255)

        font_size = max(14, int(self.w * 0.09))
        font = self._load_font(font_size)
        stroke_w = max(1, int(self.w * 0.003))

        margin = max(6, int(self.w * 0.03))
        top_margin = int(margin * 1.8)  # a bit lower

        # Symbol: 250% of font size, crop 10% from edges
        sym_size = int(font_size * 2.5)
        sym = symbol_img.resize((sym_size, sym_size), Image.LANCZOS)
        sym_cropped = sym

        # Measure letter dimensions
        bbox = draw.textbbox((0, 0), letter, font=font, stroke_width=stroke_w)
        tw = bbox[2] - bbox[0]
        t_top = bbox[1]  # actual top of rendered glyph (can be negative)

        # Letter then symbol side by side
        # Align symbol top with the actual top of the rendered letter
        gap = -tw // 2  # symbol starts at horizontal middle of the letter
        sym_y = top_margin + t_top

        # Crop left edge of symbol so it doesn't cover the letter
        overlap = tw // 2
        sym_cropped = sym_cropped.crop((overlap, 0, sym_cropped.width, sym_cropped.height))

        # Paste position: symbol left edge = letter right edge (margin + tw)
        sym_paste_x = margin + tw

        # Small corner symbol below letter (same as simple cards)
        corner_size = max(16, int(self.w * 0.07))
        corner_sym = symbol_img.resize((corner_size, corner_size), Image.LANCZOS)
        sym_offset = int(font_size * 1.15)
        # Center corner symbol under the letter
        corner_x = margin + tw // 2 - corner_size // 2

        # Top-right: letter + symbol (mirrored horizontally)
        tr_letter_x = self.w - margin - tw
        tr_corner_x = self.w - margin - tw // 2 - corner_size // 2

        # Top-left
        draw.text((margin, top_margin), letter, fill=font_color, font=font,
                  stroke_width=stroke_w, stroke_fill=font_color)
        img.paste(sym_cropped, (sym_paste_x, sym_y), sym_cropped)
        img.paste(corner_sym, (corner_x, top_margin + sym_offset), corner_sym)

        # Top-right
        draw.text((tr_letter_x, top_margin), letter, fill=font_color, font=font,
                  stroke_width=stroke_w, stroke_fill=font_color)
        img.paste(corner_sym, (tr_corner_x, top_margin + sym_offset), corner_sym)

        # Bottom-left + bottom-right via rotation of top-right + top-left
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        # Mirror of top-left → bottom-right
        temp_draw.text((margin, top_margin), letter, fill=font_color, font=font,
                       stroke_width=stroke_w, stroke_fill=font_color)
        temp.paste(sym_cropped, (sym_paste_x, sym_y), sym_cropped)
        temp.paste(corner_sym, (corner_x, top_margin + sym_offset), corner_sym)
        # Mirror of top-right → bottom-left
        temp_draw.text((tr_letter_x, top_margin), letter, fill=font_color, font=font,
                       stroke_width=stroke_w, stroke_fill=font_color)
        temp.paste(corner_sym, (tr_corner_x, top_margin + sym_offset), corner_sym)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_corners_text(self, img, letter, suit):
        """Add letter (V/C/D/R) and suit symbol text to corners."""
        draw = ImageDraw.Draw(img)
        color = SUIT_COLORS[suit]
        font_color = (200, 0, 0, 255) if color == "red" else (0, 0, 0, 255)
        symbol = SUIT_SYMBOLS[suit]

        font_size = max(14, int(self.w * 0.09))
        sym_font_size = max(12, int(self.w * 0.07))
        font = self._load_font(font_size)
        sym_font = self._load_font(sym_font_size)
        stroke_w = max(1, int(self.w * 0.003))

        margin = max(6, int(self.w * 0.03))

        # Measure widths for centering
        bbox_letter = draw.textbbox((0, 0), letter, font=font, stroke_width=stroke_w)
        lw = bbox_letter[2] - bbox_letter[0]
        bbox_sym = draw.textbbox((0, 0), symbol, font=sym_font, stroke_width=stroke_w)
        sw = bbox_sym[2] - bbox_sym[0]
        max_w = max(lw, sw)
        center_x = margin + max_w // 2

        sym_offset = int(font_size * 1.15)
        # Top-left (centered)
        draw.text((center_x - lw // 2, margin), letter, fill=font_color, font=font,
                  stroke_width=stroke_w, stroke_fill=font_color)
        draw.text((center_x - sw // 2, margin + sym_offset), symbol, fill=font_color, font=sym_font,
                  stroke_width=stroke_w, stroke_fill=font_color)

        # Bottom-right (rotated)
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((center_x - lw // 2, margin), letter, fill=font_color, font=font,
                       stroke_width=stroke_w, stroke_fill=font_color)
        temp_draw.text((center_x - sw // 2, margin + sym_offset), symbol, fill=font_color, font=sym_font,
                       stroke_width=stroke_w, stroke_fill=font_color)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_trump_number_grimaud(self, img, number):
        """Add trump number in all 4 corners of the number zones."""
        draw = ImageDraw.Draw(img)
        font_size = max(18, int(self.h * 0.11))
        font = self._load_font(font_size)
        stroke_w = max(1, int(self.w * 0.003))
        margin = max(4, int(self.w * 0.06))

        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        # Adjust for font ascent offset
        t_top = bbox[1]

        # Number zone height
        scene_h = int(self.w / 1.5)
        number_zone_h = (self.h - 2 * scene_h) // 2

        # Vertical center within number zone
        ty = (number_zone_h - th) // 2 - t_top

        # Top-left
        draw.text((margin, ty), text, fill=(0, 0, 0, 255), font=font,
                  stroke_width=stroke_w, stroke_fill=(0, 0, 0, 255))

        # Top-right
        draw.text((self.w - margin - tw, ty), text, fill=(0, 0, 0, 255), font=font,
                  stroke_width=stroke_w, stroke_fill=(0, 0, 0, 255))

        # Bottom-left and bottom-right (rotated 180° for symmetry)
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((margin, ty), text, fill=(0, 0, 0, 255), font=font,
                       stroke_width=stroke_w, stroke_fill=(0, 0, 0, 255))
        temp_draw.text((self.w - margin - tw, ty), text, fill=(0, 0, 0, 255), font=font,
                       stroke_width=stroke_w, stroke_fill=(0, 0, 0, 255))
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_excuse_text(self, img):
        """Add five-pointed stars in all 4 corners of the excuse card.
        Star color contrasts with the dominant background color."""
        import math
        from collections import Counter

        # Detect dominant background color from corner regions
        rgb_img = img.convert("RGB")
        corner_size = int(self.w * 0.15)
        corner_pixels = []
        for region in [
            (0, 0, corner_size, corner_size),
            (self.w - corner_size, 0, self.w, corner_size),
            (0, self.h - corner_size, corner_size, self.h),
            (self.w - corner_size, self.h - corner_size, self.w, self.h),
        ]:
            crop = rgb_img.crop(region)
            # Quantize to reduce unique colors
            for px in crop.getdata():
                q = (px[0] // 32 * 32, px[1] // 32 * 32, px[2] // 32 * 32)
                corner_pixels.append(q)

        dominant = Counter(corner_pixels).most_common(1)[0][0]
        # Compute contrasting color: invert the dominant and boost saturation
        # Convert to HSL, rotate hue by 180°, maximize saturation
        r, g, b = dominant
        # Simple high-contrast: invert each channel
        inv_r, inv_g, inv_b = 255 - r, 255 - g, 255 - b
        # If inverted is too close to mid-gray, push toward gold or white
        inv_lum = 0.299 * inv_r + 0.587 * inv_g + 0.114 * inv_b
        if 80 < inv_lum < 175:
            # Too muddy — push to extremes
            if inv_lum >= 128:
                inv_r, inv_g, inv_b = min(255, inv_r + 80), min(255, inv_g + 60), max(0, inv_b - 40)
            else:
                inv_r, inv_g, inv_b = max(0, inv_r - 60), max(0, inv_g - 60), min(255, inv_b + 80)
        star_color = (inv_r, inv_g, inv_b, 255)

        # Star parameters
        star_size = int(self.w * 0.05)  # radius of outer points
        margin_x = int(self.w * 0.04)
        margin_y = int(self.h * 0.02)

        def star_polygon(cx, cy, r_outer, r_inner, n_points=5, point_angle=None):
            """Generate vertices for an n-pointed star.
            point_angle: absolute angle (radians, math convention) where
                         the first outer point should be placed."""
            base = point_angle if point_angle is not None else math.pi / 2
            points = []
            for i in range(n_points * 2):
                r = r_outer if i % 2 == 0 else r_inner
                angle = base + i * math.pi / n_points
                points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
            return points

        r_inner = int(star_size * 0.38)

        # Compute exact angle from each star center to its nearest corner
        tl_cx = margin_x + star_size
        tl_cy = margin_y + star_size
        tr_cx = self.w - margin_x - star_size
        tr_cy = margin_y + star_size

        # Angle from star center to corner (math convention: y-up)
        # Top-left star → corner (0, 0): dx negative, screen dy negative = math dy positive
        tl_angle = math.atan2(tl_cy, -tl_cx)  # toward (0,0) in screen = up-left in math
        # Top-right star → corner (w, 0): dx positive, screen dy negative = math dy positive
        tr_angle = math.atan2(tr_cy, self.w - tr_cx)

        # Draw stars on top-left and top-right
        draw = ImageDraw.Draw(img)
        draw.polygon(star_polygon(tl_cx, tl_cy, star_size, r_inner, point_angle=tl_angle), fill=star_color)
        draw.polygon(star_polygon(tr_cx, tr_cy, star_size, r_inner, point_angle=tr_angle), fill=star_color)

        # Bottom stars via 180° rotation (automatically points toward bottom corners)
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.polygon(star_polygon(tl_cx, tl_cy, star_size, r_inner, point_angle=tl_angle), fill=star_color)
        temp_draw.polygon(star_polygon(tr_cx, tr_cy, star_size, r_inner, point_angle=tr_angle), fill=star_color)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    # ─────────────────────────────────────────────
    # Convenience: card filename
    # ─────────────────────────────────────────────

    def card_filename(self, card_type, suit=None, value=None, number=None):
        """Generate standard card filename."""
        if card_type == "low":
            return f"{value}_of_{suit}.png"
        elif card_type == "high":
            rank_names = {"V": "jack", "C": "knight", "D": "queen", "R": "king"}
            return f"{rank_names.get(value, value)}_of_{suit}.png"
        elif card_type == "trump":
            return f"trump_{number:02d}.png"
        elif card_type == "excuse":
            return "excuse.png"
        return "unknown.png"

    def output_path(self, filename):
        """Get full output path for a card in this deck."""
        return os.path.join(self.deck_dir, filename)


# ─────────────────────────────────────────────
# CLI interface
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deck Creator Pipeline")
    sub = parser.add_subparsers(dest="command")

    # background
    bg_parser = sub.add_parser("background", help="Assemble background from top-half asset")
    bg_parser.add_argument("deck", help="Deck name")
    bg_parser.add_argument("input", help="Top-half image (the asset IS the top half)")
    bg_parser.add_argument("output", help="Output path")

    # low-value
    low_parser = sub.add_parser("low", help="Assemble low-value card (1-10)")
    low_parser.add_argument("deck", help="Deck name")
    low_parser.add_argument("suit", choices=SUITS)
    low_parser.add_argument("value", type=int, choices=range(1, 11))
    low_parser.add_argument("background", help="Full background image (already assembled)")
    low_parser.add_argument("symbol", help="Suit symbol image (PNG, transparent bg)")
    low_parser.add_argument("output", help="Output path")

    # high-value
    high_parser = sub.add_parser("high", help="Assemble face card (V/C/D/R)")
    high_parser.add_argument("deck", help="Deck name")
    high_parser.add_argument("suit", choices=SUITS)
    high_parser.add_argument("rank", choices=list(HIGH_RANKS.keys()))
    high_parser.add_argument("figure", help="Top-half figure image (transparent bg, complete character)")
    high_parser.add_argument("background", help="Full background image (same as low-value)")
    high_parser.add_argument("output", help="Output path")

    # trump
    trump_parser = sub.add_parser("trump", help="Assemble trump card")
    trump_parser.add_argument("deck", help="Deck name")
    trump_parser.add_argument("number", type=int, choices=range(1, 22))
    trump_parser.add_argument("top", help="Top illustration (same size as bottom)")
    trump_parser.add_argument("--bottom", help="Bottom illustration (mirrors top if omitted)")
    trump_parser.add_argument("--ornament", help="Number ornament band")
    trump_parser.add_argument("output", help="Output path")

    # remove-bg
    rembg_parser = sub.add_parser("remove-bg", help="Remove background from an image (for figures/joker)")
    rembg_parser.add_argument("input", help="Input image")
    rembg_parser.add_argument("output", help="Output PNG with transparent background")

    # excuse
    exc_parser = sub.add_parser("excuse", help="Assemble excuse (joker) card")
    exc_parser.add_argument("deck", help="Deck name")
    exc_parser.add_argument("joker", help="Joker TOP-HALF figure (asset is top half only)")
    exc_parser.add_argument("background", help="Full background image")
    exc_parser.add_argument("output", help="Output path")

    args = parser.parse_args()

    if args.command:
        dc = DeckCreator(args.deck if hasattr(args, 'deck') else 'temp')
        if args.command == "remove-bg":
            dc.remove_background(args.input, args.output)
        elif args.command == "background":
            dc.assemble_background(args.input, args.output)
        elif args.command == "low":
            dc.assemble_low_value(args.suit, args.value, args.background,
                                  args.symbol, args.output)
        elif args.command == "high":
            dc.assemble_high_value(args.suit, args.rank, args.figure,
                                   args.background, args.output)
        elif args.command == "trump":
            dc.assemble_trump(args.number, args.top, args.bottom,
                              args.ornament, args.output)
        elif args.command == "excuse":
            dc.assemble_excuse(args.joker, args.background, args.output)
    else:
        parser.print_help()
