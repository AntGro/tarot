# ♠ Tarot 1v1

A 2-player French Tarot card game — fully static, no server required.

## How to Play

**Online:** Visit the GitHub Pages URL → create a room → share the 4-letter code with your opponent.

**Solo:** Click "Partie solo" to play against a simple AI opponent.

## Features

- 🃏 **78-card French Tarot deck** — 21 trumps + Excuse + 4 suits of 14 (with Knights)
- 🎮 **2-player multiplayer** via WebRTC (PeerJS) — peer-to-peer, no server
- 🤖 **AI opponent** for solo practice
- 🎨 **Felt table UI** with CSS-rendered cards (no images needed)
- 🃏 **Fan hand layout** with hover animations
- 📱 **Responsive** — works on desktop and mobile
- 🔊 **Sound effects** (Web Audio API)
- 🏠 **Room codes** — 4-letter codes to join games
- 📋 **Copy code** — click to copy room code
- 🔌 **Disconnect detection**

## Game Rules (2-player variant)

Each player gets **11 hand cards** and **7 stacks** (7, 6, 5, 4, 3, 2, 1 cards — only the top card is visible).

Players alternate playing cards:
- **Must follow suit** if possible
- **Must trump** if can't follow suit and have trumps
- **Must overtrump** if possible (play a higher trump than what's on the table)
- **Fool (Excuse)** can always be played — but almost never wins

**Scoring:** Card points range from 0.5 (pip cards) to 4.5 (Kings, Bouts). The 3 **Bouts** (Oudlers) are: Trump 1 (Petit), Trump 21, and the Fool.

## Tech Stack

- **PeerJS** (WebRTC) for P2P multiplayer
- **Vanilla JS** — no build step, no framework
- **CSS-only cards** — no image assets required
- Single `index.html` — deploy anywhere

## Deploy

Just serve `index.html`. Works on GitHub Pages, Netlify, Vercel, or any static host.

```bash
# Local dev
python3 -m http.server 8080
# then open http://localhost:8080
```

## License

MIT
