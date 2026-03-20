#!/usr/bin/env python3
"""
Deck Creator Pipeline — Full Tarot Deck Generation

Provides functions for each step of creating a complete 78-card Tarot deck:
- 40 low-value simple cards (1-10 × 4 suits)
- 16 high-value simple cards (V/C/D/R × 4 suits)
- 21 trumps (atouts)
- 1 excuse (joker)

Usage:
    from deck_pipeline import DeckCreator
    dc = DeckCreator(deck_name="refn", card_width=400, card_height=738)
    
    # Step 1: Design border
    dc.apply_border(card_image, border_image)
    
    # Step 2: Simple card backgrounds
    dc.assemble_background(top_half_bg)
    
    # Step 3: Place symbols on low-value cards
    dc.assemble_low_value(suit, value, background, symbol, border)
    
    # Step 4: Assemble high-value cards
    dc.assemble_high_value(suit, rank, garment, head, letter_symbol, border)
    
    # Step 5: Assemble trumps
    dc.assemble_trump(number, top_image, bottom_image, number_ornament, border)
    
    # Step 6: Assemble excuse
    dc.assemble_excuse(joker_image, background, border)
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont

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


class DeckCreator:
    def __init__(self, deck_name, card_width=DEFAULT_WIDTH, card_height=DEFAULT_HEIGHT):
        self.deck_name = deck_name
        self.w = card_width
        self.h = card_height
        self.deck_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "images", "decks", deck_name
        )
        os.makedirs(self.deck_dir, exist_ok=True)

    # ─────────────────────────────────────────────
    # STEP 1: Border overlay
    # ─────────────────────────────────────────────

    def apply_border(self, card_img_path, border_img_path, output_path):
        """
        Overlay a border frame (PNG with transparent center) onto a card image.
        Border image must be same dimensions as card (w × h).
        """
        card = Image.open(card_img_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
        border = Image.open(border_img_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
        result = Image.alpha_composite(card, border)
        result.save(output_path)
        print(f"✅ Border applied: {output_path}")
        return result

    # ─────────────────────────────────────────────
    # STEP 2: Background assembly (top → mirror → full)
    # ─────────────────────────────────────────────

    def assemble_background(self, top_half_path, output_path):
        """
        Create a full card background from a top-half image.
        Crops to top 50%, rotates 180°, stacks with smooth middle transition.
        """
        img = Image.open(top_half_path).convert("RGBA")
        w, h = img.size
        mid = h // 2

        top = img.crop((0, 0, w, mid))
        bottom = top.rotate(180)

        full = Image.new("RGBA", (w, h))
        full.paste(top, (0, 0))
        full.paste(bottom, (0, mid))

        # Blend the seam (4px gradient at the middle)
        blend_zone = 4
        for y in range(max(0, mid - blend_zone), min(h, mid + blend_zone)):
            alpha = (y - (mid - blend_zone)) / (2 * blend_zone)
            for x in range(w):
                top_px = top.getpixel((x, min(y, mid - 1)))
                bot_px = bottom.getpixel((x, max(y - mid, 0)))
                blended = tuple(int(top_px[c] * (1 - alpha) + bot_px[c] * alpha) for c in range(4))
                full.putpixel((x, y), blended)

        full = full.resize((self.w, self.h), Image.LANCZOS)
        full.save(output_path)
        print(f"✅ Background assembled: {output_path}")
        return full

    # ─────────────────────────────────────────────
    # STEP 3(i): Suit symbol on transparent background
    # ─────────────────────────────────────────────

    @staticmethod
    def load_symbol(symbol_path):
        """Load a suit symbol image (PNG with transparent background)."""
        return Image.open(symbol_path).convert("RGBA")

    # ─────────────────────────────────────────────
    # STEP 3(ii): Low-value card assembly (1-10)
    # ─────────────────────────────────────────────

    def assemble_low_value(self, suit, value, background_path, symbol_path,
                           border_path, output_path):
        """
        Create a low-value card (1-10) by placing suit symbols in standard positions.
        
        Layout follows French Tarot conventions:
        - Corner: value number + small suit symbol (top-left, bottom-right rotated)
        - Center: suit symbols arranged in standard patterns
        """
        bg = Image.open(background_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
        symbol = Image.open(symbol_path).convert("RGBA")

        # Corner symbol (small)
        corner_sym = symbol.resize((28, 28), Image.LANCZOS)

        # Center symbol (medium)
        center_size = int(self.w * 0.12)
        center_sym = symbol.resize((center_size, center_size), Image.LANCZOS)

        # Get standard positions for this value
        positions = self._get_symbol_positions(value, center_size)

        # Place center symbols
        for x, y, rotated in positions:
            s = center_sym.rotate(180) if rotated else center_sym
            bg.paste(s, (x, y), s)

        # Add corner value + symbol
        bg = self._add_corners(bg, str(value), corner_sym, suit)

        # Apply border
        if border_path:
            border = Image.open(border_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
            bg = Image.alpha_composite(bg, border)

        # Mirror bottom half for rotational symmetry
        bg = self._apply_rotational_symmetry(bg)

        bg.save(output_path)
        print(f"✅ {value} of {suit}: {output_path}")
        return bg

    def _get_symbol_positions(self, value, sym_size):
        """
        Standard French card symbol positions for values 1-10.
        Returns list of (x, y, is_rotated) tuples.
        Center column: x = w/2 - sym_size/2
        """
        cx = self.w // 2 - sym_size // 2
        margin_x = int(self.w * 0.22)
        lx = margin_x
        rx = self.w - margin_x - sym_size

        # Vertical positions (top half only, bottom half is mirrored)
        top_y = int(self.h * 0.08)
        mid_top_y = int(self.h * 0.22)
        mid_y = int(self.h * 0.36)
        center_y = self.h // 2 - sym_size // 2

        layouts = {
            1: [(cx, center_y, False)],
            2: [(cx, top_y, False), (cx, self.h - top_y - sym_size, True)],
            3: [(cx, top_y, False), (cx, center_y, False), (cx, self.h - top_y - sym_size, True)],
            4: [(lx, top_y, False), (rx, top_y, False),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            5: [(lx, top_y, False), (rx, top_y, False), (cx, center_y, False),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            6: [(lx, top_y, False), (rx, top_y, False),
                (lx, center_y, False), (rx, center_y, False),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            7: [(lx, top_y, False), (rx, top_y, False),
                (lx, center_y, False), (rx, center_y, False),
                (cx, mid_top_y, False),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            8: [(lx, top_y, False), (rx, top_y, False),
                (lx, center_y, False), (rx, center_y, False),
                (cx, mid_top_y, False), (cx, self.h - mid_top_y - sym_size, True),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            9: [(lx, top_y, False), (rx, top_y, False),
                (lx, mid_top_y, False), (rx, mid_top_y, False),
                (cx, center_y, False),
                (lx, self.h - mid_top_y - sym_size, True), (rx, self.h - mid_top_y - sym_size, True),
                (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
            10: [(lx, top_y, False), (rx, top_y, False),
                 (lx, mid_top_y, False), (rx, mid_top_y, False),
                 (cx, int(self.h * 0.15), False), (cx, self.h - int(self.h * 0.15) - sym_size, True),
                 (lx, self.h - mid_top_y - sym_size, True), (rx, self.h - mid_top_y - sym_size, True),
                 (lx, self.h - top_y - sym_size, True), (rx, self.h - top_y - sym_size, True)],
        }
        return layouts.get(value, [])

    # ─────────────────────────────────────────────
    # STEP 3(iii): High-value card assembly (V/C/D/R)
    # ─────────────────────────────────────────────

    def assemble_high_value(self, suit, rank, garment_path, head_path,
                            border_path, output_path, head_position=None):
        """
        Assemble a high-value face card.
        
        Args:
            suit: hearts/diamonds/clubs/spades
            rank: valet/knight/queen/king
            garment_path: PNG with transparent head area and transparent background
            head_path: PNG of the character's head
            border_path: PNG border with transparent center
            output_path: where to save the final card
            head_position: (x, y) tuple for head placement, or None for auto-center top
        """
        # Load garment (transparent bg + head placeholder)
        garment = Image.open(garment_path).convert("RGBA")
        gw, gh = garment.size

        # Load head
        head = Image.open(head_path).convert("RGBA")

        # Auto-detect head position if not specified (center-top of garment)
        if head_position is None:
            hx = (gw - head.width) // 2
            hy = int(gh * 0.02)  # near top
        else:
            hx, hy = head_position

        # Composite head onto garment
        top_half = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        top_half.paste(garment, (0, 0), garment)
        top_half.paste(head, (hx, hy), head)

        # Crop to top half
        top_crop = top_half.crop((0, 0, gw, gh // 2))

        # Rotate 180° for bottom half
        bottom_crop = top_crop.rotate(180)

        # Stack
        full = Image.new("RGBA", (gw, gh))
        full.paste(top_crop, (0, 0))
        full.paste(bottom_crop, (0, gh // 2))

        # Resize to card dimensions
        full = full.resize((self.w, self.h), Image.LANCZOS)

        # Add corner letter + suit symbol
        letter = HIGH_RANKS[rank]
        corner_sym_size = 28
        # We need the suit symbol for corners — generate a simple one
        full = self._add_corners_text(full, letter, suit)

        # Apply border
        if border_path:
            border = Image.open(border_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
            full = Image.alpha_composite(full, border)

        full.save(output_path)
        print(f"✅ {rank} of {suit}: {output_path}")
        return full

    # ─────────────────────────────────────────────
    # STEP 4: Trump (atout) assembly
    # ─────────────────────────────────────────────

    def assemble_trump(self, number, top_image_path, bottom_image_path,
                       number_ornament_path, border_path, output_path):
        """
        Assemble a trump card.
        
        Args:
            number: 1-21
            top_image_path: main illustration (top portion)
            bottom_image_path: main illustration (bottom portion), or None to mirror top
            number_ornament_path: decorative number frame/ornament (transparent PNG)
            border_path: card border
            output_path: where to save
        """
        # Load top image
        top_img = Image.open(top_image_path).convert("RGBA")

        if bottom_image_path:
            bottom_img = Image.open(bottom_image_path).convert("RGBA")
        else:
            # Mirror top for bottom
            bottom_img = top_img.rotate(180)

        # Create canvas
        canvas = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

        # Place top image (upper 45%)
        top_zone_h = int(self.h * 0.45)
        top_resized = top_img.resize((self.w, top_zone_h), Image.LANCZOS)
        canvas.paste(top_resized, (0, 0))

        # Place bottom image (lower 45%, rotated)
        bottom_zone_y = int(self.h * 0.55)
        bottom_resized = bottom_img.resize((self.w, self.h - bottom_zone_y), Image.LANCZOS)
        canvas.paste(bottom_resized, (0, bottom_zone_y))

        # Add number ornament in center band
        if number_ornament_path:
            ornament = Image.open(number_ornament_path).convert("RGBA")
            orn_h = int(self.h * 0.12)
            orn_w = int(orn_h * ornament.width / ornament.height)
            ornament = ornament.resize((orn_w, orn_h), Image.LANCZOS)
            ox = (self.w - orn_w) // 2
            oy = (self.h - orn_h) // 2
            canvas.paste(ornament, (ox, oy), ornament)

        # Add number text
        canvas = self._add_trump_number(canvas, number)

        # Apply border
        if border_path:
            border = Image.open(border_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
            canvas = Image.alpha_composite(canvas, border)

        canvas.save(output_path)
        print(f"✅ Trump {number}: {output_path}")
        return canvas

    # ─────────────────────────────────────────────
    # STEP 5: Excuse (joker) assembly
    # ─────────────────────────────────────────────

    def assemble_excuse(self, joker_image_path, background_path, border_path, output_path):
        """
        Assemble the Excuse (joker) card.
        
        Args:
            joker_image_path: joker illustration
            background_path: card background
            border_path: card border
            output_path: where to save
        """
        # Load background
        bg = Image.open(background_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)

        # Load joker image
        joker = Image.open(joker_image_path).convert("RGBA")

        # Crop joker to top half
        jw, jh = joker.size
        top_joker = joker.crop((0, 0, jw, jh // 2))
        bottom_joker = top_joker.rotate(180)

        # Stack
        full_joker = Image.new("RGBA", (jw, jh), (0, 0, 0, 0))
        full_joker.paste(top_joker, (0, 0))
        full_joker.paste(bottom_joker, (0, jh // 2))

        # Resize to fit card (with margin)
        margin = int(self.w * 0.08)
        joker_w = self.w - 2 * margin
        joker_h = int(joker_w * jh / jw)
        full_joker = full_joker.resize((joker_w, joker_h), Image.LANCZOS)

        # Center on background
        jx = margin
        jy = (self.h - joker_h) // 2
        bg.paste(full_joker, (jx, jy), full_joker)

        # Add "EXCUSE" text
        bg = self._add_excuse_text(bg)

        # Apply border
        if border_path:
            border = Image.open(border_path).convert("RGBA").resize((self.w, self.h), Image.LANCZOS)
            bg = Image.alpha_composite(bg, border)

        bg.save(output_path)
        print(f"✅ Excuse: {output_path}")
        return bg

    # ─────────────────────────────────────────────
    # Helper: Add corner text (value + suit)
    # ─────────────────────────────────────────────

    def _add_corners(self, img, value_text, symbol_img, suit):
        """Add value text and suit symbol to top-left and bottom-right corners."""
        draw = ImageDraw.Draw(img)
        color = SUIT_COLORS[suit]
        font_color = (200, 0, 0, 255) if color == "red" else (0, 0, 0, 255)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except (IOError, OSError):
            font = ImageFont.load_default()

        margin = 12
        # Top-left: value
        draw.text((margin, margin), value_text, fill=font_color, font=font)
        # Top-left: suit symbol below value
        img.paste(symbol_img, (margin, margin + 36), symbol_img)

        # Bottom-right: rotated
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((margin, margin), value_text, fill=font_color, font=font)
        temp.paste(symbol_img, (margin, margin + 36), symbol_img)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_corners_text(self, img, letter, suit):
        """Add letter (V/C/D/R) and suit symbol text to corners."""
        draw = ImageDraw.Draw(img)
        color = SUIT_COLORS[suit]
        font_color = (200, 0, 0, 255) if color == "red" else (0, 0, 0, 255)
        symbol = SUIT_SYMBOLS[suit]

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            sym_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except (IOError, OSError):
            font = ImageFont.load_default()
            sym_font = font

        margin = 12
        # Top-left
        draw.text((margin, margin), letter, fill=font_color, font=font)
        draw.text((margin, margin + 32), symbol, fill=font_color, font=sym_font)

        # Bottom-right (rotated)
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((margin, margin), letter, fill=font_color, font=font)
        temp_draw.text((margin, margin + 32), symbol, fill=font_color, font=sym_font)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_trump_number(self, img, number):
        """Add trump number to top and bottom of card."""
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except (IOError, OSError):
            font = ImageFont.load_default()

        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]

        # Top center
        draw.text(((self.w - tw) // 2, 8), text, fill=(0, 0, 0, 255), font=font)

        # Bottom center (rotated)
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text(((self.w - tw) // 2, 8), text, fill=(0, 0, 0, 255), font=font)
        temp = temp.rotate(180)
        img = Image.alpha_composite(img, temp)

        return img

    def _add_excuse_text(self, img):
        """Add 'EXCUSE' text to the card."""
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except (IOError, OSError):
            font = ImageFont.load_default()

        text = "EXCUSE"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((self.w - tw) // 2, 10), text, fill=(0, 0, 0, 255), font=font)

        return img

    def _apply_rotational_symmetry(self, img):
        """Ensure perfect 180° rotational symmetry by mirroring top half."""
        w, h = img.size
        top = img.crop((0, 0, w, h // 2))
        bottom = top.rotate(180)
        result = Image.new("RGBA", (w, h))
        result.paste(top, (0, 0))
        result.paste(bottom, (0, h // 2))
        return result

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
    bg_parser = sub.add_parser("background", help="Assemble background from top half")
    bg_parser.add_argument("deck", help="Deck name")
    bg_parser.add_argument("input", help="Top-half image")
    bg_parser.add_argument("output", help="Output path")

    # border
    brd_parser = sub.add_parser("border", help="Apply border to a card")
    brd_parser.add_argument("deck", help="Deck name")
    brd_parser.add_argument("card", help="Card image")
    brd_parser.add_argument("border", help="Border image (transparent center)")
    brd_parser.add_argument("output", help="Output path")

    # low-value
    low_parser = sub.add_parser("low", help="Assemble low-value card")
    low_parser.add_argument("deck", help="Deck name")
    low_parser.add_argument("suit", choices=SUITS)
    low_parser.add_argument("value", type=int, choices=range(1, 11))
    low_parser.add_argument("background", help="Background image")
    low_parser.add_argument("symbol", help="Suit symbol image")
    low_parser.add_argument("--border", help="Border image")
    low_parser.add_argument("output", help="Output path")

    # high-value
    high_parser = sub.add_parser("high", help="Assemble high-value face card")
    high_parser.add_argument("deck", help="Deck name")
    high_parser.add_argument("suit", choices=SUITS)
    high_parser.add_argument("rank", choices=list(HIGH_RANKS.keys()))
    high_parser.add_argument("garment", help="Garment image (transparent head area)")
    high_parser.add_argument("head", help="Head image")
    high_parser.add_argument("--border", help="Border image")
    high_parser.add_argument("output", help="Output path")

    # trump
    trump_parser = sub.add_parser("trump", help="Assemble trump card")
    trump_parser.add_argument("deck", help="Deck name")
    trump_parser.add_argument("number", type=int, choices=range(1, 22))
    trump_parser.add_argument("top", help="Top illustration")
    trump_parser.add_argument("--bottom", help="Bottom illustration (mirrors top if omitted)")
    trump_parser.add_argument("--ornament", help="Number ornament")
    trump_parser.add_argument("--border", help="Border image")
    trump_parser.add_argument("output", help="Output path")

    # excuse
    exc_parser = sub.add_parser("excuse", help="Assemble excuse card")
    exc_parser.add_argument("deck", help="Deck name")
    exc_parser.add_argument("joker", help="Joker illustration")
    exc_parser.add_argument("background", help="Background image")
    exc_parser.add_argument("--border", help="Border image")
    exc_parser.add_argument("output", help="Output path")

    args = parser.parse_args()

    if args.command:
        dc = DeckCreator(args.deck)
        if args.command == "background":
            dc.assemble_background(args.input, args.output)
        elif args.command == "border":
            dc.apply_border(args.card, args.border, args.output)
        elif args.command == "low":
            dc.assemble_low_value(args.suit, args.value, args.background,
                                  args.symbol, args.border, args.output)
        elif args.command == "high":
            dc.assemble_high_value(args.suit, args.rank, args.garment,
                                   args.head, args.border, args.output)
        elif args.command == "trump":
            dc.assemble_trump(args.number, args.top, args.bottom,
                              args.ornament, args.border, args.output)
        elif args.command == "excuse":
            dc.assemble_excuse(args.joker, args.background, args.border, args.output)
    else:
        parser.print_help()
