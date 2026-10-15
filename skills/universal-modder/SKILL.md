---
name: universal-modder
description: Universal PC game modding, reverse engineering, asset generation, and cross-game mashups. Use whenever the user asks to mod a game, inspect game files, reverse engineer game logic/formats, build sprites/textures/models for a game, create cross-game mashups (e.g. Minecraft in GTA V), or run the universal-modder (um) CLI and workflows. Triggers on "mod <game>", "reverse engineer", "game modding", "extract game assets", "unity mod", "unreal mod", "tmodloader", "bepinex", "harmony patch", "cross-game mashup", "um scan", "um backup", "universal modder".
---

# Universal Modder (UM)

A systematic, agent-native framework for reverse-engineering, modding, asset generation, and cross-game mashups across PC games you own.

> [!CAUTION]
> **STRICT SAFETY INVARIANTS (NON-NEGOTIABLE)**:
> 1. **Offline & Single-Player Only**: Modding is strictly restricted to offline single-player games, single-player campaigns, or private dedicated servers hosted by the user.
> 2. **Zero Anti-Cheat Bypass**: NEVER attach hooks, debuggers, or inject DLLs into games protected by active kernel or competitive anti-cheat (Easy Anti-Cheat, BattlEye, Vanguard, Ricochet, VAC). If detected during recon, abort runtime injection immediately.
> 3. **No Proprietary File Distribution**: Never distribute copyrighted base game binaries, raw decompiled dumps, or game assets. Ship only mod source code, patches (IPS/xdelta/Harmony), original assets, or procedural asset generators.
> 4. **Safe Lab Environment**: Always snapshot save games and user profiles with `um backup` before launching modified games. Never modify files directly in game directories without an isolated workspace or mod manager folder.

---

## The 10-Step Universal Modding Loop

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Prior Art │ ──> │ 2. Game Recon│ ──> │  3. Safe Lab │ ──> │4. Read Logic │
│  (um kb)     │     │  & Fingerprint│    │  (um backup) │     │ (Decompile)  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
│8. Record &   │ <── │ 7. In-Game   │ <── │ 6. Generate  │ <── 5. Slice │
│   Showcase   │     │  Verify (Win)│     │  Assets (fal/│     Mod Code │
└──────────────┘     └──────────────┘     │  Comfy/3D)   │     └────────┘
       │                                  └──────────────┘
       v
┌──────────────┐     ┌──────────────┐
│  9. Package  │ ──> │10. Field Note│
│  & Lint      │     │  (um kb pr)  │
└──────────────┘     └──────────────┘
```

---

### Step 1: Search Prior Art
Before touching game files, check documented engine behavior, hooks, and known traps:
```bash
um kb search "<game or engine>"
```
Inspect field notes in `knowledge/games/<game>/` for tested engine hooks, gotchas, and proven routes.

---

### Step 2: Recon & Fingerprint
Identify installation location, engine architecture, code runtime, and anti-cheat posture:
```bash
um scan "<Game Name or Path>"
```
Recon inspects:
- **Engine**: Unity (Mono vs IL2CPP), Unreal Engine (version, shipping build), Godot, .NET/XNA/FNA, Source 1/2, Custom C/C++, Java.
- **Code Type**: Managed CIL (.NET/Mono), Transpiled C++ (IL2CPP), Native PE x86/x64, JVM bytecode, Interpreted (GDScript, Lua, Python, Papyrus).
- **Security**: Anti-cheat drivers (`EasyAntiCheat.sys`, `BEService.exe`, `vgk.sys`), integrity packers (Denuvo, VMProtect, Themida).
- **Mod Ecosystem**: BepInEx, MelonLoader, tModLoader, SMAPI, Fabric, NeoForge, UE4SS, ScriptHookV, REFramework.
- **Save Directories**: `%APPDATA%`, `%LOCALAPPDATA%`, `Saved Games`, Steam Cloud `userdata`.

Produce a `MODDING_PLAN.md` with:
1. Target mechanic / feature specification.
2. Selected modding route and technical rationale.
3. Hook targets (method names, virtual offsets, memory addresses).
4. Asset requirements (dimensions, alpha, palette, animation frames).

---

### Step 3: Safe Lab Setup
Protect user progress and maintain a clean baseline:
```bash
# Snapshot save data and config
um backup create "<saves_path>" --name "<game>-premod"

# Verify restoration is functional
um backup list
```
Set up a clean mod workspace separate from the game directory. Use symlinks or mod loader staging folders instead of overwriting original game assets.

---

### Step 4: Read the Actual Code (Reverse Engineering)
Decompile or disassemble the target binary. Never guess logic or parameter signatures:
- **Managed .NET / Mono**:
  ```bash
  ilspycmd -p -o ./decompiled "<GamePath>/<Game>_Data/Managed/Assembly-CSharp.dll"
  ```
- **Unity IL2CPP**:
  Run `Cpp2IL` on `GameAssembly.dll` + `global-metadata.dat` to extract dummy C# stub assemblies with correct type definitions and method signatures.
- **Java (Minecraft / LibGDX)**:
  Decompile JARs using Vineflower or CFR.
- **Native C/C++ (Unreal, Custom Engines)**:
  - Generate SDK headers using Dumper-7 (Unreal) or Il2CppDumper.
  - Inspect call paths with Ghidra / IDA Pro or Frida dynamic traces.
  - Inspect GPU render state and shaders using RenderDoc.

> [!IMPORTANT]
> Store all decompiled outputs outside the mod repository (`.gitignore` decompiled folders). Never commit raw decompiled game source.

---

### Step 5: Route Selection & Slice Implementation
Always climb the route ladder from easiest to deepest:

| Level | Route | When to Use | Typical Tools |
| :--- | :--- | :--- | :--- |
| **0** | **Data / Config Overrides** | Tunables, JSON/XML/CSV edits, loose file injection | Text editor, script unpacker |
| **1** | **Official / Community Loader API** | Supported mod ecosystem exists | tModLoader, SMAPI, Fabric, UE4SS, ScriptHookV |
| **2** | **Managed Harmony Patching** | .NET / Unity Mono games without direct loader API | Harmony Lib (`[HarmonyPatch]`), BepInEx |
| **3** | **Native Proxy DLL / MinHook** | Native C++ engines, DirectX/Vulkan game loops | MinHook, `version.dll` proxy, SafetyHook |
| **4** | **Reimplementation / Engine Decomp** | Open-source engine ports (OpenMW, Ship of Harkinian) | C/C++ build systems, SDL2 |
| **5** | **Passthrough Mashup** | Cross-game bridging, dual-process IPC | Local WebSocket, Shared Memory, DXGI depth hook |

Build the minimum viable slice first (e.g. spawn 1 item, hook 1 log message, change 1 stat).

---

### Step 6: Asset Generation Pipeline
Match the game's exact visual and auditory language:
- **Local ComfyUI** (Port `8188`):
  ```bash
  um comfy image --prompt "<pixel art sprite, transparent background>" --sprite
  ```
- **fal.ai REST MCP / CLI**:
  ```bash
  um fal sprite --prompt "sci-fi plasma rifle, 32-bit pixel art" --out ./assets/rifle.png
  ```
- **Asset Normalization (`um sprite`)**:
  - `cutout`: Remove background artifacts and ensure crisp alpha channel.
  - `fit`: Nearest-neighbor scale to standard tile sizes (16x16, 32x32, 64x64).
  - `palette`: Quantize colors to the game's authentic color palette.
  - `sheet`: Pack multiple frames into animation sheets.
- **3D-to-Sprite Rendering (`um render3d`)**:
  Render 3D GLB/FBX models into isometric/directional 2D sprite headings (AoE2, StarCraft, Diablo style) using headless Blender.

---

### Step 7: In-Game Verification
Validate runtime behavior in a controlled windowed environment:
```bash
# Launch in windowed mode with logging
um win launch "<GamePath>/game.exe" --args "-windowed -log"

# Capture clean screenshot of modded element
um win shot --process "game.exe" --out ./receipts/verify.png
```
Check game logs (`Player.log`, `BepInEx/LogOutput.log`, `UE4SS.log`) for unhandled exceptions or missing assets.

---

### Step 8: Record & Showcase
Capture clean gameplay footage without system noise:
```bash
# Capture window video with process-loopback audio
um win record --process "game.exe" --duration 15 --out ./showcase/gameplay.mp4

# Generate contact sheets and cut showcase clip
um video contact ./showcase/gameplay.mp4
um video compile --edl ./showcase/edl.json --out ./showcase/final.mp4
```

---

### Step 9: Package & Lint
Run publication audits before creating release archives:
```bash
um publish check ./my-mod/
```
The linter verifies:
- No copyrighted game binaries (`.exe`, `.dll`, `.pak`, `.assets`) are packaged.
- No decompiled source code or proprietary schemas leak.
- No hardcoded API keys or personal access tokens exist.
- Manifest, documentation, and installation instructions are complete.

---

### Step 10: Document Field Notes (Knowledge Base)
Record reverse-engineering discoveries, engine quirks, and fixes for future agents:
```bash
# Create a new field note template
um kb new --game "<Game Title>" --title "<Feature / Topic>" --agent "Gaya"

# Verify formatting and schema compliance
um kb check knowledge/games/<game>/<feature>.md

# Submit PR to universal-modder knowledge base
um kb pr knowledge/games/<game>/<feature>.md
```

---

## Engine Playbook Quick Reference

See detailed procedures in [engine-playbooks.md](file:///C:/Users/rossi/.gemini/config/skills/universal-modder/references/engine-playbooks.md):
- **Unity**: Mono (BepInEx 5/6 + Harmony) vs IL2CPP (MelonLoader / BepInEx 6 Bleeding Edge + Il2CppInterop).
- **Unreal Engine**: UE4SS Lua scripting, UObject reflection hooks, and C++ SDK generation via Dumper-7.
- **.NET / XNA**: tModLoader (Terraria), SMAPI (Stardew Valley), Everest (Celeste).
- **Godot**: `pck` extraction via `gdsdecomp`, GDScript bytecode manipulation.
- **Bethesda**: Creation Kit plugin records (`.esp`/`.esm`), Papyrus script overrides, SKSE/F4SE native plugins.
- **Minecraft**: Fabric / NeoForge, Mixin injection points (`@Inject`, `@Redirect`, `@ModifyVariable`).
- **Native C++**: MinHook API detour hooks, proxy DLLs (`version.dll`, `dxgi.dll`).

---

## Cross-Game Mashup Patterns

See architecture patterns in [mashup-patterns.md](file:///C:/Users/rossi/.gemini/config/skills/universal-modder/references/mashup-patterns.md):
1. **Asset & Map Porting**: Extract geometry, textures, and skeletal animations from Source/Unreal into formats usable by Target game engine.
2. **Dual-Process Passthrough**: Run two game instances concurrently. Synchronize camera position, orientation, and game events over local IPC (WebSocket / Named Pipes). Example: Minecraft world rendering inside GTA V Los Santos.
3. **DXGI Frame & Depth Compositing**: Hook DirectX present loop to read color and depth buffers from guest engine, compositing them into host engine with occlusion.
4. **Decomp-as-Library**: Compile a decompiled retro game (Mario 64, Sonic CD, Diablo 1) as a headless shared library DLL, running game physics and simulation inside a host modern game.

---

## CLI Reference Guide

See complete command manual in [um-cli.md](file:///C:/Users/rossi/.gemini/config/skills/universal-modder/references/um-cli.md):
- `um scan`: Automated engine, architecture, loader, and anti-cheat fingerprinting.
- `um backup`: Save game snapshotting, diffing, and restoration.
- `um sprite`: Pixel-art optimization, cutout, palette fitting, sheet assembly.
- `um render3d`: Blender headless batch isometric/directional sprite rendering.
- `um win`: Game window capture, process loopback audio recording, isolated input driving.
- `um comfy`: Local ComfyUI workflow execution and sprite rendering.
- `um fal`: Cloud generative asset pipeline (2D, 3D, audio, video).
- `um kb`: Field notes knowledge base search, formatting check, and PR automation.
