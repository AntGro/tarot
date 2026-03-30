# Deck Creator Pipeline

## Pipeline Rules

1. **One shared background** for ALL simple cards (low-value 1-10 + face cards V/C/D/R). Asset = top-half only → mirrored programmatically for 180° rotational symmetry.

2. **Face cards**: single figure asset with **transparent background** (complete character, NOT separate garment + head). Asset = **top-half figure only** → mirrored programmatically.

3. **Excuse/joker asset = top-half figure only** → mirrored programmatically.

4. **Trump number ornaments** at **TOP and BOTTOM** of the card (Grimaud style), NOT in a center band. Ornaments overlay the illustrations.

5. **Trump top & bottom illustrations**: same size (each half the card height).

6. **Stack order**: `background → symbols/figures → corners`.

7. **Low-value symbol directions**: 
   - Top half: **upward**
   - Bottom half: **downward**  
   - Middle horizontal line: **upward**

8. **AI prompt rules for figures/excuse**:
   - Always include "plain solid color background" so `rembg` works cleanly.
   - All figures (V/C/D/R) and excuse must be **half-length portraits**: "from the waist up, no legs visible, full head visible with space above, showing hands, centered".
   - **Knights** must also show the horse head: "knight mounted on horse, half-length portrait showing rider from waist up with hands visible and horse head and neck, no hooves".
   - Do **NOT** use "close-up" or "zoomed in" — it crops too tight.
   - Avoid textured/gradient/scenic backgrounds.
   - The pipeline includes **automatic leg detection** (`detect_legs`): warns if bottom 30% fill < 30%. If triggered, regenerate.

9. **Suit symbol rules**:
   - Generated suit symbols must be **vertically symmetrical** (like standard ♥♦♣♠).
   - AI prompt must include "vertically symmetrical, symmetric along vertical axis".
   - After generation, the pipeline enforces symmetry by mirroring the left half onto the right half.
   - Symbols must have a **transparent background** and be centered.

## Assets Needed Per Deck

| Asset | Description | Count |
|-------|-------------|-------|
| `background_top.png` | Top-half background (mirrored for full card) | 1 |
| `symbol_*.png` | Suit symbol (♥♦♣♠) on transparent bg, **vertically symmetrical** | 4 |
| `figure_*_top.png` | Face card top-half figure (transparent bg, complete character) | 16 (4 suits × 4 ranks) |
| `trump_top_*.png` | Trump illustration top half | 21 |
| `trump_bottom_*.png` | Trump illustration bottom half (optional, mirrors top) | 0-21 |
| `ornament.png` | Trump number decoration (placed at top + bottom) | 1 |
| `joker_top.png` | Excuse figure top half | 1 |
| `cardback.png` | Card back design | 1 |
| **`style_guide.md`** | **Deck documentation (required, see template below)** | **1** |

## Deck Documentation (`style_guide.md`)

Every themed deck **must** include a `style_guide.md` at `images/decks/<name>/style_guide.md` describing all creative choices. This is generated alongside the assets, not after.

### Required Template

```markdown
# <Deck Name> Tarot Deck — Style Guide

## Theme
Brief description of the deck's universe/setting and visual aesthetic.

## Card Dimensions
<width> × <height> pixels

## Background
Description of the shared background image (color palette, texture, mood).

## Suits
| Traditional | Themed Symbol | Visual Description | Color Tone |
|------------|---------------|-------------------|------------|
| Hearts ♥ | <name> | <what it looks like> | <dominant color> |
| Diamonds ♦ | <name> | <what it looks like> | <dominant color> |
| Clubs ♣ | <name> | <what it looks like> | <dominant color> |
| Spades ♠ | <name> | <what it looks like> | <dominant color> |

## Figure Cards
| Rank | Hearts | Diamonds | Clubs | Spades |
|------|--------|----------|-------|--------|
| Valet (V) | <character name + description> | ... | ... | ... |
| Cavalier (C) | <character name + description> | ... | ... | ... |
| Dame (D) | <character name + description> | ... | ... | ... |
| Roi (R) | <character name + description> | ... | ... | ... |

### Figure Details
For each figure, describe:
- Who they are in the theme's universe
- Key visual elements (costume, props, pose)
- Why they were chosen for this suit/rank

## Trump Cards (1-21)
| Number | Name | Top Scene | Bottom Scene |
|--------|------|-----------|--------------|
| 1 | <name> | <description> | <description> |
| 2 | <name> | <description> | <description> |
| ... | ... | ... | ... |
| 21 | <name> | <description> | <description> |

### Trump Narrative
Brief explanation of the trump sequence — is there a story arc, thematic progression, or symbolic order?

## Excuse (Joker)
- Character: <who/what>
- Visual description: <pose, outfit, props>
- Thematic significance: <why this character>

## Ornament
Description of the trump number zone ornament pattern.

## AI Prompt Guidelines
Style keywords and visual references used for this deck's image generation (for reproducibility).

## File Structure
<tree of generated files>

## Generated
<date> using the tarot deck pipeline
```

## Usage

```python
from deck_pipeline import DeckCreator

dc = DeckCreator(deck_name="dune")

# 1. Assemble background from top-half asset
dc.assemble_background("assets/bg_top.png", "background.png")

# 2. Low-value card (bg → symbols → corners)
dc.assemble_low_value("hearts", 5, "background.png", "symbol_hearts.png", "5_of_hearts.png")

# 3. Face card (bg → figure → corners)
# Figure is a SINGLE top-half image with transparent background
dc.assemble_high_value("hearts", "queen", "figure_queen_hearts_top.png",
                       "background.png", "queen_of_hearts.png")

# 4. Trump (ornaments at top + bottom, Grimaud style)
dc.assemble_trump(1, "trump_top_01.png", None, "ornament.png", "trump_01.png")

# 5. Excuse (joker asset = top half only)
dc.assemble_excuse("joker_top.png", "background.png", "excuse.png")
```

## Background Removal (for figures & joker)

`imagine` can't generate transparent backgrounds natively. Use `remove_background()` as a post-processing step after generating face card figures and joker art:

```python
# After generating a figure with imagine
dc.remove_background("figure_raw.jpg", "figure_queen_hearts_top.png")
```

Requires: `pip install rembg onnxruntime`

CLI: `python deck_pipeline.py remove-bg input.jpg output.png`

## Image Generation Guidelines

When using `imagine` to generate assets, match orientation to the target ratio:

| Asset | Target ratio | `--orientation` |
|-------|-------------|-----------------|
| `background_top` | ~1.08:1 (400×369) | `square` |
| `figure_*_top` (face cards) | ~1.08:1 (top half of card) | `square` |
| `joker_top` | ~1.08:1 (top half of card) | `square` |
| `trump_top_*` | ~1.08:1 (400×369) | `square` |
| `cardback` | ~0.54:1 (400×738) | `vertical` |
| `ornament` | wide banner | `landscape` |
| `symbol_*` | 1:1 | `square` |

## CLI

```bash
python deck_pipeline.py background dune assets/bg_top.png output/background.png
python deck_pipeline.py low dune hearts 5 background.png symbol_hearts.png output/5_of_hearts.png
python deck_pipeline.py high dune hearts queen figure_top.png background.png output/queen.png
python deck_pipeline.py trump dune 1 top.png output/trump_01.png
python deck_pipeline.py excuse dune joker_top.png background.png output/excuse.png
```
