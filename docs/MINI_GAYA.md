# 🤖 Mini Gaya — Desktop Companion & Voice Suite

**Mini Gaya** is an interactive desktop companion, telemetry HUD, and local voice suite powered by PySide6 (Qt). Mini Gaya lives on your desktop, monitors the active AI agent sessions in real-time, displays reactive animations, toasts critical alerts (like LOGOS PASS or input requests), and speaks directly to you.

---

## ⚡ Core Features
- **Live Reactive Sprite**: Custom gold-and-obsidian anime guardian sprite with dynamic idle, thinking, floating, celebrating, and alert animations.
- **Bi-Directional Telemetry**: Tracks Google Antigravity and OpenCode sessions live from the transcript stream.
- **Voice Suite (STT + TTS)**:
  - Local speech synthesis with automatic phonetic name correction (pronounces **R0n** accurately as **"Ros"**).
  - Sanitized speech output ensuring no confusing legacy cloud phrases.
  - Spoken announcements when LOGOS signs off (`"LOGOS passed it, Ros."`) or when approval is needed.
- **Interactive Island & Brief**:
  - Click the sprite to view recent session briefs and context budget pressure.
  - Interactive approval cards for pending permissions and tool questions.

---

## 🚀 Installation & Launch

### Prerequisites:
- Python 3.10+
- PySide6, Pillow, requests

```bash
cd mini_gaya
pip install -r requirements.txt # or: pip install PySide6 Pillow requests pyttsx3
```

### Launching:
```cmd
python launch_mini_gaya.py
```
Or double click:
```cmd
start_mini_gaya.bat
```
