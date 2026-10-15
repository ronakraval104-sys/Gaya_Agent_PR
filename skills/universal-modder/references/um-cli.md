# Universal Modder (`um`) CLI Reference

The `um` CLI provides command-line primitives for game discovery, safe backups, asset generation, window automation, video editing, and knowledge base collaboration.

---

## 1. Game Reconnaissance: `um scan`

Inspects installed games across Steam, Epic, Xbox Game Pass, and custom directories.

```bash
# Scan a specific game directory
um scan "C:\Games\Terraria"

# Scan by game title across detected stores
um scan "Age of Empires II"

# Output format as structured JSON
um scan "C:\Program Files (x86)\Steam\steamapps\common\Portal 2" --json > recon.json
```

### Outputs Detected:
- **Engine**: Unity (Mono / IL2CPP), Unreal Engine, .NET/XNA, Godot, Source 1/2, Custom C++.
- **Binary Architecture**: PE32 vs PE64, architecture type (x86 / x64 / ARM64).
- **Anti-Cheat Presence**: Flags active anti-cheat kernel drivers (Easy Anti-Cheat, BattlEye, Vanguard, VAC).
- **Existing Loaders**: Checks if BepInEx, MelonLoader, tModLoader, UE4SS, or Fabric are installed.
- **Save Directories**: Finds user save games, world files, and config paths across `%APPDATA%`, `%LOCALAPPDATA%`, and Steam Cloud.

---

## 2. Lab Safety: `um backup`

Snapshots, diffs, and restores save games and configuration folders before testing risky code modifications.

```bash
# Create a named snapshot of a saves folder
um backup create "%USERPROFILE%\Documents\My Games\Terraria\Worlds" --name "pre-nuke-test"

# List all existing backups
um backup list

# View diff between current files and a snapshot
um backup diff "pre-nuke-test"

# Restore a snapshot cleanly
um backup restore "pre-nuke-test" --yes
```

---

## 3. Pixel Art & Sprite Processing: `um sprite`

Transforms raw generated AI images into game-ready sprites with clean transparency, correct resolution, and palette quantization.

```bash
# Remove background and produce crisp alpha channel
um sprite cutout ./raw_art.png --out ./sprites/gun_cutout.png

# Nearest-neighbor resize preserving pixel art sharpness
um sprite fit ./sprites/gun_cutout.png --width 64 --height 32 --out ./sprites/gun_64x32.png

# Quantize colors to a game's specific color palette
um sprite palette ./sprites/gun_64x32.png --palette ./palettes/aoe2.act --out ./sprites/gun_quantized.png

# Pack loose frame images into a sprite sheet
um sprite sheet ./frames/*.png --columns 8 --padding 1 --out ./sprites/walk_sheet.png

# Slice a sprite sheet back into individual frames
um sprite slice ./sprites/walk_sheet.png --tile-width 32 --tile-height 32 --out-dir ./frames/

# Generate an animated GIF preview
um sprite preview ./frames/*.png --fps 12 --out ./preview.gif
```

---

## 4. 3D Model to Sprite Rendering: `um render3d`

Uses headless Blender to render 3D meshes (GLB, FBX, OBJ) into directional 2D sprite headings matching game camera angles.

```bash
# Render a 3D model into 16 isometric directions (AoE2 standard)
um render3d ./models/robotaxi.glb --preset aoe2 --headings 16 --out-dir ./sprites/robotaxi/

# Presets available:
#   - aoe2: Elevation 30°, azimuth stepped 22.5° (16 headings)
#   - iso8: Standard 8-direction isometric (elevation 35.264°)
#   - trueiso: True dimetric/isometric projection
#   - topdown: 90° top-down camera (Hotline Miami / GTA 1/2 style)
#   - side: 2D platformer / side-scroller side view
#   - turntable: 360° rotational turntable preview
```

---

## 5. Windows Game Automation: `um win`

Controls and verifies the running game safely without interfering with other desktop apps.

```bash
# Launch a game process in windowed mode with logging
um win launch "C:\Games\Terraria\Terraria.exe" --args "-windowed -log"

# Capture a clean screenshot of the game window (DirectX / GPU safe)
um win shot --process "Terraria.exe" --out ./receipts/ingame_weapon.png

# Send isolated input strokes directly to the game window
um win drive --process "Terraria.exe" --keys "SPACE" --duration 0.2

# Find game process ID and performance stats
um win ps --filter "Terraria"

# Terminate process safely by PID
um win kill --pid 14208
```

---

## 6. Showcase Recording & Editing: `um win record` & `um video`

Records clean in-game video and process-isolated audio, then cuts automated showcase videos from edit decision lists (EDL).

```bash
# Record game window with process loopback audio (avoids capturing Discord/system music)
um win record --process "Terraria.exe" --duration 20 --out ./raw_recording.mp4

# Generate thumbnail contact sheet of the recording
um video contact ./raw_recording.mp4 --interval 2 --out ./contact_sheet.png

# Compile an edited video from an EDL JSON specification
um video compile --edl ./edit_list.json --music ./bgm.mp3 --out ./showcase.mp4
```

---

## 7. Generative Asset Pipelines: `um comfy` & `um fal`

Connects to local ComfyUI or cloud fal.ai to generate assets with provenance tracking.

### Local ComfyUI (Port 8188)
```bash
# Verify ComfyUI status
um comfy status

# Generate an image and automatically cut out transparent sprite
um comfy image --prompt "pixel art flame sword, transparent background" --sprite --out ./assets/sword.png

# Execute any arbitrary exported ComfyUI API workflow
um comfy run --workflow ./workflows/sd_pixel_api.json --inputs '{"prompt": "retro alien npc"}' --out-dir ./assets/
```

### fal.ai Cloud REST MCP / CLI
```bash
# Set API key securely
um fal key set

# Generate sprites, audio, and 3D models
um fal sprite --prompt "futuristic hovering drone, pixel art" --out ./assets/drone.png
um fal sfx --prompt "plasma blast explosion, 16-bit retro" --duration 1.5 --out ./audio/plasma.wav
um fal model3d --prompt "isometric military tank" --out ./models/tank.glb
```

---

## 8. Mod Publishing & Linting: `um publish check`

Verifies that a mod package complies with open-source and legal invariants before publication.

```bash
um publish check ./my-mod-package/
```
Checks performed:
- [x] No proprietary game executable or DLL files.
- [x] No game asset archives (`.pak`, `.assets`, `.vpk`) bundled directly.
- [x] No decompiled source dumps present in distribution.
- [x] No leaked environment variables, tokens, or API keys (`FAL_KEY`, `OPENAI_API_KEY`).
- [x] Valid license and `README.md` instructions included.

---

## 9. Knowledge Base Collaboration: `um kb`

Interacts with the communal knowledge base of field notes.

```bash
# Search prior art for a game or mechanism
um kb search "Hades"

# Create a new field note skeleton
um kb new --game "Hades II" --title "A new boon god" --from-scan hades --agent "Gaya"

# Validate field note formatting against schema
um kb check knowledge/games/hades-ii/a-new-boon-god.md

# Open a GitHub Pull Request to share field note with the community
um kb pr knowledge/games/hades-ii/a-new-boon-god.md --yes
```
