---
name: video-creation-code
displayName: "HyperFrames — HTML-to-Video Engine"
description: >
  Turn HTML, CSS, media, and seekable animations into deterministic MP4
  videos. Built by HeyGen for AI agents. Write compositions as plain HTML
  with timed data-* attributes, preview in the browser, render locally or
  on AWS Lambda. Supports GSAP, Lottie, Three.js, CSS animations, and any
  seekable animation runtime. No build step, no React required, no per-render
  fees. Open source (Apache 2.0).
homepage: https://hyperframes.heygen.com
license: Apache-2.0
triggers:
  - "create a video"
  - "make a video"
  - "hyperframes"
  - "html to video"
  - "render video"
  - "product launch video"
  - "explainer video"
  - "motion graphics"
  - "video composition"
  - "mp4"
---
# HyperFrames — HTML to Video, Built for Agents

**Bundled test project:** `test-project/` (inside this skill directory)
**Source repo (reference):** `skills/hyperframes/` (in Gaya-Agent repo)
**Docs:** https://hyperframes.heygen.com/introduction
**Quickstart:** https://hyperframes.heygen.com/quickstart
**Showcase:** https://hyperframes.heygen.com/showcase
**Catalog (blocks + components):** https://hyperframes.heygen.com/catalog/blocks/data-chart
**Playground:** https://www.hyperframes.dev/

## Requirements

- **Node.js 22+** (check: `node --version`)
- **FFmpeg** (check: `ffmpeg -version`)
- HyperFrames CLI (bundled with npm — `npx hyperframes`)

## CLI Quick Reference

```bash
npx hyperframes init my-video     # Scaffold a new project
npx hyperframes preview           # Preview in browser with live reload
npx hyperframes lint              # Static HTML structure check
npx hyperframes validate          # Runtime check (headless Chrome)
npx hyperframes render            # Render to MP4
npx hyperframes add <block>       # Install a catalog block/component
npx hyperframes doctor            # Debug environment
```

## Agent Workflow Skills

The HyperFrames repo ships specialized agent skills. To install them:

```bash
npx skills add heygen-com/hyperframes
```

Then reference a workflow by name:

```
Using /product-launch-video, create a 30s promo from this URL: ...
Using /faceless-explainer, make a 60s video about this topic: ...
Using /website-to-video, turn this site into a walkthrough: ...
Using /pr-to-video, explain this PR as a changelog video: ...
Using /motion-graphics, make a 5s kinetic type title card: ...
Using /embedded-captions, add captions to this talking-head: ...
Using /graphic-overlays, package this interview with lower-thirds: ...
Using /general-video, make a 10s product bumper: ...
```

Workflow reference:
- `/product-launch-video` — Product URL/brief → promo up to ~3 min
- `/website-to-video` — General URL → site tour video
- `/faceless-explainer` — Topic/article → narrated explainer (no URL)
- `/embedded-captions` — Existing MP4 → captions added
- `/graphic-overlays` — Existing MP4 → kinetic titles, lower-thirds, data callouts
- `/pr-to-video` — GitHub PR → code-change explainer
- `/motion-graphics` — Short design-led motion (kinetic type, logo sting, chart hit)
- `/general-video` — Fallback for any other video creation
- `/remotion-to-hyperframes` — Port existing Remotion project

## Composition Contract

Every HyperFrames composition is a plain HTML file. Key rules:

### 1. Stage element
```html
<div id="stage" data-composition-id="my-video" data-start="0" data-width="1920" data-height="1080">
```

### 2. Timed clips need `class="clip"` + data attributes
```html
<video class="clip" data-start="0" data-duration="6" data-track-index="0" src="intro.mp4" muted playsinline></video>
<h1 class="clip" data-start="1" data-duration="4" data-track-index="1">Title</h1>
<audio data-start="0" data-duration="6" data-track-index="2" data-volume="0.5" src="music.wav"></audio>
```

### 3. Seekable animation (GSAP example)
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
  window.__timelines = window.__timelines || {};
  window.__timelines["my-video"] = tl;
</script>
```

### 4. MUST be deterministic
- No `Date.now()`, no unseeded `Math.random()`, no render-time network fetches
- Every asset must be local or a stable URL

### 5. Animations must be seekable
Paused timeline + registered on `window.__timelines`. GSAP is the primary adapter. Lottie, Three.js, Anime.js, WAAPI also supported via frame adapters.

## Workflow

```
1. PLAN     — Determine intent, length, input type → pick workflow
2. SCAFFOLD — `npx hyperframes init` or write HTML directly
3. BUILD    — Write composition HTML with data-* attributes + animation
4. LINT     — `npx hyperframes lint` (static check)
5. VALIDATE — `npx hyperframes validate` (runtime check)
6. PREVIEW  — `npx hyperframes preview` (browser, live reload)
7. RENDER   — `npx hyperframes render` → outputs MP4
```

## Common Video Dimensions

| Format | Resolution | Aspect Ratio |
|--------|-----------|--------------|
| Landscape | 1920×1080 | 16:9 |
| Portrait | 1080×1920 | 9:16 |
| Square | 1080×1080 | 1:1 |
| Vertical | 1080×1350 | 4:5 |

## Troubleshooting

- **"Command not found"** → Run `npx hyperframes` (bundled with npm)
- **Render fails** → Check FFmpeg: `ffmpeg -version`
- **Assets not loading** → Ensure paths are relative to the composition HTML
- **Animation not playing** → Verify timeline is `paused: true` and registered on `window.__timelines`
- **Preview works but render is blank** → Run `npx hyperframes validate`

## Bundled Test Project

A working test composition is bundled with this skill at `test-project/`:

```bash
# From this skill's directory:
cd test-project
npx hyperframes preview     # Preview in browser (localhost:3002)
npx hyperframes render      # Render to MP4
```

The test project includes:
- GSAP timeline with proper finite repeats (deterministic)
- Gradient text, glow pulse, progress bar
- CSS initial states (no JS visibility toggles)
- Clean validation (no infinite-repeat errors)
