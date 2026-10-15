---
name: gis-cartography-designer
description: >
  The visual design of maps — color, type, hierarchy, symbology, layout.
  Different from gis-analyst-type work (data processing) — this is making
  a map READABLE and BEAUTIFUL. DUM-E pool — fires when a deliverable
  includes a map that needs design treatment.
---

# GIS Cartography Designer
A map is a visual argument. Good cartography makes the argument readable in 5 seconds and explorable for 5 minutes.

## The cartographic hierarchy
Every map element gets a tier. Higher tier = more visual weight (size, contrast, position).

| Tier | Examples |
|---|---|
| **Primary** | The subject — the data you're showing (highlighted features, key labels) |
| **Secondary** | Context that helps interpret — major roads, city names, water bodies |
| **Tertiary** | Reference — minor labels, lighter contour, neighborhood labels |
| **Background** | Base — terrain, soft fill, faint admin boundaries |

If everything is bold, nothing is. Drop tertiary contrast 30%, background 50%.

## Color
- **Sequential** (single-hue gradient, light→dark): for ordered quantitative data (population density, elevation).
- **Diverging** (two hues meeting at midpoint): for data with a meaningful midpoint (above/below average, change from baseline).
- **Categorical** (distinct hues): for nominal data (land use types, agency boundaries). Max 7 categories — beyond that, distinguishability dies.
- **Steer from ColorBrewer or Carto's palette tools** — they're tested for colorblind-safety + print/screen behavior.
- **Avoid red+green together** — colorblind-unsafe; use red+blue or orange+blue.

## Typography
- **Serif** for labels of NATURAL features (rivers, mountains).
- **Sans-serif** for labels of CULTURAL features (cities, roads).
- **Italic** for water labels by convention; readers expect it.
- **Type hierarchy:** city → town → neighborhood = decreasing size, decreasing weight.
- **No more than 3 typefaces** on one map. Two is better.

## Layout (the surround)
A map artifact usually includes:
- The map itself
- **Title** (what is this showing? for whom?)
- **Legend** (what do the colors/symbols mean?)
- **Scale bar** (always; never just zoom-level)
- **North arrow** (only if north isn't up — most maps north is up by default)
- **Source citation** (where did the data come from? when?)
- **Inset / locator** (where in the world?)

Most map errors are missing legend or missing scale — readers can't trust what they can't reference.

## Symbology
- **Proportional symbols** for quantitative point data (circle size = magnitude).
- **Choropleth** for area-based rate data (NOT raw counts — normalize by area or population).
- **Heat maps** for density patterns; warn that they can mislead with sparse data.
- **Symbol consistency** within a series — same color = same thing across all maps in a report.

## Common cartographic mistakes
- Choropleth of raw population (always just shows where population is concentrated).
- Too many color categories (rainbow palettes that mean nothing).
- Tiny labels on busy basemaps (illegible at intended display size).
- No basemap thinning (every road labeled, drowning the data).
- Default GIS-software exports (look like 2003).

## Hard rules
- **Design for the display size.** A map on a 9"x12" print is different from a map on a 1920x1080 screen is different from a map embedded in a slide. Same data, different design.
- **Static map = different rules from interactive map.** Interactive can hide-and-reveal; static must show all critical info at once.
- **Test on a colorblind simulator.** ~8% of male readers have some form of color deficiency.

## Coordination
- Pair with `gis-3d-scene-developer` when the map is part of a 3D scene.
- Pair with `data-storytelling` when the map is part of a narrative report.
- Pair with `frontend-design` for web map UI.
- Surface to FRIDAY for visual treatment and brand consistency.
