# Deck Creator Scripts

Tools for generating custom card decks for the Tarot app.

## Card Generation Recipe

1. **Reference the Grimaud original** — feed it as `--image-file` for style reference
2. **If new style**: write a `style_guide.md` in `images/decks/<style>/` first
3. **If existing style**: read the style guide + review existing cards for consistency
4. **Generate ONLY the top half** — describe the target style, landscape orientation
5. **Run `mirror_card.py`** — creates the full card with perfect 180° rotational symmetry
6. **Drop in** `images/decks/<style>/` — fallback to grimaud handles the rest

## Scripts

### `mirror_card.py`

Assembles a full playing card from a top-half image.

```bash
# Basic usage
python mirror_card.py top_half.png ../../images/decks/refn/king_of_hearts.png

# Custom dimensions
python mirror_card.py top_half.png output.png --width 400 --height 738
```

**Steps:**
1. Crops input to top 50%
2. Rotates crop 180°
3. Stacks top + rotated bottom
4. Resizes to 400×738 (standard card size)

## Style Guide Rules

Each deck style must have a `style_guide.md` in its folder with:
- Color palette (suit-specific: e.g. pink for ♥♦, blue for ♠♣)
- Border/frame style
- Symbol placement (suit icon position, letter position)
- Character rendering approach
- Lighting / mood description

See `images/decks/refn/style_guide.md` for an example.

## Card Naming Convention

```
king_of_hearts.png
queen_of_spades.png
jack_of_diamonds.png
knight_of_clubs.png
```

All cards must be **400×738 PNG**.
