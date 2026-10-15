---
name: curved-led-wall
description: >
  The canonical method for laying flat rectangular modules (LED cabinets,
  panels, screens, tiles) into a CURVED wall so adjacent modules touch
  edge-to-edge with no gaps or overlap. Fires when Katviz says "curved",
  "concave", "convex", "curve angle", "bend", or asks to arc/wrap a panel
  array — in any LED-wall, video-wall, or tiled-display tool (Three.js / R3F
  / canvas / SVG plan view). One common pivot, chord-based radius, panels span
  shared vertices. Use this geometry every time; do not re-derive.
version: 1.0.0
tags: [led-wall, curve, three-js, geometry, visual-rhyme, faceted-arc, chord]
---

# Curved LED Wall — Faceted-Arc Geometry

When modules are **rigid flat rectangles** of fixed width `cW`, a curve is a
**faceted arc** (a regular polygon segment), not a smooth bend. The only model
that makes neighbouring modules' side edges *meet* is the **chord-vertex** model
below. Apply it verbatim. Battle-tested in the Visual Rhyme LED Wall Planner
(`Desktop\LEDWallPlanner.jsx`), 2026-06-25.

## The rule
1. **Align flat first** — modules centered, spacing = `cW`.
2. **One common pivot** — a single circle; its centre is the shared pivot for every module.
3. **Split the input angle** — total curve angle `A` divides into `Δθ = A / cols` per module.
4. **Edges touch by construction** — each module is a *chord* spanning two shared corner vertices; neighbours share a vertex, so their edges meet.

## The math (this is the whole skill)
```
A      = curveAngle * π/180         // TOTAL subtended angle of the wall (user input, degrees)
cols   = number of modules across
Δθ     = A / cols                   // bend per module about the common pivot
R      = cW / (2 * sin(Δθ/2))       // CHORD radius — solved so each chord == one module width cW
sign   = concave ? +1 : -1          // concave wraps toward viewer (+z)

// Corner vertices on the circle, k = 0..cols  (module c spans vertex c → c+1)
vertX(k) = R * sin(-A/2 + k*Δθ)
vertZ(k) = sign * R * (1 - cos(-A/2 + k*Δθ))

// Module c position = midpoint of its two corner vertices (chord centre)
colX(c) = (vertX(c) + vertX(c+1)) / 2
colZ(c) = (vertZ(c) + vertZ(c+1)) / 2

// Module c facing = tangent at its mid-angle
colAngle(c) = -A/2 + (c + 0.5)*Δθ
rotationY(c) = -sign * colAngle(c)
```
Because `R` is solved from `cW`, every chord length == `cW` exactly, so adjacent
modules share vertex `c+1` and the side edges touch. A small bezel (e.g. render
width `cW*0.96`) leaves a realistic seam; widen toward `cW` for zero gap.

## Sanity checks (always run mentally before shipping)
- **Reduces to flat:** as `A → 0`, `colX(c) → (c - (cols-1)/2)*cW`, `colZ → 0`, `rotation → 0`. If your formula doesn't collapse to clean flat centering, it's wrong.
- **Edge-touch:** adjacent module centres are `cW` apart along the chord; corners coincide at shared vertices.
- **Any scale:** correct for *few* columns + *big* angle (where approximations explode) and many columns + small angle alike.
- **cols = 1:** single module, `colAngle = 0`, stays flat-facing (one panel can't curve). Guard divide-by-zero on `cols` and `Δθ`.

## Wrong models — do NOT use (already tried and failed)
- **Vertex distribution over `cols-1` + chord radius `wW/(2 sin(A/2))`** — places modules at column *vertices*, not centres; gaps + stagger. (Original bug.)
- **Centres-on-arc + arc-length radius `wW/A`** — puts each module centre *on* the circle at its mid-angle. Looks fine for many columns/small angle, but with few columns + big angle the modules drift apart and overlap because a flat chord's centre sits *inside* the arc at `R·cos(Δθ/2)`, not on it. (Second bug — the scatter Katviz caught.)
- Only the **chord-midpoint placement with chord-solved radius** (above) is exact.

## Apply to
3D viewport (Three.js cabinet meshes + support tubes + base, all driven by one
`colX/colZ/colAngle`), plan-view diagrams, and any "wrap N panels to X degrees"
request. Keep one set of helpers so structure and modules share the curve.
