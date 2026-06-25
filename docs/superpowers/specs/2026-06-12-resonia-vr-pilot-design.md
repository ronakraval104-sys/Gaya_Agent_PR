# Resonia VR Fitter Training — POC Design

**Date:** 2026-06-12
**Status:** Approved by R0n
**Client:** Resonia Limited (formerly Sterlite Power Transmission Limited)
**Engagement:** Option B — Pilot-Only (₹9,60,000 + GST)
**Deadline:** 2026-06-15 (Monday client meeting)
**Build Days:** 2 (13-14 June 2026)

---

## 1. Background

### 1.1 Client Context

Resonia Limited has successfully completed India's first 106-tonne, 765kV transmission tower using **Double Arm Gin Pole (DAGP)** technology at the Vikramgarh site (K4CPTL Project, EPC partner: Tata Projects Limited). They have a 52-page SOP (Doc. Ref. RSL/MCH/SOP/DAGP/01, Rev 02, Jan 8 2026) detailing the complete tower erection process.

Resonia has identified a critical workforce skill gap — limited trained manpower for DAGP erection gangs. They plan to set up **30 VR headsets** for training across their centers.

### 1.2 Ryze Proposal

Our submitted proposal (Ref: RS-PROP-RESONIA-2026-001) includes four modules:
- **Module A:** AR/VR Immersive Training
- **Module B:** Simulation-Based Learning System
- **Module C:** Digital Twin Training Environment
- **Module D:** Analytics & Performance Tracking Engine

**Resonia has opted for Option B: Pilot-Only Engagement (₹9,60,000 + GST)** — Discovery + single VR module + basic analytics dashboard + 2-month pilot.

### 1.3 POC Objective

Build a working VR fitter training prototype to demo on Monday 15 June 2026 at the client meeting. The POC must:
- Demonstrate a fitter going through 4 key steps of DAGP tower erection
- Show real-time analytics on a live dashboard
- Run on a single Quest 2 (wireless, no PC tether) + laptop + phone hotspot
- Prove the concept is production-ready for 30-headset deployment

---

## 2. System Architecture

### 2.1 Deployment Topology

```
         ┌──────────────────┐
         │  Mobile Phone     │
         │  (WiFi Hotspot)   │  ← Creates local LAN
         └────────┬─────────┘
                  │
      ┌───────────┴────────────┐
      │                        │
┌─────┴──────┐          ┌─────┴──────────┐
│  Meta      │          │  Laptop         │
│  Quest 2   │          │  (Windows)      │
│            │          │                 │
│  WebXR     │◄─HTTP────│  Node.js        │
│  A-Frame   │  WS      │  Server         │
│  Browser   │          │                 │
│            │          │  Port 3000      │
└────────────┘          └────────┬────────┘
                                 │
                                 │ HDMI
                          ┌──────┴──────┐
                          │  Client TV   │
                          │  (Dashboard  │
                          │   Display)   │
                          └─────────────┘
```

### 2.2 Tech Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| **VR Runtime** | A-Frame | 1.7+ | WebXR on Quest browser, no build |
| **3D Rendering** | Three.js (via A-Frame) | r170+ | glTF model loading |
| **Multiplayer** | Networked-Aframe | 0.12+ | WebRTC peer sync |
| **Backend** | Node.js + Express | 20 LTS | I write 100%, zero config |
| **Real-time** | WebSocket (ws) + SSE | latest | Live dashboard updates |
| **Dashboard** | Chart.js | 4.x | Live bar/donut charts |
| **3D Assets** | Your Max models → glTF | — | You supply |
| **Network** | Phone hotspot | — | Zero cloud dependency |

### 2.3 Data Flow

```
VR Headset (Quest 2)                      Laptop (Node.js)                   TV (HDMI)
┌──────────────────┐     WebSocket      ┌─────────────────┐     SSE       ┌──────────────┐
│                  │───────────────────→│                 │──────────────→│              │
│  Step started    │                    │  Server stores  │               │  Dashboard   │
│  Step completed  │                    │  session state  │               │  updates in  │
│  Time per step   │                    │  timestamps     │               │  real-time   │
│  Score/accuracy  │                    │  per-user data  │               │              │
│  Safety errors   │                    │                 │               │              │
│                  │←───────────────────│                 │               │              │
│  Step validation │                    │  Sync broadcast │               │              │
└──────────────────┘                    └─────────────────┘               └──────────────┘
```

---

## 3. VR Training Module (Quest 2)

### 3.1 Scene Environment

- **Setting:** A leveled construction site pad with a partially erected tower section and a DAGP assembly on the ground
- **Scale:** 1:1 real-world scale
- **Lighting:** Daylight ambient (construction site feel)
- **Terrain:** Flat ground with reference markers for anchor points

### 3.2 3D Models Required (from you → glTF)

| Model | Description | Priority |
|---|---|---|
| Tower section | One lattice tower body section (4-6m) with connection lugs | High |
| DAGP Assembly | Double Arm Gin Pole — mast, arms, pulleys | High |
| Winch machine | 5-ton winch (on ground) | Medium |
| Wire rope / sling | Rigging cables with hooks | Medium |
| Safety barriers | Barricade poles + signage | Low |
| Ground layout | Leveled pad with anchor markers | Low |

### 3.3 The 4 Fitter Steps

#### Step 1: Inspect DAGP Components
**SOP Reference:** Checklist items 8-14
- **What the fitter does:** Approach the DAGP assembly. Look at highlighted inspection points. Confirm each is clear.
- **VR interaction:** Gaze/ray pointer on 4 inspection zones → each turns green when confirmed
- **Validation:** All 4 inspected → step complete
- **Error state:** Missing an inspection → "Incomplete inspection" warning

#### Step 2: Check Winch & Wire Ropes
**SOP Reference:** Checklist items 10-13
- **What the fitter does:** Walk to winch station. Pull rope tension test lever. Inspect hook condition.
- **VR interaction:** Grab rope → pull to test tension. Inspect hook (rotate with controller).
- **Validation:** Rope tension OK + hook confirmed → step complete
- **Error state:** Rope found damaged → "Tag out equipment" instruction

#### Step 3: Attach Rigging to Tower Section
**SOP Reference:** Instructions 29-35
- **What the fitter does:** Take rigging hook from DAGP arm, align to tower section lift point, connect.
- **VR interaction:** Drag rigging cable to tower lug → snap connection on alignment
- **Validation:** Both arms connected → step complete
- **Error state:** Wrong lug selected → "Check rigging diagram" overlay

#### Step 4: Safety Check & Signal Lift
**SOP Reference:** Instructions 36-43
- **What the fitter does:** Check load path clear (look left/right). Raise hand signal to winch operator. Confirm lift start.
- **VR interaction:** Turn head to visually sweep the load zone → perform hand signal (controller gesture) → press confirm
- **Validation:** Sweep complete + signal performed → step complete
- **Error state:** Load path not clear → "Stop! Worker in load zone" alert

### 3.4 UI/UX Elements

| Element | Position | Function |
|---|---|---|
| Step indicator | Top-center, persistent | Shows current step (1/4, 2/4, etc.) |
| Instruction card | Below center, fade-in | Text: "Inspect the DAGP mast for cracks" |
| Highlight glow | On interactive objects | Pulsing outline on interactable parts |
| Confirmation check | On step complete | Green checkmark + chime |
| Error flash | On mistake | Red border + error sound |
| Timer | Top-right | Elapsed time for current step |
| Score badge | End screen | Summary: steps correct, time, safety rating |

### 3.5 Multiplayer (Stretch)

**If time permits after single-player works:** Add a second trainee via Networked-Aframe.
- Second player appears as a floating head + hands
- Both see each other's step progress
- Dashboard shows both trainees' data

---

## 4. Dashboard (Laptop → TV via HDMI)

### 4.1 Layout

```
┌─────────────────────────────────────────────────────────────┐
│  RESONIA VR TRAINING — LIVE DASHBOARD          [[Trainee]]  │
│  Session: Demo_Monday_01                                     │
├────────────┬────────────────────┬────────────────────────────┤
│            │                    │                            │
│ STEP TRACK │  TIMING           │  DASHBOARD LEGEND          │
│            │                    │                            │
│ [1] Inspect│  Step 1:  0:32    │  ⬤ Future Planning         │
│     ✅     │  Step 2:  0:45    │                             │
│ [2] Winch  │  Step 3:  1:12    │  ⬜ 30-Headset Vision      │
│     ⬜     │  Step 4:  —        │                             │
│ [3] Rigging│  Total:   2:29    │  ⬤ Pilot (Aug 2026)       │
│     ⬜     │                    │                             │
│ [4] Signal │  ┌──────────┐     │  Option B: ₹9.6L           │
│     ⬜     │  │ Step     │     │                             │
│            │  │ Accuracy │     │  Includes: Full source,     │
│ SAFETY     │  │   82%    │     │  3D assets, analytics,      │
│ COMPLIANCE │  │          │     │  train-the-trainer          │
│    ✅ 92%  │  └──────────┘     │                             │
└────────────┴────────────────────┴────────────────────────────┘
```

### 4.2 Dashboard Panels

| Panel | Data | Update Rate |
|---|---|---|
| Step Tracker | Current step, completed steps with green checkmarks | Real-time |
| Timing | Per-step duration + total session time | Every second |
| Accuracy Gauge | Donut chart showing accuracy % (weighted by safety) | Per step complete |
| Safety Score | Running percentage of safety checks passed | Real-time |
| Session Log | Timestamped list of every action taken | Real-time |
| Future Vision | Static card showing 30-headset deployment + pilot next steps | Static |

### 4.3 Post-Session Summary

After training ends, the dashboard shows:
- **Session report card** — all 4 steps with pass/fail + time
- **Score breakdown** — accuracy, safety, speed ratings
- **Replay log** — chronological list of all actions with timestamps
- **Export** — one-click copy of session data (for client to take away)

---

## 5. Implementation Plan

### 5.1 Day 1 — Saturday 13 June

| Block | Task | Owner |
|---|---|---|
| AM | Scaffold Node.js server + WebSocket backend | Gaya |
| AM | Build VR scene (ground, tower section, DAGP from placeholder geometry) | Gaya |
| PM | Implement Step 1 (Inspect) — gaze/ray interaction + validation | Gaya |
| PM | Implement Step 2 (Winch Check) — grab/tension interaction | Gaya |
| Eve | Build Dashboard HTML + Chart.js layout | Gaya |
| Eve | Connect VR → Dashboard via WebSocket (live data flow) | Gaya |

### 5.2 Day 2 — Sunday 14 June

| Block | Task | Owner |
|---|---|---|
| AM | Implement Step 3 (Rigging) — drag-to-connect mechanic | Gaya |
| AM | Implement Step 4 (Safety Signal) — gesture + look sweep | Gaya |
| PM | Integrate all 4 steps into linear flow | Gaya |
| PM | Polish UI — step indicators, error states, instruction cards | Gaya |
| PM | Full end-to-end test on Node.js server | Gaya |
| PM | **R0n imports his Max models as glTF → replaces placeholders** | **R0n** |
| Eve | Final test on Quest 2 browser + dashboard on laptop | Both |
| Eve | Bug fixes + optimization | Gaya |

### 5.3 Monday 15 June — Showtime

| Time | Activity |
|---|---|
| Pre-meeting | Start Node.js server on laptop. Connect Quest to phone hotspot. HDMI to client TV. |
| Demo | Walk through 4 steps. Client watches live dashboard on TV. |
| Vision pitch | Show "30-Headset" card. Explain how this POC scales to full pilot. |

---

## 6. Files to Deliver

All files in `Ryze studio/2026-06-12-vr-fitter-training-poc/`:

```
docs/
  2026-06-12-resonia-vr-pilot-design.md    ← This document

server/
  server.js                                 ← Node.js backend (Express + WebSocket)

public/
  index.html                                ← Main VR training app (A-Frame)
  js/
    steps.js                                ← Step logic + validation
    multiplayer.js                          ← Networked-Aframe config
    audio-feedback.js                       ← Sound cues
  assets/
    models/
      tower-section.gltf                    ← Tower body (your export)
      dagp-assembly.gltf                    ← DAGP (your export)
      winch-machine.gltf                    ← Winch (your export)
      rigging-cable.gltf                    ← Cable + hooks
    textures/                               ← Any materials

dashboard/
  index.html                                ← Live dashboard (Chart.js)
  dashboard.js                              ← SSE consumer + chart rendering
```

---

## 7. Future Path (Post-POC)

### From POC → Pilot (Next 2 Months)

| Phase | Timeline | Deliverable |
|---|---|---|
| 1. Discovery | Weeks 1-2 | Site visit, scenario prioritization |
| 2. Prototype | Weeks 3-6 | Full VR module (7 scenarios) + refined analytics |
| 3. Pilot | Weeks 7-14 | Deploy at Resonia training center, 4-week pilot |
| 4. Scale | Post-pilot | 30 headset deployment, AR field guide, multi-language |

### From Pilot → Full Option A

The POC code (A-Frame + Node.js) is designed to scale:
- **Local → Cloud:** Replace Node.js with AWS/Azure backend
- **Single → Multiplayer:** Networked-Aframe already supports 30+ nodes
- **Dashboard → Full Analytics:** Chart.js visuals feed into Power BI
- **Quest 2 → Quest 4/3:** WebXR runs on any headset with browser

---

## 8. Risks & Mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| Max → glTF export has issues | Medium | Test export early Day 1. Use simple geo as fallback |
| Quest 2 browser performance | Low | A-Frame is optimized. Keep poly count low (<50K tris) |
| WebSocket drops on hotspot | Low | Auto-reconnect in client code. Offline fallback mode |
| Client asks for feature not in POC | Medium | "This is a POC — the pilot covers that." Redirect to proposal |
| Time overrun | Medium | Scope-lock: 4 steps only. Skip multiplayer if tight |

---

*Prepared by: Gaya (Ryze Studios AI Agent) for Ronak Raval*
*Document Version: 1.0*
*Classification: Confidential — Resonia Limited Engagement*
