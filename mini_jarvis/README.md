# JARVIS // Arc Sentinel Avatar System
### Anime Chibi Commander Edition · 1024px Ultra-HD Multi-Layer Sprite Engine

An authentic, fully animated, state-reactive anime avatar system created for **JARVIS**. Built specifically to deliver razor-sharp visual fidelity on high-DPI displays even when scaled up to **2.0x**, while maintaining full physics (gliding, flinging, roaming, puppet walking), real-time holographic Arc Reactor reticles, and IPC socket automation.

---

## ⚡ Key Highlights

- **1024px Ultra-HD Master Assets**: All turnaround views (`front`, `three_quarter`, `side`, `back`) are generated at 1024px resolution and downsampled with Lanczos subpixel filters at runtime, guaranteeing that **2.0x desktop scale** looks crisp and immaculate on 4K and Retina screens.
- **Dynamic 0.5x – 2.0x Matrix Scaling**: Integrated matrix transformation (`QPainter.scale(scale, scale)`) allows instant resizing without pixelation, window edge clipping, or physics distortion.
- **State-Reactive Arc Reactor Core**: The Arc Reactor chest core and HUD target reticles automatically pulse and shift colors to reflect live states:
  - 💠 **Idle**: Electric Arc Cyan (`#00F0FF`)
  - ⚡ **Thinking**: Stark Gold (`#FFB703`)
  - 🚀 **Spawning**: Azure High-Energy (`#78DCFF`)
  - 🛡️ **Hold / Needs Boss**: Emergency Ruby Red (`#FF4B4B`)
  - 🟢 **Approved**: Energy Matrix Green (`#32E68C`)
  - 💤 **Asleep**: Standby Indigo (`#285AA0`)
- **Procedural Puppet Walking**: Side and three-quarter views swing dynamically from the hip line (`HIP = 0.56`), complete with breathing bobs, step sway, and thruster hop particles.
- **Holographic Arc HUD Reticles**: Concentric targeting rings and telemetry degree ticks rotate smoothly behind the head in real time.
- **Standalone & Portable**: Self-contained engine with zero cloud dependencies; runs completely offline on Windows (`WinSta0\Default`).

---

## 📁 Repository Structure

```
mini_jarvis/
├── art/
│   ├── body/                     # 1024px Ultra-HD master sprite layers
│   │   ├── front_{base,glow,bloom,full}.png
│   │   ├── three_quarter_{base,glow,bloom,full}.png
│   │   ├── side_{base,glow,bloom,full}.png
│   │   └── back_{base,glow,bloom,full}.png
│   └── concepts/                 # Showcase presentation boards & turnarounds
│       └── jarvis_anime_turnaround_sheet.png (2400x1200 Ultra-HD)
├── layers/                       # 80x80 Arc Reactor Core emblem layers (notch / tray)
│   ├── base.png, glow.png, bloom.png
│   └── mask_{visor,core,chev}.png
├── sounds/                       # Auditory tactile feedback chimes (WAV)
├── fonts/                        # SpaceGrotesk & SpaceMono UI fonts
├── build_jarvis_sprite_art.py    # Master vector generator (regenerate all assets at any resolution)
├── sprite_body.py                # Procedural puppet walker & Arc HUD renderer
├── mini_jarvis.py                # Desktop sprite companion application (PySide6)
├── jarvis_island.py              # Island widget & state palette definitions
├── sprite_ui.py                  # UI components, Radial menu, request bubbles
├── launch_jarvis.py              # 1-Click desktop surface launcher
└── README.md                     # Complete documentation
```

---

## 🚀 Quickstart

### 1. Requirements
Ensure Python 3.10+ is installed with the following packages:
```bash
pip install PySide6 Pillow numpy
```

*(Optional for Windows desktop injection: `pip install pywin32`)*

### 2. Launching Mini JARVIS
Double-click `launch_jarvis.py` or run from terminal:
```bash
python launch_jarvis.py
```
Mini JARVIS will spawn immediately on your primary desktop surface (`WinSta0\Default`) with full click-and-drag physics.

---

## 🎚️ Scaling & Controls

### Tray Menu Scaling
Right-click Mini JARVIS's icon in the Windows Taskbar Notification Tray:
- Go to **Scale (0.5x - 2.0x)**:
  - `0.5x (Mini)` — Compact pocket companion (~60 × 99 px)
  - `0.75x (Compact)` — Subtle desk presence (~90 × 148 px)
  - `1.0x (Standard)` — Standard commander scale (~120 × 197 px)
  - `1.25x (Hero)` — Prominent presence (~150 × 246 px)
  - `1.5x (Large)` — Expanded detail view (~180 × 295 px)
  - `2.0x (Colossus)` — Ultra-HD giant commander (~240 × 394 px)

### Desktop Interactions
- **Left-Click Drag**: Move Mini JARVIS anywhere on your screen.
- **Fling / Throw**: Release while dragging with momentum to toss JARVIS; he will glide and bounce softly off your screen edges!
- **Triple-Click**: Triggers a playful dizzy animation.
- **Right-Click**: Opens the context menu (scale presets, voice toggle, sound mute, roam toggle).

---

## 📡 IPC Socket API

Mini JARVIS includes a local authenticated hook server listening on **port 8768** (configurable via `JARVIS_PORT` environment variable).

### Changing Scale via Socket
Send an HMAC-signed JSON packet to `127.0.0.1:8768`:
```json
{
  "event": "SetScale",
  "payload": {
    "scale": 1.5
  }
}
```

### Sending a Toast Notification
```json
{
  "event": "Notification",
  "payload": {
    "title": "Stark Industries",
    "message": "Arc Reactor operating at 100% capacity."
  }
}
```

---

## 🎨 Customizing the Sprite Art

To tweak armor colors, hairstyles, or dimensions:
1. Open [`build_jarvis_sprite_art.py`](file:///d:/Ai_Tools/antigravity_ai/mini_jarvis/build_jarvis_sprite_art.py).
2. Adjust the color palette constants:
   ```python
   CYAN_GLOW = (0, 240, 255, 255)       # Arc Reactor glow
   TITANIUM_MAIN = (48, 58, 74, 255)     # Armor plating
   CARBON_MAIN = (20, 24, 32, 255)       # Under-suit
   PLATINUM_HAIR = (225, 235, 248, 255)  # Hair
   ```
3. Run the script:
   ```bash
   python build_jarvis_sprite_art.py
   ```
All 1024px assets across `front`, `three_quarter`, `side`, and `back` views, along with the `layers/` core emblem and the 2400x1200 turnaround showcase board, will be regenerated in seconds!

---

*Engineered with precision for the creator of JARVIS.*
