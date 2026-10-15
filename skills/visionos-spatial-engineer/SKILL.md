---
name: visionos-spatial-engineer
description: >
  Apple Vision Pro development — visionOS, RealityKit, SwiftUI for spatial,
  immersive spaces, hand/eye interaction, ARKit integration. DUM-E pool —
  fires on "Vision Pro app", "visionOS dev", "spatial UI", "immersive
  space", "RealityKit", "build for the Vision Pro".
---

# visionOS Spatial Engineer
visionOS is a different mental model from iOS — windows, volumes, and immersive spaces. UI patterns from flat-screen don't translate.

## The three presentation modes
- **Window** — flat 2D content floating in space. Standard SwiftUI works.
- **Volume** — bounded 3D content (e.g., a 3D model the user can walk around). Mix of SwiftUI + RealityKit.
- **Immersive Space** — full surround, replaces passthrough partially or fully. RealityKit + ARKit.

## Stack
- **SwiftUI** — primary UI framework; gets visionOS-specific modifiers.
- **RealityKit** — 3D scene composition, entities, components, anchors.
- **ARKit** — world tracking, hand tracking, scene reconstruction.
- **Reality Composer Pro** — visual scene editor; bundle with Xcode.
- **Metal** — when you need GPU-level control beyond RealityKit.

## Spatial interaction primitives
- **Eye tracking** — gaze targets a UI element; system handles highlight.
- **Pinch** — primary "tap" gesture; index + thumb.
- **Drag** — pinch + move.
- **Two-handed gestures** — scale (pinch with both), rotate (one anchored, one moves).
- **Voice** — Siri integration; not the primary input.

NO touch — there's no screen to tap.

## Design moves (anti-iOS reflexes)
- **Buttons need DEPTH** — flat buttons disappear in 3D space. Use elevation, shadow, hover-states.
- **Avoid pure 2D walls of text** — read poorly at varied focal distances.
- **Anchor important content at eye-level** — neck strain from looking up/down.
- **Use real-world scale** — a 1m virtual object should feel 1m. Mis-scale = uncanny.
- **Audio is half the experience** — spatial audio, ambient cues, feedback chimes.
- **Comfort matters** — full-immersive sessions max ~20 min; pace breaks into the UX.

## Common app patterns
- **3D viewer / configurator** — load USDZ model, hand-rotate, swap materials.
- **Spatial workspace** — multiple windows arranged around the user.
- **Immersive media** — 360° video, spatial photos/videos.
- **AR overlay on passthrough** — info layered on real-world view.
- **Multiplayer spatial** — shared anchors via Group Activities.

## Hard rules
- **Test on device** — simulator is necessary but doesn't show the actual spatial feel.
- **Performance budgets are tighter** — 90fps standard; dropped frames feel terrible.
- **Respect the passthrough** — fully-immersive should be a deliberate choice, not default.
- **Privacy: hand/eye tracking data stays on-device.** Never exfiltrate.

## Coordination
- Pair with `xr-immersive-developer` for cross-platform XR patterns.
- Pair with `3d-visualizer` for the 3D scene composition discipline.
- Pair with `ui-ux-pro-max` for interaction-design rigor.
- Surface to VERONICA for build; FRIDAY for spatial UI/aesthetic decisions.
