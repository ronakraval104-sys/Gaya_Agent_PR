---
name: procedural-3d-modeling
description: >
  The geometry-construction brain for ALL 3D work — building shapes,
  structures, and scenes from parameters and math rather than sculpting by
  hand. Fires when Katviz wants to model/build/generate 3D geometry: meshes,
  parametric solids, extrude/lathe/loft/sweep, booleans/CSG, curves & splines,
  arraying/tiling (flat or curved), instancing, pivots & transforms, UVs, mesh
  optimization. Tool-agnostic (Three.js / R3F, Blender bpy + Geometry Nodes,
  Unreal). This skill OWNS the geometry reasoning and delegates execution to
  the 3D specialists: 3d-visualizer (Three.js), unreal-engine-cpp-pro,
  archviz-optimizer, digital-twin-generation. curved-led-wall is one worked
  example of its arraying law.
version: 1.0.0
tags: [3d-modeling, procedural, parametric, geometry, three-js, blender, unreal, cad, mesh, splines]
---

# Procedural 3D Modeling — the construction brain

**Core belief:** any 3D form is *points → curves → surfaces → solids*, placed and
oriented by *transforms about pivots*, combined by *operations*. If you can name
the parameters and the rule, you can model it procedurally — repeatably, at any
scale, with a slider on every dimension. This skill is the reasoning layer; the
3D specialist skills are the hands.

## When I fire
"model / build / generate / construct" a 3D thing · parametric or procedural
geometry · extrude, revolve, loft, sweep, tube-along-curve · boolean / cut /
union · array / tile / repeat / instance · curve, spline, arc, bend · pivot,
align, rotate-about, transform order · UVs, seams · mesh too heavy / optimize.

## The pipeline (always reason in this order)
1. **Parameters** — list every dimension/count/angle that should be a knob. Name them.
2. **Points** — the defining coordinates (corners, path samples, profile).
3. **Curves** — splines/arcs through points (Catmull-Rom, Bézier, arc, polyline).
4. **Surfaces/Solids** — generate volume from curves (extrude/lathe/loft/sweep/primitive).
5. **Transform** — place + orient about the correct **pivot** (see Pivot Law).
6. **Operate** — boolean / merge / array / instance.
7. **Finish** — UVs, normals, materials, then **optimize** (merge, instance, LOD, dispose).
8. **Verify** — render and check against a degenerate case (see Sanity Law).

## Construction primitives (the verbs)
| Verb | Input → output | Use for |
|------|----------------|---------|
| **Primitive** | params → box/cyl/sphere/torus/cone | blocks, fast prototyping |
| **Extrude** | 2D profile + depth → prism | walls, signage, letters, slabs |
| **Lathe / Revolve** | profile + axis + angle → solid of revolution | bottles, columns, vases, lenses |
| **Loft** | series of profiles → skinned surface | hulls, transitions, terrain strips |
| **Sweep / Tube** | profile + path curve → swept solid | pipes, cables, rails, trim, mouldings |
| **Boolean (CSG)** | A ∪ ∩ − B | holes, cuts, joins, mortise/tenon |
| **Array / Tile** | unit + count + rule → repetition | grids, façades, LED walls, fences |
| **Instance** | one geometry, many transforms | forests, crowds, bolts — cheap at scale |

## Three load-bearing LAWS (these are where modeling goes wrong)

### 1. Pivot Law — transforms happen about a pivot, order matters
- Rotation/scale apply about the object's **local origin**. To rotate about an
  arbitrary point P: translate so P is at origin → rotate → translate back. Or
  parent to an empty/Group placed at P and rotate the parent.
- Order is **T·R·S** read right-to-left (scale, then rotate, then translate) in
  most engines. Changing order changes the result. Decide the pivot *before* you
  place geometry, not after.
- For symmetric arrays, model the **unit at the origin** centered, then place
  copies — never bake position into the unit.

### 2. Arraying Law — flat is centering; curved is a faceted arc
- **Flat tile c of N, width w:** center at `(c − (N−1)/2)·w`. Spacing = w. Done.
- **Curved (rigid flat modules):** it is a **faceted arc** (regular polygon
  segment), NOT a smooth bend. One common pivot (circle centre); each module is a
  **chord**; modules share corner vertices so edges touch. Radius solved from the
  module width: `R = w / (2·sin(Δθ/2))`, `Δθ = totalAngle/N`. Place each module at
  the **chord midpoint**, rotate to the tangent. → Full method + the two wrong
  models that scatter modules: **see `curved-led-wall` skill.** Always verify it
  reduces to flat centering as angle→0.
- Curved-along-a-path (signage on a wall, text on a ring): sample the path,
  orient each unit to the path tangent (Frenet) — same chord logic generalized.

### 3. Sanity Law — verify against a degenerate case, in a render
- Every parametric formula must **collapse cleanly** at its limits: angle→0 ⇒
  flat; count→1 ⇒ single unit; radius→∞ ⇒ straight. If it doesn't, it's wrong.
- Guard divide-by-zero on counts/angles (`Math.max(n−1, 1)`, skip when angle 0).
- **Present-in-scene ≠ correct.** Render headless and screenshot, or eyeball in
  the viewport — never trust the math alone. (Links `verification-before-completion`.)

## Curves & splines toolkit
- **Catmull-Rom** — smooth interpolation *through* points (paths, tubes). Cheap, intuitive.
- **Bézier / NURBS** — control-point shaping, exact CAD curves, font outlines.
- **Arc / circle** — exact radii; the faceted-arc backbone of the Arraying Law.
- **Polyline** — straight segments; the truth underneath every faceted curve.
- Sample density drives smoothness vs. cost — expose it as a parameter.

## Mesh hygiene & optimization (ship-ready geometry)
- **Merge** static geometry sharing a material → one draw call. **Instance**
  repeated geometry (`InstancedMesh` / particle systems) → thousands cheaply.
- Correct **normals** (recompute after edits), weld seams, keep **winding** consistent.
- **UVs**: unwrap before texturing; box/planar/cylindrical projections for fast cases.
- **LOD** for distance; **dispose** geometry+material on rebuild (no leaks).
- Heavy archviz/perf work → delegate to `archviz-optimizer`.

## Tool routing (this skill decides; specialists execute)
| Target | Route to | Notes |
|--------|----------|-------|
| Web / interactive / R3F | `3d-visualizer` | Three.js meshes, materials, controls |
| Unreal 5 / C++ / runtime | `unreal-engine-cpp-pro` | procedural meshes, UObjects, BP interop |
| Archviz / heavy scene perf | `archviz-optimizer` | instancing, LOD, draw-call budget |
| Avatars / photoreal humans | `digital-twin-generation` | scanned/generated likeness |
| **Blender** | inline here | `bpy` scripting + **Geometry Nodes** for non-destructive procedural graphs; modifiers (Array, Curve, Bevel, Boolean, Mirror, Subdiv) are the verbs above made native |

## Worked examples to reuse
- **Curved LED wall** — Arraying Law, faceted arc, edge-touching modules. (`curved-led-wall`)
- **Pipe/cable run** — Sweep a circle profile along a Catmull-Rom path; cap ends.
- **Parametric staircase** — Array a step unit; rise/run/count as knobs; pivot at stringer.
- **Façade panelization** — Tile a panel over a surface; flat → Arraying Law flat; curved wall → faceted arc.

## Operating discipline
Name the knobs first. Model the unit at the origin. Pick the pivot before placing.
Make the curve faceted when modules are rigid. Verify against the degenerate case
in a real render. Then optimize. Then ship.
