# Refn Tarot Deck — Style Guide

## Theme
A French Tarot deck immersed in the cinematic universe of **Nicolas Winding Refn** — neon noir, hyper-stylized violence, brooding silence, and beauty laced with danger. Drawing from *Drive*, *Only God Forgives*, *The Neon Demon*, *Valhalla Rising*, *Bronson*, *Too Old to Die Young*, and *Copenhagen Cowboy*. The visual aesthetic is **oil painting with neon-noir palette**: deep blacks, electric pinks, cobalt blues, and blood reds — like a Caravaggio lit by neon signs.

## Card Dimensions
960 × 1771 pixels (aspect ratio ≈ 1:1.845)

## Background
Dark neon-noir texture — deep charcoal/black with subtle neon pink and blue undertones, like light bleeding through rain on a dark window. No frame, no objects, just atmosphere. Used for all cards.

## Suits

| Traditional | Themed Symbol | Visual Description | Color Tone |
|------------|---------------|-------------------|------------|
| Hearts ♥ | **Scorpion** | A scorpion viewed from above, tail curled symmetrically upward, inspired by the Driver's iconic jacket emblem | Gold/amber |
| Diamonds ♦ | **Neon Diamond** | A geometric diamond shape with neon glow edges, like a Bangkok neon sign | Hot pink/magenta |
| Clubs ♣ | **Clenched Fist** | A symmetrical clenched fist viewed from the front, knuckles forward — Bronson's raw power | Pale/bone white |
| Spades ♠ | **Katana** | A Japanese katana blade pointing upward, symmetrical guard/tsuba, from Only God Forgives | Steel blue/silver |

All suit symbols are vertically symmetrical (enforced via `enforce_vertical_symmetry()` post-processing) and have transparent backgrounds.

## Figure Cards

| Rank | Hearts (Scorpion) | Diamonds (Neon Diamond) | Clubs (Fist) | Spades (Katana) |
|------|-------------------|------------------------|--------------|-----------------|
| Valet (V) | The Kid (Drive) | Ruby (Neon Demon) | Young Bronson | Miu (Copenhagen Cowboy) |
| Cavalier (C) | Standard Gabriel (Drive) | The Countess (Neon Demon) | Prison Guard (Bronson) | Billy Lee (Too Old to Die Young) |
| Dame (D) | Irene (Drive) | Jesse (Neon Demon) | Mai (Copenhagen Cowboy) | Crystal Chang (Only God Forgives) |
| Roi (R) | The Driver (Drive) | The Neon Demon itself | Charles Bronson | Julian (Only God Forgives) |

### Figure Details

**Hearts — Drive / The Getaway**
The suit of the scorpion represents loyalty, silence, and lethal precision.
- **Valet**: The Kid — Benicio's young character, wide-eyed in a hoodie, LA streetlight glow on his face. The innocent drawn into violence.
- **Cavalier**: Standard Gabriel — the stuntman's mentor/colleague, older, weathered, Hawaiian shirt, cigar smoke curling. A man who knows the underworld.
- **Dame**: Irene — gentle beauty in warm light, sundress, caring eyes. The humanity the Driver protects. Soft golden tones against the noir.
- **Roi**: The Driver — iconic scorpion jacket, driving gloves, toothpick in mouth. Half his face lit by dashboard glow, half in shadow. The silent hero.

**Diamonds — The Neon Demon / Beauty & Destruction**
The suit of neon represents beauty, vanity, narcissism, and the consuming nature of the fashion world.
- **Valet**: Ruby — makeup artist with an unsettling smile, holding a brush like a weapon. Jealousy and obsession personified.
- **Cavalier**: The Countess — a powerful fashion industry figure, draped in designer clothes, cold eyes behind sunglasses. The gatekeeper of beauty.
- **Dame**: Jesse — the ingenue, impossibly beautiful, doe-eyed, bathed in neon pink light. Fresh-faced innocence about to be devoured.
- **Roi**: The Neon Demon itself — an abstract, terrifying figure of pure neon energy, a triangle of light with eyes, the dark heart of LA vanity.

**Clubs — Bronson & Copenhagen Cowboy / Raw Power**
The suit of the fist represents brute strength, madness, performance, and the primal self.
- **Valet**: Young Bronson — before the infamy, a troubled youth with a shaved head and manic grin. Raw potential for chaos.
- **Cavalier**: Prison Guard — uniformed, rigid, representing the system that tries and fails to contain Bronson. Shield and baton ready.
- **Dame**: Mai — the enigmatic protagonist of Copenhagen Cowboy, pale skin, dark bob haircut, supernatural stillness. An otherworldly presence.
- **Roi**: Charles Bronson — handlebar mustache, bare-chested, covered in war paint/grease. The ultimate performer of violence, arms spread theatrically.

**Spades — Only God Forgives & Too Old to Die Young / Vengeance**
The suit of the katana represents honor, revenge, divine punishment, and the East-meets-West collision.
- **Valet**: Miu — Copenhagen Cowboy's young woman navigating the criminal underworld, leather jacket, neon-lit face, determined stare.
- **Cavalier**: Billy Lee — from Too Old to Die Young, a cartel enforcer in a sharp suit, gold chain, dead eyes. Violence as profession.
- **Dame**: Crystal Chang — Julian's terrifying mother in Only God Forgives. Blonde hair, red dress, venomous elegance. The dragon lady of Bangkok.
- **Roi**: Julian — Ryan Gosling in Bangkok, white shirt stained with sweat, hands that want to clench but can't. Haunted, guilt-ridden, seeking forgiveness from a god who doesn't forgive.

## Trump Cards (Major Arcana)

The 21 trumps trace the arc of Refn's filmography and thematic obsessions — from silent violence to neon transcendence.

| # | Name | Top Scene | Bottom Scene |
|---|------|-----------|--------------|
| 1 | **The Driver** | A silver Chevy Malibu racing through neon-lit LA streets at night, reflections on wet asphalt | The Driver sitting alone in a motel room, bathed in blue TV light, toothpick between lips |
| 2 | **The Getaway** | A car chase through LA's concrete river channels, headlights blazing, sparks flying | The elevator scene — golden light, a moment of tenderness before ultraviolence |
| 3 | **The Scorpion Jacket** | Close-up of the iconic silver satin jacket with the gold scorpion emblem, neon reflections | A dark alley in LA, the jacket splattered with blood, the fable of the scorpion and the frog |
| 4 | **Real Human Being** | The Driver carrying young Benicio through a sunlit neighborhood, genuine warmth | The mask — a latex face staring blankly, the stuntman's disguise, identity dissolved |
| 5 | **Valhalla** | A Viking longship emerging from fog on a grey Nordic sea, One-Eye standing at the prow | The New World — lush green forests of North America, Norse warriors confronting the unknown |
| 6 | **One-Eye** | A mud-covered warrior with one eye, chained, fighting in a pit surrounded by torch-bearing spectators | A psychedelic red vision — One-Eye's prophetic hallucination, abstract shapes and blood |
| 7 | **The Neon Demon** | A runway show bathed in strobing neon — pink, blue, white — models as spectres | Jesse lying in a pool of neon light, the triangle symbol glowing above her, consumed by beauty |
| 8 | **The Audition** | A sterile white casting room, a row of identical beautiful girls, fluorescent lights | A dark bathroom — mirrors reflecting infinity, Jesse seeing her true self for the first time |
| 9 | **Bangkok Noir** | Bangkok's Chinatown at night — neon signs in Thai script, rain-slicked streets, karaoke bars glowing | A Muay Thai boxing ring, empty except for blood on the canvas, spotlights cutting through smoke |
| 10 | **The Hands of God** | Chang walking through Bangkok streets, sword hidden behind his back, people parting before him | A karaoke stage — Chang singing to a rapt audience, the divine executioner at peace |
| 11 | **Crystal's Wrath** | A luxury Bangkok hotel suite, all gold and red, Crystal Chang holding court | A dingy basement, instruments of torture laid out with surgical precision, neon flickering |
| 12 | **Bronson Unbound** | Bronson in his cell, painting the walls with elaborate murals, bare-chested, manic energy | The one-man show — Bronson on a theater stage in full makeup, audience in formal dress, performing his life |
| 13 | **The Cage** | Prison corridors stretching to infinity, fluorescent lights buzzing, cells on both sides | Bronson fighting six guards in slow motion, grease covering his body, a ballet of violence |
| 14 | **Copenhagen Nights** | Copenhagen's harbor at night, container ships and cranes silhouetted against a bruised purple sky | An underground fighting ring beneath neon signs, Mai standing perfectly still among chaos |
| 15 | **The Supernatural** | Mai walking through a forest of birch trees, everything silver and grey, an otherworldly glow around her | A pig farm at night — sinister red lights, the boundary between the mundane and the horrific |
| 16 | **Too Old to Die Young** | Los Angeles at golden hour, seen from a hilltop — the city sprawling below like a circuit board | A Mexican cartel compound at night, fire and neon, the collision of two criminal worlds |
| 17 | **The Vigilante** | A lone figure walking down an empty LA street at 3am, streetlights creating pools of orange light | A diner at dawn — a man eating alone, gun visible under his jacket, the weight of what he's done |
| 18 | **Neon Requiem** | A corridor of neon tubes — pink, blue, purple — stretching into infinity, a figure walking toward the light | Shattered neon signs on wet pavement, sparks and glass, beauty destroyed |
| 19 | **The Reflection** | A man staring at his hands in a dark room, a single shaft of light illuminating the blood on them | A still lake at sunset reflecting a burning building, beauty in destruction |
| 20 | **Divine Punishment** | Chang's sword descending in slow motion, light catching the blade, Bangkok skyline behind | A Buddhist temple at dawn, incense smoke rising, the aftermath of violence — peace restored through blood |
| 21 | **Only God Forgives** | A neon-lit hallway stretching to eternity — pink walls, blue floor, a figure at the vanishing point | Julian kneeling before Chang, arms extended, offering his hands — the final act of submission and grace |

### Narrative Arc
The trumps trace Refn's cinematic journey: from the cool restraint of Drive (1-4), through the primal Norse violence of Valhalla Rising (5-6), into the neon-drenched horror of beauty in The Neon Demon (7-8), the divine vengeance of Bangkok in Only God Forgives (9-11), the raw performance art of Bronson (12-13), the supernatural noir of Copenhagen Cowboy (14-15), the sprawling LA crime saga of Too Old to Die Young (16-17), and finally the transcendent neon mythology that connects all of Refn's work (18-21).

## Excuse (Joker)
- **Character**: One-Eye from Valhalla Rising — the mute Viking warrior, the most elemental of Refn's protagonists
- **Visual description**: A mud-caked warrior with one eye (the other a scarred empty socket), wild hair, animal furs, holding a primitive weapon. Silent, primal, outside time and civilization. Oil painting style with dark earth tones.
- **Thematic significance**: One-Eye exists outside narrative — he is pure archetype, pure violence, pure silence. Like the traditional Excuse/Fool, he stands apart from the hierarchy of the other cards, moving between worlds (the Old World and the New, life and death, the human and the divine).

## Ornament
The trump center ornament is a shared baroque/Art Nouveau pattern, arc-masked to fit the curved borders between the number boxes. Original colors preserved, no tinting.

## AI Prompt Guidelines
- **Style keywords**: "Nicolas Winding Refn cinematic universe, neon noir, oil painting style, rich impasto brushstrokes, dark moody palette, neon pink blue accents"
- **Figure prompts**: "half-length portrait from waist up, face prominently visible, hands visible, plain solid white background, oil painting style, rich impasto brushstrokes, neon noir lighting" + character-specific details
- **Knight prompts**: add "mounted on horse/vehicle, rider from waist up with mount visible, oil painting style"
- **Trump scene prompts**: "epic cinematic scene, oil painting style, rich impasto brushstrokes, neon noir palette, [specific scene description], Nicolas Winding Refn aesthetic"
- **Symbol prompts**: "vertically symmetrical [object] icon, centered, transparent background, clean lines, single color, oil painting style"
- **Orientation**: `--orientation square` for figures/symbols, `--orientation landscape` for trump scenes and backgrounds

## File Structure
```
images/decks/refn/
├── background.png
├── style_guide.md
├── suits/
│   ├── hearts.png    # Scorpion
│   ├── diamonds.png  # Neon Diamond
│   ├── clubs.png     # Clenched Fist
│   └── spades.png    # Katana
├── simple/
│   ├── hearts_01.png ... hearts_10.png
│   ├── diamonds_01.png ... diamonds_10.png
│   ├── clubs_01.png ... clubs_10.png
│   └── spades_01.png ... spades_10.png
├── figures/
│   ├── hearts_valet.png ... hearts_king.png
│   ├── diamonds_valet.png ... diamonds_king.png
│   ├── clubs_valet.png ... clubs_king.png
│   └── spades_valet.png ... spades_king.png
├── trumps/
│   └── trump_01.png ... trump_21.png
├── excuse/
│   └── excuse.png
└── raw/             # Raw generated images before pipeline processing
```
