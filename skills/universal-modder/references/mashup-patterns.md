# Cross-Game Mashup Architectural Patterns

A guide to bridging disparate game worlds, physics engines, and content formats into cohesive cross-game mashups.

---

## Pattern 1: Dual-Process Passthrough (Worked Example: Minecraft × GTA V)

Run two distinct game processes concurrently on the same machine, synchronizing cameras and world events over low-latency local IPC.

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│        Guest: Minecraft         │           │         Host: GTA V             │
│ (Fabric Mod / Headless Client)  │           │   (ScriptHookV + ReShade Addon) │
└───────────────┬─────────────────┘           └─────────────────┬───────────────┘
                │                                               │
                │             Local IPC (WebSocket)             │
                │ <===========================================> │
                │  - Host sends: Camera pos, FOV, look vector   │
                │  - Guest sends: World events, explosions      │
                │                                               │
                v                                               v
        [Render to Offscreen]                         [Composite Output Frame]
                │                                               ^
                └─────── DXGI Shared Handle / Shmem ────────────┘
                         (Depth Buffer + Color Buffer)
```

### 1. Camera & State Synchronization
- **Host (GTA V)**: A `ScriptHookV` C++ plugin extracts the active gameplay camera matrix (`x, y, z`, pitch, yaw, roll, FOV) at the start of each frame.
- **Transport**: Sends coordinate packets over a local WebSocket server (port `8080`) or Windows Named Pipe at 60 Hz.
- **Guest (Minecraft)**: A Fabric client mod listens to the stream, teleporting the player/camera entity to matching world coordinates and freezing game time/physics to match host cadence.

### 2. Event Exchange
- When Minecraft TNT explodes, the Fabric mod emits an event packet: `{ type: "explosion", pos: [x, y, z], radius: 10 }`.
- GTA V script catches the event and triggers a native explosion at the translated coordinates: `FIRE::ADD_EXPLOSION(pos.x, pos.y, pos.z, EXP_TAG_GRENADE, 10.0f, true, false, 0.5f)`.
- Damage dealt to host entities reports back to guest to sync NPC health.

### 3. Visual Depth Compositing
To prevent the guest game from merely floating on top of the host:
- The guest renderer copies its Color and Depth buffers into a DirectX 11/12 shared handle (`IDXGIResource::GetSharedHandle`).
- A custom ReShade add-on inside GTA V reads the shared surface in a post-processing pass.
- For each pixel:
  ```hlsl
  if (guestDepth < hostDepth) {
      return guestColor;
  } else {
      return hostColor;
  }
  ```
- This yields true occlusion: GTA skyscrapers naturally occlude Minecraft blocks behind them, while Minecraft blocks placed close to the camera occlude GTA roads.

---

## Pattern 2: Content Porting Pipeline (Halo Warthog into Minecraft)

Extracting functional mechanical assets from one game's file format and rebuilding them in another.

```
┌──────────────────────────┐
│  Source Game (Halo MCC)  │
│  - Model / Mesh (.tag)   │
│  - Audio (.sound)        │
│  - Physics values        │
└────────────┬─────────────┘
             │
             v Extract & Convert
┌──────────────────────────┐
│ Intermediate Assets      │
│ - Blender: Scale/Rig/UV  │
│ - ffmpeg: Convert to OGG │
│ - Extract speed, turn    │
└────────────┬─────────────┘
             │
             v Authoring
┌──────────────────────────┐
│ Target Game (Minecraft)  │
│ - Fabric Entity Class    │
│ - Custom EntityRenderer  │
│ - Turret Gunner Seat     │
└──────────────────────────┘
```

### Steps:
1. **Extraction**: Use engine-specific tools (`Reclaimer` for Halo, `Source IO` for Valve games, `UModel` for Unreal) to export meshes to `.obj`/`.gltf` and sounds to `.wav`.
2. **Asset Normalization**:
   - Align scale: 1 meter in source = 1 block in Minecraft.
   - Re-texture or downscale to maintain target game aesthetic (e.g. apply pixelation shader or palette quantization via `um sprite palette`).
3. **Behavioral Mapping**:
   Map source vehicle physics (acceleration curve, steering angle, passenger seat offsets) into target game entity classes.

---

## Pattern 3: Decomp-as-a-Library (Retro Sim in Modern Engine)

Compiling an open-source reverse-engineered engine into a headless dynamic library (`.dll`) to run identical original physics inside a new host.

### Architecture:
- Projects like **Ship of Harkinian** (Zelda 64), **OpenGOAL** (Jak & Daxter), or **Diablo 1 (DevilutionX)** provide fully decompiled game code.
- Strip graphics, audio, and platform event loops, leaving pure state simulation:
  ```cpp
  extern "C" __declspec(dllexport) void Sim_Init();
  extern "C" __declspec(dllexport) void Sim_Tick(InputState inputs);
  extern "C" __declspec(dllexport) GameState Sim_GetState();
  ```
- The host game (e.g. a Unity or Unreal sandbox) loads the DLL, inputs player actions into `Sim_Tick()`, and queries exact actor coordinates to render high-fidelity modern meshes matching original physics 1:1.
