# 🃏 Tarot 1v1

A browser-based **French Tarot** card game for two players — no server required.

## ✨ Features

- **Peer-to-peer multiplayer** via [PeerJS](https://peerjs.com/) (WebRTC) — no backend, no signaling server to maintain
- **AI opponent** — play solo against a built-in AI that follows standard Tarot strategy
- **Single-file architecture** — one `index.html`, drop it anywhere and play
- **Full French Tarot rules** for 1v1 (simplified from the 4-player variant):
  - 78-card deck (suits + 21 trumps + Excuse)
  - Bidding phase (Pass / Petite / Garde)
  - Dog (chien) reveal and exchange
  - Trick-by-trick play with proper suit/trump obligations
  - Scoring with multipliers and bonus tracking (Petit au bout, etc.)
- **Responsive layout** — scales from mobile to desktop
- **Card images** — classic French card artwork with illustrated trumps
- **Text-mode fallback** — for narrow screens, switches to compact text rendering

## 🚀 Play

### Online (GitHub Pages)

👉 **[Play now](https://antgro.github.io/tarot/)**

### Locally

Just open `index.html` in a browser. No build step, no dependencies.

```bash
git clone https://github.com/AntGro/tarot.git
open tarot/index.html   # macOS
# or
xdg-open tarot/index.html   # Linux
```

## 🎮 How to Play

1. **Choose a mode:**
   - 🤖 **vs AI** — instant solo game
   - 👥 **Host** — create a room and share the Room ID with a friend
   - 🔗 **Join** — enter a Room ID to join an existing game

2. **Bidding:** After cards are dealt, decide whether to bid (Petite/Garde) or pass.

3. **Dog phase:** The bidder sees the 6-card dog and can exchange cards.

4. **Play:** Alternate tricks following French Tarot rules:
   - Must follow suit if possible
   - Must play a trump if you can't follow suit
   - Must overtrump if possible (play a higher trump than what's on the table)
   - The Excuse can be played anytime but doesn't win tricks

5. **Scoring:** Points are counted based on card values. The bidder needs 36+ points (with 0 bouts) to 56+ points (with 3 bouts) to win.

## 🏗️ Architecture

```
tarot/
├── index.html     # Everything — HTML, CSS, JS, game engine (~1900 lines)
├── images/        # Card artwork
│   ├── trumps/    # 22 trump card illustrations (TN-00.jpg to TN-21.jpg)
│   ├── cardback.jpg
│   └── *.png      # Standard suit cards
└── README.md
```

**Key design decisions:**
- **Zero dependencies** (except PeerJS CDN for multiplayer)
- **No framework** — vanilla JS with a state-driven render loop
- **DOM diffing** — signature-based per-section updates to minimize flicker
- **Per-slot center zone** — each table slot tracks its own card independently
- **CSS transitions** for opacity changes (trick resolution) instead of DOM rebuilds

## 🔀 Branches

| Branch | Description |
|--------|-------------|
| `master` | Current version — static single-file PeerJS game |
| `v1` | Archive of the original Python/Flask multiplayer version |

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
