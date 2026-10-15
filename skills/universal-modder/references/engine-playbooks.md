# Engine Playbooks & Reverse-Engineering Technical Guide

Concrete technical workflows for fingerprinting, hooking, decompiling, and modifying games across major game engines.

---

## 1. Unity Engine

Unity games run in one of two backends: **Mono** (managed .NET bytecode) or **IL2CPP** (ahead-of-time compiled C++).

### Fingerprinting Unity Backend
- **Mono**: Check `<Game>_Data/Managed/Assembly-CSharp.dll` and `mono-2.0-bdwgc.dll` in the game root.
- **IL2CPP**: Check for `GameAssembly.dll` in root and `<Game>_Data/il2cpp_data/Metadata/global-metadata.dat`.

### Route A: Unity Mono (Easiest)
1. **Decompilation**:
   ```bash
   ilspycmd -p -o ./decompiled "<GamePath>/<Game>_Data/Managed/Assembly-CSharp.dll"
   ```
2. **Mod Loader**: Install **BepInEx 5.x** (place BepInEx folder, `winhttp.dll`, and `doorstop_config.ini` in game root).
3. **Harmony Patching**:
   Write a C# plugin targeting `BaseUnityPlugin`:
   ```csharp
   using BepInEx;
   using HarmonyLib;

   [BepInPlugin("com.user.mod", "Sample Mod", "1.0.0")]
   public class SampleMod : BaseUnityPlugin {
       void Awake() {
           var harmony = new Harmony("com.user.mod");
           harmony.PatchAll();
           Logger.LogInfo("Mod loaded successfully!");
       }
   }

   [HarmonyPatch(typeof(PlayerController), "TakeDamage")]
   class Patch_PlayerController_TakeDamage {
       static bool Prefix(ref int damage) {
           // Modify damage or return false to skip original execution
           damage = 0; 
           return true; 
       }
   }
   ```
4. **Compile**: Compile with `dotnet build` targeting `net472` or `netstandard2.0` referencing game assemblies.

### Route B: Unity IL2CPP (Compiled Native)
1. **Decompilation & Metadata Extraction**:
   Run `Cpp2IL` on `GameAssembly.dll` and `global-metadata.dat`:
   ```bash
   cpp2il --game-path "<GamePath>" --exe-name "<Game>.exe" --analysis-level=3
   ```
   This generates dummy C# stub assemblies in `cpp2il_out/` showing all class layouts, field offsets, and method signatures.
2. **Mod Loader**: Use **MelonLoader** (IL2CPP build) or **BepInEx 6.x Bleeding Edge** with `Il2CppInterop`.
3. **Hooking**: Use `Il2CppInterop.Runtime.Injection` to hook unmanaged functions, or call Il2Cpp methods directly via generated wrappers.

---

## 2. Unreal Engine (UE4 / UE5)

Unreal Engine games compile down to native C++ with an extensive UObject reflection system.

### Fingerprinting Unreal Engine
- Check `<Game>/Binaries/Win64/<Game>-Win64-Shipping.exe`.
- Check `<Game>/Content/Paks/` for `.pak` files and `.ucas`/`.utoc` Zen Store containers.

### Route A: UE4SS (Unreal Engine 4/5 Scripting System)
The gold standard for Unreal Engine modding without source code:
1. **Installation**: Download UE4SS and place `UE4SS.dll` and `dwmapi.dll` (or proxy) into `<Game>/Binaries/Win64/`.
2. **Lua Scripting**:
   Add scripts in `<Game>/Binaries/Win64/Mods/<ModName>/scripts/main.lua`:
   ```lua
   -- Hook UFunction calls dynamically
   RegisterHook("/Script/Engine.PlayerController:ClientRestart", function(self)
       print("[Mod] PlayerController restarted!")
   end)

   -- Find UObjects in memory
   local player = FindFirstOf("BP_PlayerCharacter_C")
   if player:IsValid() then
       player.Health = 9999.0
   end
   ```
3. **SDK Header Dumping**:
   In `UE4SS-settings.ini`, enable `CXXHeaderGenerator = 1` or use **Dumper-7** to extract full C++ header representations of all engine and game types directly from the running process.

### Route B: Pak Patching (Data / Visuals / Audio)
1. **Unpacking**: Use `repak` or `UnrealPak` to extract `.pak` archives (check for AES encryption keys on community forums if encrypted).
2. **Cooking Overrides**: Using matching Unreal Engine Editor version, cook assets with identical relative paths (e.g. `Content/Characters/Hero/Hero_Mat.uasset`).
3. **Packing**: Pack into `<Game>/Content/Paks/~mods/<ModName>_P.pak` (the `_P` suffix forces Unreal's virtual file system to prioritize the patch).

---

## 3. .NET / XNA / MonoGame

Common for classic indie masterpieces: Terraria, Stardew Valley, Celeste.

### Terraria (tModLoader)
1. Use the official **tModLoader** environment on Steam or standalone.
2. Implement standard classes:
   ```csharp
   using Terraria.ModLoader;
   using Terraria.ID;

   public class NukeLauncher : ModItem {
       public override void SetDefaults() {
           Item.damage = 5000;
           Item.DamageType = DamageClass.Ranged;
           Item.width = 64;
           Item.height = 24;
           Item.useTime = 60;
           Item.useAnimation = 60;
           Item.useStyle = ItemUseStyleID.Shoot;
           Item.shoot = ProjectileID.RocketI;
           Item.shootSpeed = 16f;
       }
   }
   ```
3. Place textures at matching paths (e.g., `Items/NukeLauncher.png`). Build using `tModLoader` build menu or CLI.

### Stardew Valley (SMAPI)
1. Target **SMAPI** API (`StardewModdingAPI`).
2. Implement `Mod` class with event handlers:
   ```csharp
   public class ModEntry : Mod {
       public override void Entry(IModHelper helper) {
           helper.Events.GameLoop.DayStarted += OnDayStarted;
       }
       private void OnDayStarted(object sender, DayStartedEventArgs e) {
           this.Monitor.Log("A new day begins!", LogLevel.Info);
       }
   }
   ```

---

## 4. Godot Engine

Godot packages scenes, scripts, and assets into virtual file packs (`.pck` or embedded in the PE binary).

### Reverse Engineering & Modding
1. **Extraction**:
   Use `gdsdecomp` (Godot RE Tools) to extract `.pck` files:
   ```bash
   gdre_tools --headless --recover="<GamePath>/<Game>.pck" --output-dir="./extracted_project"
   ```
2. **Decompiling GDScript**:
   `gdsdecomp` decompiles compiled `.gdc` files back into readable `.gd` scripts.
3. **Mod Injection**:
   - Modern Godot 3.x/4.x supports PCK loading via `ProjectSettings.load_resource_pack("res://mod.pck")`.
   - Pack modified scripts and scenes back into a standalone `.pck` using Godot CLI:
     ```bash
     godot --headless --export-pack "Windows Desktop" ./mods/my_mod.pck
     ```

---

## 5. Bethesda Creation Engine (Skyrim / Fallout 4 / Starfield)

Bethesda games utilize structured master records (`.esm`), plugin patches (`.esp`), and compiled Papyrus scripts (`.pex`).

### Reverse Engineering & Tooling
1. **Records & FormIDs**: Use `xEdit` (SSEEdit / FO4Edit) to inspect, clean, and resolve FormID conflicts.
2. **Script Decompilation**:
   Decompile `.pex` files into source `.psc` files using `Champollion`:
   ```bash
   Champollion.exe "<ScriptPath>/SampleScript.pex" ./decompiled/
   ```
3. **Native Extenders**:
   Use **SKSE** (Skyrim Script Extender) or **F4SE** (Fallout 4 Script Extender) to write native C++ plugins that register custom Papyrus functions and hook engine internals.

---

## 6. Minecraft (Java Edition)

The bedrock of modern bytecode modding.

### Tooling & Architecture
1. **Loaders**: **Fabric** (lightweight, modern) or **NeoForge** (comprehensive).
2. **Mixin Injection Points**:
   Modify compiled Minecraft bytecode without replacing entire classes:
   ```java
   @Mixin(PlayerEntity.class)
   public class MixinPlayerEntity {
       @Inject(method = "tick", at = @At("HEAD"))
       private void onPlayerTick(CallbackInfo ci) {
           // Injected at start of player tick loop
       }
   }
   ```
3. **Decompilation**: Handled automatically in dev environment via Parchment/Mojmap mappings using `loom` or `moddevgradle`.

---

## 7. Native C/C++ Games (Custom Engines & Proprietary Runtimes)

When no managed runtime or loader exists, native hooking is required.

### Technique 1: DLL Sideloading / Proxy DLL
Place a custom DLL with the same name as a common dependency in the game executable directory:
- Common proxy targets: `version.dll`, `winhttp.dll`, `dxgi.dll`, `d3d11.dll`.
- The proxy exports all original functions, forwarding them to the real Windows DLL in `System32`, while executing mod code on `DLL_PROCESS_ATTACH`.

### Technique 2: MinHook Detours
Hook arbitrary functions by memory address or pattern scan:
```cpp
#include "MinHook.h"

typedef void (*fnDoAttack)(void* playerObj, int targetId);
fnDoAttack fpOriginalDoAttack = NULL;

void DetourDoAttack(void* playerObj, int targetId) {
    // Custom logic before
    printf("[Hook] Player attacked target %d\n", targetId);
    
    // Call original function
    fpOriginalDoAttack(playerObj, targetId);
}

void SetupHooks() {
    MH_Initialize();
    uintptr_t targetAddr = 0x140123450; // Found via Ghidra/x64dbg
    MH_CreateHook((LPVOID)targetAddr, &DetourDoAttack, (LPVOID*)&fpOriginalDoAttack);
    MH_EnableHook(MH_ALL_HOOKS);
}
```
