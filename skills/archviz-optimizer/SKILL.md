# ArchViz Optimizer — UE5 Optimization for Architectural Visualization

**Domain:** Unreal Engine 5 / ArchViz / Real Estate Visualization
**Author:** Gaya (deployed for R0n, 30-May-2026)
**Prerequisites:** `unreal-engine-cpp-pro`

---

## When to Use

Activate when the user is optimizing an **Unreal Engine 5** project for **architectural visualization** purposes:
- ArchViz firm needs higher FPS in walkthroughs
- Draw calls too high in interior scenes
- LOD generation for furniture/assets
- Nanite/Lumen tuning for real estate
- Asset optimization for ArchViz pipelines
- Rendering pipeline optimization (forward/deferred)
- Memory budget management for large interior scenes

## NOT for
- Game development optimization (use `unreal-engine-cpp-pro`)
- Non-UE5 rendering (V-Ray, Corona, etc.)
- ArchViz *production* (modeling, texturing) — this is about *performance*

---

## Optimization Workflow

### Phase 1: DIAGNOSE
1. **Profile the scene** — Use `stat fps`, `stat unit`, `stat gpu` to find bottlenecks
2. **Identify the bottleneck type:**
   - **GPU-bound** (high draw calls, overdraw, shader complexity)
   - **CPU-bound** (game thread stalls, slow blueprints)
   - **Memory-bound** (texture streaming, mesh memory)

### Phase 2: TARGET

| Bottleneck | Primary Fix | Secondary Fix |
|---|---|---|
| High draw calls | Merge static meshes, HLOD | Instanced static meshes |
| Overdraw (glass/transparent) | Reduce layered transparent materials | Sort order optimization |
| Texture memory | Texture atlasing, size budget | Virtual Texture streaming |
| Lumen cost | Reduce Lumen scene cache resolution | Lower Lumen mesh SDF detail |
| Nanite overdraw | Mark small meshes as non-Nanite | Increase Nanite triangle threshold |
| Post-processing cost | Reduce PP blend count | Use lighter tonemapper |

### Phase 3: EXECUTE

**Draw Call Reduction:**
- Merge small static meshes into larger batches
- Use `InstancedStaticMesh` for repeated elements (chairs, lights, plants)
- Enable HLOD for distant views
- Reduce unique material count — share material instances

**LOD Strategy for Interiors:**
- 4 LODs per hero asset (0 for close examination)
- 2 LODs for secondary assets
- Auto LOD generation with correct screen sizes for interior distances
- Nanite for hero assets, traditional LOD for fill assets

**Nanite Settings:**
```
For hero furniture: Nanite ON, keep default
For walls/floors: keep static mesh (Nanite adds overhead at close range)
For small decor: Nanite OFF (too many small meshes break Nanite efficiency)
```

**Lumen Settings for ArchViz:**
```ini
r.Lumen.DiffuseIndirect.Allow=1
r.Lumen.Reflections.Allow=1
r.Lumen.Scene.Cache.DownsampleFactor=2   # 4 for performance, 1 for quality
r.Lumen.MeshSDF.DownsampleFactor=2        # Higher = faster but less detailed
```

### Phase 4: VERIFY
- **Before/after:** `stat fps`, `stat unit` screenshots
- **Target:** 60 FPS on target hardware (RTX 4060 laptop or equivalent)
- **Minimum acceptable:** 30 FPS stable
- **Check:** No visual quality regression in hero shots

---

## Common ArchViz Traps

| Trap | Why It's Bad | Fix |
|---|---|---|
| Alpha transparency on foliage | Kills fill rate, GPU-bound | Alpha-to-coverage, dithered opacity |
| Unique material per object | Skyrockets draw calls | Material atlasing, shared instances |
| High-res textures on everything | Memory bloat | Texture budget: 2K hero, 1K secondary |
| Real-time lighting everywhere | Lumen cost per light | Bake where possible, limit to 1-2 dynamic lights |
| Importing with merged UVs | Can't use LODs | Keep proper UV sets for LOD generation |

---

## Target Metrics

| Scenario | Target FPS | Notes |
|---|---|---|
| Interior walkthrough (small apt) | 60+ | RTX 4060 laptop, 1080p |
| Interior walkthrough (villa) | 45-60 | More geometry, more lights |
| Exterior + interior (large) | 30-45 | HLOD + distance culling critical |
| VR mode | 72+ (per eye) | Aggressive optimization required |
