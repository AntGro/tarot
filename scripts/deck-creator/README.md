# Deck Creator Scripts

Complete pipeline for generating custom 78-card French Tarot decks.

## Card Types

A French Tarot deck has **78 cards**:

| Type | Count | Cards |
|------|-------|-------|
| Low-value simples | 40 | 1-10 × 4 suits |
| High-value simples | 16 | Valet(V), Cavalier(C), Dame(D), Roi(R) × 4 suits |
| Atouts (trumps) | 21 | Numbered 1-21 |
| Excuse (joker) | 1 | The Fool |

## Pipeline Overview

### Step 1: Set dimensions
Default: **400×738 px**

### Step 2: Design the border
Generate a PNG with **transparent inner area** — this frame overlays every card.

### Step 3: Simple cards

#### 3a. Background
Design the **top half** of a card background → `deck_pipeline.py background` mirrors it into a full background with smooth center transition.

#### 3b. Suit symbols
Design each suit symbol (♥♦♣♠) on **transparent background** — used for both low-value layouts and corner indicators.

#### 3c. Low-value cards (1-10)
`deck_pipeline.py low` places suit symbols in standard French card positions:
- Corner: value number + small suit symbol
- Center: standard pattern for 1-10 pips

#### 3d. High-value cards (V/C/D/R)
For each of the 16 face cards:
1. **Garment** — costume + attributes (horse for C, etc.) with transparent head zone + transparent background
2. **Head** — character portrait
3. **Assembly** — `deck_pipeline.py high` composites head onto garment, adds corner letter + suit, mirrors for rotational symmetry, applies border

### Step 4: Trumps (Atouts 1-21)
1. Design number ornamentation
2. Generate two illustrations (or one that gets mirrored)
3. `deck_pipeline.py trump` assembles: top image + bottom image + number + ornament + border

### Step 5: Excuse (Joker)
1. Generate joker illustration
2. `deck_pipeline.py excuse` mirrors it, places on background, adds "EXCUSE" text + border

## CLI Usage

```bash
# Assemble background from top half
python deck_pipeline.py background refn top_half.png output_bg.png

# Apply border to any card
python deck_pipeline.py border refn card.png border_frame.png output.png

# Create low-value card
python deck_pipeline.py low refn hearts 5 bg.png heart_symbol.png --border border.png output.png

# Create face card
python deck_pipeline.py high refn spades king garment.png head.png --border border.png output.png

# Create trump
python deck_pipeline.py trump refn 14 top.png --bottom bottom.png --ornament ornament.png --border border.png output.png

# Create excuse
python deck_pipeline.py excuse refn joker.png background.png --border border.png output.png
```

## Python API

```python
from deck_pipeline import DeckCreator

dc = DeckCreator("refn", card_width=400, card_height=738)

# Background
dc.assemble_background("top_half.png", "bg.png")

# Low-value card
dc.assemble_low_value("hearts", 5, "bg.png", "heart.png", "border.png", "5_of_hearts.png")

# Face card
dc.assemble_high_value("spades", "king", "garment.png", "head.png", "border.png", "king_of_spades.png")

# Trump
dc.assemble_trump(14, "top.png", None, "ornament.png", "border.png", "trump_14.png")

# Excuse
dc.assemble_excuse("joker.png", "bg.png", "border.png", "excuse.png")
```

## Style Guides

Each deck has a `style_guide.md` in `images/decks/<style>/` with:
- Color palette (suit-specific colors)
- Border/frame design specs
- Symbol placement rules
- Character rendering approach
- Lighting/mood description

See `images/decks/refn/style_guide.md` for an example.

## Naming Convention

```
1_of_hearts.png ... 10_of_hearts.png
jack_of_hearts.png
knight_of_hearts.png
queen_of_hearts.png
king_of_hearts.png
trump_01.png ... trump_21.png
excuse.png
cardback.png
```

All cards: **400×738 PNG**.
