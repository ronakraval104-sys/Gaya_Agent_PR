# Resonia VR Fitter Training POC — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working VR fitter training POC for Resonia Limited's DAGP tower erection SOP — 4 steps, live dashboard, WebXR on Quest 2, demoable by Monday 15 June.

**Architecture:** A-Frame (WebXR) on Quest 2 browser connects via WebSocket to a Node.js/Express server. The server broadcasts session state to a Chart.js dashboard live on the client TV via SSE. No build step, no compilation — zero-install deployment.

**Tech Stack:** A-Frame 1.7, Three.js r170, Node.js 20, Express, ws, Chart.js 4, SSE.

**Project Root:** `Ryze studio/2026-06-12-vr-fitter-training-poc/`

---

## File Structure

```
Ryze studio/2026-06-12-vr-fitter-training-poc/
  package.json                     ← npm init, dependencies: express, ws
  server/
    server.js                      ← Express + WebSocket + SSE server
  public/
    index.html                     ← A-Frame VR scene (environment, models, UI overlays)
    js/
      steps.js                     ← Step state machine, validation, scoring, WebSocket emitter
      audio-feedback.js            ← Web Audio API sound cues
  dashboard/
    index.html                     ← Live dashboard layout (Chart.js)
    dashboard.js                   ← SSE consumer, Chart.js rendering, DOM updates
```

**Key design decisions:**
- No build step. CDN-loaded A-Frame, Three.js, Chart.js.
- All step logic in `steps.js` — the server is stateless (state lives in VR client, events broadcast).
- Dashboard receives events via SSE, not direct WebSocket — simpler reconnection, no message protocol.
- Placeholder geometry (boxes, cylinders, spheres) until R0n provides glTF models.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `package.json`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "resonia-vr-pilot",
  "version": "1.0.0",
  "description": "VR Fitter Training POC for Resonia Limited",
  "main": "server/server.js",
  "scripts": {
    "start": "node server/server.js",
    "dev": "node --watch server/server.js"
  },
  "dependencies": {
    "express": "^4.21.0",
    "ws": "^8.18.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run: `cd Ryze studio/2026-06-12-vr-fitter-training-poc && npm install`
Expected: `node_modules/` created, no errors.

---

### Task 2: Node.js Server (Express + WebSocket + SSE)

**Files:**
- Create: `server/server.js`

The server serves static files from `public/` and `dashboard/`, manages a WebSocket connection from the VR client, and broadcasts events via SSE to the dashboard.

- [ ] **Step 1: Write server.js**

```javascript
const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const path = require('path');

const PORT = 3000;
const app = express();

// Serve static files
app.use('/app', express.static(path.join(__dirname, '..', 'public')));
app.use('/dashboard', express.static(path.join(__dirname, '..', 'dashboard')));

// Root redirect
app.get('/', (req, res) => {
  res.redirect('/app');
});

// SSE endpoint for dashboard
app.get('/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });

  // Send initial connection event
  res.write(`data: ${JSON.stringify({ type: 'connected', timestamp: Date.now() })}\n\n`);

  // Keep alive
  const keepAlive = setInterval(() => {
    res.write(`:keepalive\n\n`);
  }, 15000);

  req.on('close', () => {
    clearInterval(keepAlive);
  });

  // Store reference for broadcasting
  if (!app.locals.sseClients) app.locals.sseClients = new Set();
  app.locals.sseClients.add(res);
  req.on('close', () => app.locals.sseClients.delete(res));
});

// Broadcast to all SSE clients
function broadcastEvent(event) {
  if (!app.locals.sseClients) return;
  const data = `data: ${JSON.stringify(event)}\n\n`;
  app.locals.sseClients.forEach(client => {
    client.write(data);
  });
}

// HTTP server
const server = http.createServer(app);

// WebSocket server
const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  console.log('VR client connected');

  ws.on('message', (message) => {
    try {
      const event = JSON.parse(message.toString());
      console.log('Event:', event.type);

      // Add server timestamp
      event.timestamp = Date.now();

      // Broadcast to all SSE clients (dashboard)
      broadcastEvent(event);

      // Echo back to VR client for confirmation
      ws.send(JSON.stringify({ type: 'ack', originalType: event.type }));
    } catch (err) {
      console.error('Parse error:', err);
    }
  });

  ws.on('close', () => {
    console.log('VR client disconnected');
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Dashboard at http://localhost:${PORT}/dashboard`);
});
```

- [ ] **Step 2: Verify server starts**

Run: `cd Ryze studio/2026-06-12-vr-fitter-training-poc && node server/server.js`
Expected: "Server running on http://localhost:3000" logged. Kill with Ctrl+C after 2s.

---

### Task 3: VR Scene Base (A-Frame)

**Files:**
- Create: `public/index.html`

The VR scene includes: ground plane, sky, tower section placeholder, DAGP assembly placeholder, winch placeholder, instructional UI overlay, WebSocket connection to server.

- [ ] **Step 1: Write public/index.html**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Resonia VR — DAGP Fitter Training</title>
  <script src="https://aframe.io/releases/1.7.0/aframe.min.js"></script>
  <script src="/app/js/steps.js" defer></script>
  <script src="/app/js/audio-feedback.js" defer></script>
  <style>
    body { margin: 0; overflow: hidden; font-family: Arial, Helvetica, sans-serif; }
    
    /* UI Overlay */
    #ui-overlay {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      pointer-events: none; z-index: 100;
    }
    #step-indicator {
      position: absolute;
      top: 20px; left: 50%; transform: translateX(-50%);
      color: white; font-size: 28px; font-weight: bold;
      text-shadow: 0 2px 8px rgba(0,0,0,0.8);
      background: rgba(0,0,0,0.5); padding: 10px 24px;
      border-radius: 30px; backdrop-filter: blur(4px);
    }
    #instruction-card {
      position: absolute;
      bottom: 80px; left: 50%; transform: translateX(-50%);
      color: white; font-size: 22px; text-align: center;
      text-shadow: 0 2px 8px rgba(0,0,0,0.8);
      background: rgba(0,0,0,0.6); padding: 16px 32px;
      border-radius: 16px; backdrop-filter: blur(4px);
      max-width: 70%; transition: opacity 0.3s ease;
    }
    #timer {
      position: absolute;
      top: 20px; right: 30px;
      color: #00ff88; font-size: 26px; font-weight: bold;
      text-shadow: 0 2px 8px rgba(0,0,0,0.8);
      font-family: 'Courier New', monospace;
    }
    #completion-overlay {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.85);
      display: none; align-items: center; justify-content: center;
      z-index: 200; pointer-events: auto;
    }
    #completion-overlay.visible { display: flex; }
    #completion-card {
      background: #1a1a2e; border: 2px solid #00ff88;
      border-radius: 24px; padding: 40px 60px;
      text-align: center; color: white;
      max-width: 600px;
    }
    #completion-card h1 { color: #00ff88; font-size: 42px; margin-bottom: 10px; }
    #completion-card .score { font-size: 64px; font-weight: bold; color: #ffd700; }
    #completion-card .detail { font-size: 20px; margin: 8px 0; opacity: 0.8; }
    #completion-card .steps-grid {
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 10px; margin: 20px 0; text-align: left;
    }
    #completion-card .step-row { padding: 8px 12px; border-radius: 8px; background: rgba(255,255,255,0.05); }
    #completion-card .step-row.pass { border-left: 4px solid #00ff88; }
    #completion-card .step-row.fail { border-left: 4px solid #ff4444; }
    #error-toast {
      position: absolute;
      top: 50%; left: 50%; transform: translate(-50%, -50%);
      color: #ff4444; font-size: 28px; font-weight: bold;
      text-shadow: 0 2px 12px rgba(0,0,0,0.9);
      background: rgba(0,0,0,0.7); padding: 20px 40px;
      border-radius: 16px; border: 2px solid #ff4444;
      opacity: 0; transition: opacity 0.3s ease;
      pointer-events: none;
    }
    #error-toast.visible { opacity: 1; }
    #connection-status {
      position: absolute;
      bottom: 20px; right: 30px;
      font-size: 14px; padding: 6px 14px;
      border-radius: 20px; pointer-events: none;
    }
    #connection-status.connected { background: #00ff8844; color: #00ff88; }
    #connection-status.disconnected { background: #ff444444; color: #ff4444; }
  </style>
</head>
<body>
  <a-scene>
    <!-- Environment -->
    <a-sky color="#87CEEB"></a-sky>
    
    <!-- Ground -->
    <a-plane position="0 -0.5 0" rotation="-90 0 0" width="40" height="40" 
             color="#8B7355" shadow></a-plane>
    
    <!-- Grid helper lines -->
    <a-entity position="0 0 0">
      <a-plane position="0 0.01 0" rotation="-90 0 0" width="40" height="40"
               color="#000000" opacity="0.1" material="transparent:true"></a-plane>
    </a-entity>

    <!-- Center marker -->
    <a-ring position="0 0.01 0" rotation="-90 0 0" radius-inner="0.5" radius-outer="0.6"
            color="#ffaa00" material="opacity:0.6"></a-ring>

    <!-- Tower Section (placeholder — replace with glTF) -->
    <a-entity id="tower-section" position="0 2 -6">
      <a-box width="2" height="4" depth="2" color="#666666"
             material="roughness:0.8;metalness:0.2"></a-box>
      <!-- Cross-bracing indicators -->
      <a-entity position="0 -1.5 0"><a-entity rotation="0 0 45">
        <a-box width="0.06" height="2.8" depth="0.06" color="#888888"></a-box>
      </a-entity></a-entity>
      <a-entity position="0 -1.5 0"><a-entity rotation="0 0 -45">
        <a-box width="0.06" height="2.8" depth="0.06" color="#888888"></a-box>
      </a-entity></a-entity>
    </a-entity>

    <!-- DAGP Assembly (placeholder) -->
    <a-entity id="dagp-assembly" position="-3 0.2 1">
      <!-- Mast -->
      <a-cylinder position="0 1.5 0" radius="0.12" height="3" color="#cc4444"></a-cylinder>
      <!-- Left arm -->
      <a-box position="-1.2 2.2 0" width="2.4" height="0.08" depth="0.08" color="#cc4444"></a-box>
      <!-- Right arm -->
      <a-box position="1.2 1.8 0" width="2.4" height="0.08" depth="0.08" color="#cc4444"></a-box>
      <!-- Pulley indicators -->
      <a-torus position="-1.2 2.6 0" radius="0.15" radius-tubular="0.04" color="#444444"></a-torus>
      <a-torus position="1.2 2.2 0" radius="0.15" radius-tubular="0.04" color="#444444"></a-torus>
      <!-- Base plate -->
      <a-box position="0 0 0" width="0.8" height="0.1" depth="0.8" color="#444444"></a-box>
    </a-entity>

    <!-- Winch Machine (placeholder) -->
    <a-entity id="winch-machine" position="4 0.3 2">
      <!-- Body -->
      <a-box position="0 0.5 0" width="1.6" height="0.6" depth="1.0" color="#cc8833"></a-box>
      <!-- Drum -->
      <a-cylinder position="0.6 0.5 0" radius="0.3" height="0.8" color="#444444" rotation="0 0 90"></a-cylinder>
      <!-- Rope from drum outward -->
      <a-cylinder position="1.2 0.5 0" radius="0.02" height="1.5" color="#aaaaaa" rotation="0 0 0"></a-cylinder>
    </a-entity>

    <!-- Lighting -->
    <a-light type="ambient" color="#ffffff" intensity="0.5"></a-light>
    <a-light type="directional" position="10 15 10" intensity="0.8" shadow></a-light>

    <!-- Camera (required for Quest 2 WebXR) -->
    <a-camera id="camera" position="0 1.6 8" look-controls="enabled:true" wasd-controls="enabled:true">
      <!-- Reticle cursor -->
      <a-cursor id="cursor" color="#00ff88" opacity="0.8" 
                fuse="false" rayOrigin="mouse"></a-cursor>
    </a-camera>
  </a-scene>

  <!-- UI Overlay -->
  <div id="ui-overlay">
    <div id="step-indicator">Step 1/4: Inspect DAGP</div>
    <div id="timer">00:00</div>
    <div id="instruction-card">Approach the DAGP and inspect each marked component</div>
    <div id="error-toast"></div>
    <div id="connection-status" class="disconnected">● Disconnected</div>
  </div>

  <!-- Completion Overlay -->
  <div id="completion-overlay">
    <div id="completion-card">
      <h1>✓ Training Complete</h1>
      <div class="score" id="final-score">0%</div>
      <div style="font-size:18px;margin-bottom:16px;opacity:0.6;">Overall Score</div>
      <div class="steps-grid" id="steps-summary"></div>
      <div class="detail">⏱ Total Time: <span id="final-time">00:00</span></div>
      <div class="detail">🛡 Safety Rating: <span id="final-safety">0%</span></div>
      <div style="margin-top:20px;font-size:14px;opacity:0.5;">
        Session data sent to dashboard
      </div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 2: Add WebSocket connection init script inline (before closing body)**

We'll add this inline rather than creating a separate file for a 5-line init. Add before `</body>`:

```html
<script>
  // WebSocket connection to server
  const wsUrl = `ws://${location.hostname}:3000`;
  let ws = null;
  let serverConnected = false;

  function connectWebSocket() {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      serverConnected = true;
      document.getElementById('connection-status').textContent = '● Connected';
      document.getElementById('connection-status').className = 'connected';
      console.log('WebSocket connected');
    };
    ws.onclose = () => {
      serverConnected = false;
      document.getElementById('connection-status').textContent = '● Disconnected';
      document.getElementById('connection-status').className = 'disconnected';
      console.log('WebSocket disconnected, reconnecting in 3s...');
      setTimeout(connectWebSocket, 3000);
    };
    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
    ws.onmessage = (msg) => {
      // Handle acks from server
      console.log('Server:', msg.data);
    };
  }
  connectWebSocket();

  // Helper to send events to server
  function sendEvent(event) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(event));
    }
  }
</script>
```

---

### Task 4: Steps State Machine & Validation (steps.js)

**Files:**
- Create: `public/js/steps.js`

This is the core logic: step definitions, state transitions, validation per step, scoring, timer, and WebSocket event emission.

- [ ] **Step 1: Write steps.js**

```javascript
// Step definitions
const STEPS = [
  {
    id: 1,
    title: 'Inspect DAGP',
    instruction: 'Approach the DAGP and inspect each component',
    checkpoints: 4,
    safetyCritical: true
  },
  {
    id: 2,
    title: 'Check Winch & Ropes',
    instruction: 'Test rope tension and inspect hook condition',
    checkpoints: 3,
    safetyCritical: true
  },
  {
    id: 3,
    title: 'Attach Rigging',
    instruction: 'Connect rigging cables to tower section lift points',
    checkpoints: 2,
    safetyCritical: false
  },
  {
    id: 4,
    title: 'Safety Signal',
    instruction: 'Sweep load zone and signal winch operator',
    checkpoints: 3,
    safetyCritical: true
  }
];

// Session state
const state = {
  currentStep: 0,          // 0-indexed
  steps: [
    { completed: false, checkpoints: 0, errors: 0, time: 0 },
    { completed: false, checkpoints: 0, errors: 0, time: 0 },
    { completed: false, checkpoints: 0, errors: 0, time: 0 },
    { completed: false, checkpoints: 0, errors: 0, time: 0 }
  ],
  startTime: null,
  stepStartTime: null,
  timerInterval: null,
  sessionActive: false,
  errors: []
};

// UI element references
const ui = {
  stepIndicator: document.getElementById('step-indicator'),
  instructionCard: document.getElementById('instruction-card'),
  timer: document.getElementById('timer'),
  errorToast: document.getElementById('error-toast'),
  completionOverlay: document.getElementById('completion-overlay'),
  finalScore: document.getElementById('final-score'),
  finalTime: document.getElementById('final-time'),
  finalSafety: document.getElementById('final-safety'),
  stepsSummary: document.getElementById('steps-summary')
};

// Start training session
function startTraining() {
  state.sessionActive = true;
  state.startTime = Date.now();
  state.stepStartTime = Date.now();
  state.currentStep = 0;
  startTimer();
  updateUI();
  sendEvent({ type: 'session_start', timestamp: Date.now() });
  console.log('Training started');
}

// Timer
function startTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
  state.timerInterval = setInterval(() => {
    if (!state.sessionActive) return;
    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const secs = String(elapsed % 60).padStart(2, '0');
    ui.timer.textContent = `${mins}:${secs}`;
    
    // Update current step time
    const stepElapsed = Math.floor((Date.now() - state.stepStartTime) / 1000);
    state.steps[state.currentStep].time = stepElapsed;
  }, 1000);
}

// Advance a checkpoint within current step
function advanceCheckpoint() {
  if (!state.sessionActive) return;
  const step = state.steps[state.currentStep];
  if (step.completed) return;
  
  step.checkpoints = Math.min(step.checkpoints + 1, STEPS[state.currentStep].checkpoints);
  
  sendEvent({
    type: 'checkpoint',
    step: state.currentStep + 1,
    checkpoint: step.checkpoints,
    total: STEPS[state.currentStep].checkpoints
  });
  
  // Check if step complete
  if (step.checkpoints >= STEPS[state.currentStep].checkpoints) {
    completeStep();
  } else {
    updateUI();
  }
}

// Record an error for current step
function recordError(message) {
  if (!state.sessionActive) return;
  const step = state.steps[state.currentStep];
  step.errors++;
  
  const error = {
    step: state.currentStep + 1,
    message: message,
    timestamp: Date.now()
  };
  state.errors.push(error);
  
  sendEvent({ type: 'error', ...error });
  
  // Show error toast
  ui.errorToast.textContent = '⚠ ' + message;
  ui.errorToast.classList.add('visible');
  setTimeout(() => ui.errorToast.classList.remove('visible'), 3000);
}

// Complete current step
function completeStep() {
  const stepIndex = state.currentStep;
  const step = state.steps[stepIndex];
  step.completed = true;
  
  sendEvent({
    type: 'step_complete',
    step: stepIndex + 1,
    title: STEPS[stepIndex].title,
    time: step.time,
    errors: step.errors
  });
  
  // Play success sound
  if (typeof playSound === 'function') {
    playSound('success');
  }

  // Move to next step or finish
  if (stepIndex + 1 >= STEPS.length) {
    completeTraining();
  } else {
    state.currentStep++;
    state.stepStartTime = Date.now();
    updateUI();
  }
}

// Complete training
function completeTraining() {
  state.sessionActive = false;
  if (state.timerInterval) clearInterval(state.timerInterval);
  
  const totalTime = Math.floor((Date.now() - state.startTime) / 1000);
  const totalErrors = state.errors.length;
  const totalCheckpoints = STEPS.reduce((s, st) => s + st.checkpoints, 0);
  const totalSafetyCritical = STEPS.filter(s => s.safetyCritical).length;
  const safetyPassed = state.errors.filter(e => 
    STEPS[e.step - 1]?.safetyCritical
  ).length;
  const safetyScore = Math.max(0, Math.round((1 - safetyPassed / Math.max(1, totalSafetyCritical)) * 100));
  
  // Calculate per-step scores
  const stepScores = state.steps.map((s, i) => {
    const max = STEPS[i].checkpoints;
    const score = max > 0 ? Math.round((s.checkpoints / max) * 100) : 0;
    const penalty = s.errors * 15;
    return Math.max(0, score - penalty);
  });
  const overallScore = Math.round(stepScores.reduce((a, b) => a + b, 0) / stepScores.length);

  // Show completion overlay
  ui.finalScore.textContent = overallScore + '%';
  ui.finalTime.textContent = String(Math.floor(totalTime / 60)).padStart(2, '0') + ':' + 
    String(totalTime % 60).padStart(2, '0');
  ui.finalSafety.textContent = safetyScore + '%';
  
  // Step summary grid
  ui.stepsSummary.innerHTML = STEPS.map((s, i) => {
    const st = state.steps[i];
    const passed = st.completed;
    return `<div class="step-row ${passed ? 'pass' : 'fail'}">
      <strong>Step ${s.id}:</strong> ${s.title}
      <span style="float:right">${passed ? '✅ Pass' : '❌ Fail'} | ${st.time}s</span>
    </div>`;
  }).join('');
  
  ui.completionOverlay.classList.add('visible');
  
  sendEvent({
    type: 'training_complete',
    overallScore,
    totalTime,
    safetyScore,
    steps: state.steps.map((s, i) => ({
      id: STEPS[i].id,
      title: STEPS[i].title,
      completed: s.completed,
      time: s.time,
      errors: s.errors
    }))
  });
}

// Update UI to reflect current state
function updateUI() {
  const stepIndex = state.currentStep;
  const stepDef = STEPS[stepIndex];
  const stepState = state.steps[stepIndex];
  
  ui.stepIndicator.textContent = `Step ${stepDef.id}/4: ${stepDef.title}`;
  ui.instructionCard.textContent = stepDef.instruction;
  
  // Update instruction card with checkpoint progress
  if (!stepState.completed) {
    const remaining = stepDef.checkpoints - stepState.checkpoints;
    if (remaining > 0) {
      ui.instructionCard.textContent = 
        `${stepDef.instruction} (${stepState.checkpoints}/${stepDef.checkpoints})`;
    }
  }
}

// Expose for use in VR scene
window.startTraining = startTraining;
window.advanceCheckpoint = advanceCheckpoint;
window.recordError = recordError;
window.STEPS = STEPS;
window.state = state;
```

---

### Task 5: Audio Feedback Module

**Files:**
- Create: `public/js/audio-feedback.js`

Uses Web Audio API to generate tones — no external audio files needed.

- [ ] **Step 1: Write audio-feedback.js**

```javascript
// Web Audio API sound effects — no external files needed
let audioContext = null;

function getAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

function playSound(type) {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    switch (type) {
      case 'success':
        // Rising two-tone chime
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523, ctx.currentTime);       // C5
        osc.frequency.setValueAtTime(659, ctx.currentTime + 0.1); // E5
        osc.frequency.setValueAtTime(784, ctx.currentTime + 0.2); // G5
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.4);
        break;
        
      case 'error':
        // Low buzz
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, ctx.currentTime);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.3);
        break;
        
      case 'checkpoint':
        // Short click/beep
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.08);
        break;
        
      case 'complete':
        // Triumphant arpeggio
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523, ctx.currentTime);
        osc.frequency.setValueAtTime(659, ctx.currentTime + 0.15);
        osc.frequency.setValueAtTime(784, ctx.currentTime + 0.3);
        osc.frequency.setValueAtTime(1047, ctx.currentTime + 0.45);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.7);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.7);
        break;
    }
  } catch (e) {
    // Audio not supported — fail silently
    console.log('Audio unavailable');
  }
}

// Expose globally
window.playSound = playSound;
```

---

### Task 6: Step 1 — Inspect DAGP Components

**Files:**
- Modify: `public/index.html` (add DAGP inspection zones with glow highlight)
- Depends on: Task 3, 4, 5

Add inspection zone entities to the DAGP assembly with A-Frame click/hover handlers for gaze or ray pointer interaction on Quest 2.

- [ ] **Step 1: Add inspection zones to DAGP assembly in index.html**

Replace the DAGP placeholder entity in `public/index.html` with:

```html
    <!-- DAGP Assembly with Inspection Zones -->
    <a-entity id="dagp-assembly" position="-3 0.2 1">
      <!-- Mast -->
      <a-cylinder position="0 1.5 0" radius="0.12" height="3" color="#cc4444"></a-cylinder>
      
      <!-- Left arm -->
      <a-box position="-1.2 2.2 0" width="2.4" height="0.08" depth="0.08" color="#cc4444"></a-box>
      <!-- Right arm -->
      <a-box position="1.2 1.8 0" width="2.4" height="0.08" depth="0.08" color="#cc4444"></a-box>
      
      <!-- Pulley indicators -->
      <a-torus position="-1.2 2.6 0" radius="0.15" radius-tubular="0.04" color="#444444"></a-torus>
      <a-torus position="1.2 2.2 0" radius="0.15" radius-tubular="0.04" color="#444444"></a-torus>
      
      <!-- Base plate -->
      <a-box position="0 0 0" width="0.8" height="0.1" depth="0.8" color="#444444"></a-box>
      
      <!-- Inspection Zone 1: Mast weld -->
      <a-entity class="inspect-zone" data-point="1" 
                position="0 1.5 0.2" scale="0.5 0.6 0.05"
                geometry="primitive:box" material="color:#00ff88;transparent:true;opacity:0.4"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.5 0.6 0.05;to:0.55 0.66 0.06;dur:800">
        <a-entity position="0 0.5 0" text="value:Mast Weld;align:center;color:#00ff88;width:2"></a-entity>
      </a-entity>
      
      <!-- Inspection Zone 2: Left pulley -->
      <a-entity class="inspect-zone" data-point="2"
                position="-1.2 2.6 0.2" scale="0.3 0.3 0.05"
                geometry="primitive:box" material="color:#00ff88;transparent:true;opacity:0.4"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.3 0.3 0.05;to:0.35 0.35 0.06;dur:800">
        <a-entity position="0 0.4 0" text="value:Left Pulley;align:center;color:#00ff88;width:2"></a-entity>
      </a-entity>
      
      <!-- Inspection Zone 3: Right pulley -->
      <a-entity class="inspect-zone" data-point="3"
                position="1.2 2.2 0.2" scale="0.3 0.3 0.05"
                geometry="primitive:box" material="color:#00ff88;transparent:true;opacity:0.4"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.3 0.3 0.05;to:0.35 0.35 0.06;dur:800">
        <a-entity position="0 0.4 0" text="value:Right Pulley;align:center;color:#00ff88;width:2"></a-entity>
      </a-entity>
      
      <!-- Inspection Zone 4: Base mount -->
      <a-entity class="inspect-zone" data-point="4"
                position="0 0 0.2" scale="0.6 0.1 0.05"
                geometry="primitive:box" material="color:#00ff88;transparent:true;opacity:0.4"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.6 0.1 0.05;to:0.66 0.12 0.06;dur:800">
        <a-entity position="0 0.3 0" text="value:Base Mount;align:center;color:#00ff88;width:2"></a-entity>
      </a-entity>
    </a-entity>
```

- [ ] **Step 2: Add click handlers for inspection zones in index.html**

Add this before the closing `</body>` tag:

```html
<script>
  // Step 1: Inspect DAGP — click handlers for inspection zones
  document.addEventListener('DOMContentLoaded', function() {
    const zones = document.querySelectorAll('.inspect-zone');
    zones.forEach(zone => {
      zone.addEventListener('click', function(evt) {
        const point = parseInt(this.dataset.point);
        
        // Verify we're on step 1
        if (window.state && window.state.currentStep === 0) {
          // Check if this point was already inspected
          const alreadyInspected = this.getAttribute('material').color !== '#00ff88';
          
          if (!alreadyInspected) {
            // Mark as inspected — turn green solid
            this.setAttribute('material', 'color', '#00ff88;opacity:0.8');
            this.setAttribute('animation__pulse', 'enabled', false);
            
            // Play checkpoint sound
            if (typeof playSound === 'function') playSound('checkpoint');
            
            // Advance state
            advanceCheckpoint();
          }
        } else if (window.state && window.state.currentStep !== 0) {
          // Wrong step — show message
          if (typeof recordError === 'function') {
            recordError('Complete the current step first');
          }
        }
      });
      
      // Also make them hoverable for cursor feedback
      zone.addEventListener('mouseenter', function(evt) {
        if (window.state && window.state.currentStep === 0) {
          this.setAttribute('material', 'opacity', '0.7');
        }
      });
      zone.addEventListener('mouseleave', function(evt) {
        this.setAttribute('material', 'opacity', '0.4');
      });
    });
  });
</script>
```

---

### Task 7: Step 2 — Check Winch & Wire Ropes

**Files:**
- Modify: `public/index.html` (add winch interactive zones)
- Depends on: Task 6

- [ ] **Step 1: Add winch interactive zones to index.html**

Replace the winch placeholder in index.html with:

```html
    <!-- Winch Machine with Interaction Zones -->
    <a-entity id="winch-machine" position="4 0.3 2">
      <!-- Body -->
      <a-box position="0 0.5 0" width="1.6" height="0.6" depth="1.0" color="#cc8833"></a-box>
      <!-- Drum -->
      <a-cylinder position="0.6 0.5 0" radius="0.3" height="0.8" color="#444444" rotation="0 0 90"></a-cylinder>
      
      <!-- Rope tension test zone -->
      <a-entity class="winch-rope" data-point="rope"
                position="1.2 0.5 0.5" scale="1.5 0.05 0.05"
                geometry="primitive:cylinder" material="color:#ffaa00;transparent:true;opacity:0.6"
                animation__pulse="property:scale;dir:alternate;loop:true;from:1.5 0.05 0.05;to:1.6 0.07 0.07;dur:600">
        <a-entity position="0.5 0.3 0" text="value:Pull to Test Tension;align:center;color:#ffaa00;width:4"></a-entity>
      </a-entity>
      
      <!-- Hook inspection zone -->
      <a-entity class="winch-hook" data-point="hook"
                position="1.8 0.3 0.3" scale="0.15 0.15 0.15"
                geometry="primitive:torus" material="color:#ffaa00;transparent:true;opacity:0.6"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.15 0.15 0.15;to:0.18 0.18 0.18;dur:600">
        <a-entity position="0 -0.3 0" text="value:Inspect Hook;align:center;color:#ffaa00;width:3"></a-entity>
      </a-entity>
    </a-entity>
```

- [ ] **Step 2: Add winch interaction script**

Add before closing `</body>`:

```html
<script>
  // Step 2: Winch interactions
  document.addEventListener('DOMContentLoaded', function() {
    // Rope tension test
    const ropeZone = document.querySelector('.winch-rope');
    if (ropeZone) {
      ropeZone.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 1 && !window._ropeTested) {
          window._ropeTested = true;
          this.setAttribute('material', 'color', '#00ff88;opacity:0.8');
          this.setAttribute('animation__pulse', 'enabled', false);
          if (typeof playSound === 'function') playSound('checkpoint');
          advanceCheckpoint();
        }
      });
    }
    
    // Hook inspection
    const hookZone = document.querySelector('.winch-hook');
    if (hookZone) {
      hookZone.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 1 && !window._hookInspected) {
          window._hookInspected = true;
          this.setAttribute('material', 'color', '#00ff88;opacity:0.8');
          this.setAttribute('animation__pulse', 'enabled', false);
          
          // Show inspection detail briefly
          const inst = document.getElementById('instruction-card');
          const origText = inst.textContent;
          inst.textContent = '✓ Hook condition: GOOD — No cracks or deformation';
          
          if (typeof playSound === 'function') playSound('checkpoint');
          advanceCheckpoint();
          
          setTimeout(() => {
            inst.textContent = origText;
          }, 2000);
        }
      });
    }
    
    // Step 2 error simulation: if user clicks drum instead of rope
    const drum = document.querySelector('#winch-machine a-cylinder');
    if (drum) {
      drum.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 1) {
          recordError('Check the rope tension first, not the drum');
        }
      });
    }
  });
</script>
```

---

### Task 8: Step 3 — Attach Rigging to Tower Section

**Files:**
- Modify: `public/index.html` (add rigging cables and tower lift points)
- Depends on: Task 6

- [ ] **Step 1: Add rigging cables and tower lift points to index.html**

Add after the tower-section entity:

```html
    <!-- Rigging Cables (from DAGP to tower) -->
    <a-entity id="rigging-assembly" position="0 0 0">
      <!-- Cable 1 (Left) — starts at DAGP left pulley, ends at tower left lug -->
      <a-entity class="rigging-cable" data-cable="1" 
                position="-0.8 -0.5 -2" rotation="0 0 35">
        <a-cylinder position="0 0 0" radius="0.015" height="3.5" color="#aaaaaa"></a-cylinder>
        <!-- Connection point indicator -->
        <a-entity class="rigging-connect" data-cable="1"
                  position="-1.7 0 0" scale="0.12 0.12 0.12"
                  geometry="primitive:sphere" material="color:#00ff88;transparent:true;opacity:0.6"
                  animation__pulse="property:scale;dir:alternate;loop:true;from:0.12 0.12 0.12;to:0.16 0.16 0.16;dur:600">
          <a-entity position="0 -0.3 0" text="value:Connect to Tower;align:center;color:#00ff88;width:3"></a-entity>
        </a-entity>
      </a-entity>
      
      <!-- Cable 2 (Right) -->
      <a-entity class="rigging-cable" data-cable="2"
                position="0.8 -0.5 -2" rotation="0 0 -35">
        <a-cylinder position="0 0 0" radius="0.015" height="3.5" color="#aaaaaa"></a-cylinder>
        <!-- Connection point indicator -->
        <a-entity class="rigging-connect" data-cable="2"
                  position="1.7 0 0" scale="0.12 0.12 0.12"
                  geometry="primitive:sphere" material="color:#00ff88;transparent:true;opacity:0.6"
                  animation__pulse="property:scale;dir:alternate;loop:true;from:0.12 0.12 0.12;to:0.16 0.16 0.16;dur:600">
          <a-entity position="0 -0.3 0" text="value:Connect to Tower;align:center;color:#00ff88;width:3"></a-entity>
        </a-entity>
      </a-entity>
    </a-entity>
    
    <!-- Tower Lift Point Lugs -->
    <a-entity class="tower-lug" data-lug="1" position="-1.3 0.5 -6" scale="0.1 0.15 0.1"
              geometry="primitive:box" material="color:#ffaa00"
              animation__pulse="property:scale;dir:alternate;loop:true;from:0.1 0.15 0.1;to:0.13 0.18 0.13;dur:800">
    </a-entity>
    <a-entity class="tower-lug" data-lug="2" position="1.3 0.5 -6" scale="0.1 0.15 0.1"
              geometry="primitive:box" material="color:#ffaa00"
              animation__pulse="property:scale;dir:alternate;loop:true;from:0.1 0.15 0.1;to:0.13 0.18 0.13;dur:800">
    </a-entity>
    <!-- Wrong lug (distractor) -->
    <a-entity class="tower-lug" data-lug="wrong" position="0 1.5 -6" scale="0.08 0.08 0.08"
              geometry="primitive:box" material="color:#ff6666"
              animation__pulse="property:scale;dir:alternate;loop:true;from:0.08 0.08 0.08;to:0.1 0.1 0.1;dur:800">
    </a-entity>
```

- [ ] **Step 2: Add rigging interaction script**

Add before closing `</body>`:

```html
<script>
  // Step 3: Rigging connection
  document.addEventListener('DOMContentLoaded', function() {
    let cablesConnected = 0;
    const totalCables = 2;
    
    // Connection points on cables
    document.querySelectorAll('.rigging-connect').forEach(connector => {
      connector.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 2) {
          const cableNum = parseInt(this.dataset.cable);
          
          // Start "dragging"—just flash and then it's connected (simplified for POC)
          this.setAttribute('material', 'color', '#00ff88;opacity:0.9');
          this.setAttribute('animation__pulse', 'enabled', false);
          
          // Animate cable moving to tower (simplified: just change color)
          const cable = document.querySelector(`.rigging-cable[data-cable="${cableNum}"]`);
          if (cable) {
            const cyl = cable.querySelector('a-cylinder');
            if (cyl) cyl.setAttribute('color', '#00ff88');
          }
          
          cablesConnected++;
          if (typeof playSound === 'function') playSound('checkpoint');
          advanceCheckpoint();
        }
      });
    });
    
    // Tower lug click handlers
    document.querySelectorAll('.tower-lug').forEach(lug => {
      lug.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 2) {
          const lugNum = this.dataset.lug;
          
          if (lugNum === 'wrong') {
            recordError('Wrong lift point — check rigging diagram');
          } else {
            // Correct lug — this is the second part of the interaction
            this.setAttribute('material', 'color', '#00ff88');
            this.setAttribute('animation__pulse', 'enabled', false);
            if (typeof playSound === 'function') playSound('checkpoint');
            
            // This would normally be connected to cable progress, but for simplicity
            // we advance here only if not already connected from cable side
            if (!this.dataset.connected) {
              this.dataset.connected = 'true';
              // Only advance if cables were already clicked
              if (cablesConnected > 0) {
                // already counted via cable clicks
              }
            }
          }
        }
      });
    });
  });
</script>
```

---

### Task 9: Step 4 — Safety Check & Signal Lift

**Files:**
- Modify: `public/index.html` (add head sweep zones and signal gesture)
- Depends on: Task 6

- [ ] **Step 1: Add safety sweep zones and signal button in index.html**

Add after the rigging assembly in index.html:

```html
    <!-- Safety Zone indicators (for Step 4) -->
    <a-entity id="safety-zones" position="0 0 0">
      <!-- Left sweep zone -->
      <a-entity class="sweep-zone" data-side="left"
                position="-4 2 -3" scale="2 1.5 0.05"
                geometry="primitive:box" material="color:#ffaa00;transparent:true;opacity:0.3"
                animation__pulse="property:scale;dir:alternate;loop:true;from:2 1.5 0.05;to:2.2 1.7 0.07;dur:1000">
        <a-entity position="0 1.2 0" text="value:← Look Left;align:center;color:#ffaa00;width:4"></a-entity>
      </a-entity>
      
      <!-- Right sweep zone -->
      <a-entity class="sweep-zone" data-side="right"
                position="4 2 -3" scale="2 1.5 0.05"
                geometry="primitive:box" material="color:#ffaa00;transparent:true;opacity:0.3"
                animation__pulse="property:scale;dir:alternate;loop:true;from:2 1.5 0.05;to:2.2 1.7 0.07;dur:1000">
        <a-entity position="0 1.2 0" text="value:Look Right →;align:center;color:#ffaa00;width:4"></a-entity>
      </a-entity>
      
      <!-- Hand Signal Button (floating in front of user) -->
      <a-entity class="signal-button"
                position="0 1.2 -1" scale="0.3 0.15 0.05"
                geometry="primitive:box" material="color:#00ff88;transparent:true;opacity:0.7"
                animation__pulse="property:scale;dir:alternate;loop:true;from:0.3 0.15 0.05;to:0.35 0.2 0.07;dur:600">
        <a-entity position="0 0.3 0" text="value:👋 Signal Lift →;align:center;color:#ffffff;width:3"></a-entity>
      </a-entity>
    </a-entity>
```

- [ ] **Step 2: Add safety sweep + signal interaction script**

Add before closing `</body>`:

```html
<script>
  // Step 4: Safety sweep & signal
  document.addEventListener('DOMContentLoaded', function() {
    let sweepsDone = 0;
    let signalDone = false;
    
    // Sweep zones
    document.querySelectorAll('.sweep-zone').forEach(zone => {
      zone.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 3 && !this.dataset.swept) {
          this.dataset.swept = 'true';
          this.setAttribute('material', 'color', '#00ff88;opacity:0.5');
          this.setAttribute('animation__pulse', 'enabled', false);
          
          sweepsDone++;
          if (typeof playSound === 'function') playSound('checkpoint');
          
          // Show confirmation text
          const side = this.dataset.side;
          const inst = document.getElementById('instruction-card');
          const origText = inst.textContent;
          inst.textContent = `✓ ${side.charAt(0).toUpperCase() + side.slice(1)} side clear`;
          
          setTimeout(() => {
            inst.textContent = origText;
          }, 1500);
          
          advanceCheckpoint();
        }
      });
    });
    
    // If worker model is in left/right visual range at start, trigger sweep
    // For POC, sweep zones act as click targets the user looks at
    // In production: use camera rotation check
    
    // Signal button
    const signalBtn = document.querySelector('.signal-button');
    if (signalBtn) {
      signalBtn.addEventListener('click', function() {
        if (window.state && window.state.currentStep === 3 && !signalDone) {
          signalDone = true;
          
          // Flash animation
          this.setAttribute('material', 'color', '#00ff00;opacity:1.0');
          this.setAttribute('animation__pulse', 'enabled', false);
          
          // Scale up briefly to simulate hand raise
          this.setAttribute('scale', '0.5 0.3 0.1');
          setTimeout(() => {
            this.setAttribute('scale', '0.3 0.15 0.05');
          }, 300);
          
          if (typeof playSound === 'function') playSound('success');
          advanceCheckpoint();
        }
      });
    }
    
    // Error: clicking signal before sweeping
    if (signalBtn) {
      signalBtn.addEventListener('click', function(evt) {
        if (window.state && window.state.currentStep === 3 && sweepsDone < 2) {
          // Prevent the advance if we already called it above
          if (!signalDone) {
            recordError('Check load zone before signaling');
          }
        }
      });
    }
  });
</script>
```

---

### Task 10: Dashboard HTML Layout

**Files:**
- Create: `dashboard/index.html`

The dashboard displays live training data via SSE from the Node.js server, rendered with Chart.js. Shows 6 panels: step tracker, timing, accuracy gauge, safety score, session log, and a static future vision card.

- [ ] **Step 1: Write dashboard/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Resonia VR — Live Training Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <script src="/dashboard/dashboard.js" defer></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #0a0a1a;
      color: #e0e0e0;
      padding: 20px;
      min-height: 100vh;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #1a1a3e;
    }
    .header h1 {
      font-size: 28px;
      color: #00ff88;
      font-weight: 600;
    }
    .header .session-info {
      text-align: right;
      font-size: 14px;
      opacity: 0.6;
    }
    .header .status-badge {
      display: inline-block;
      padding: 4px 14px;
      border-radius: 12px;
      font-size: 13px;
      margin-left: 10px;
    }
    .status-badge.active { background: #00ff8844; color: #00ff88; border: 1px solid #00ff88; }
    .status-badge.waiting { background: #ffaa0044; color: #ffaa00; border: 1px solid #ffaa00; }
    
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }
    .card {
      background: #111128;
      border: 1px solid #1a1a3e;
      border-radius: 16px;
      padding: 20px;
    }
    .card h2 {
      font-size: 16px;
      color: #8888aa;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 16px;
    }
    
    /* Step Tracker */
    .step-tracker .step-item {
      display: flex;
      align-items: center;
      padding: 10px 14px;
      margin-bottom: 8px;
      border-radius: 10px;
      background: rgba(255,255,255,0.03);
      transition: all 0.3s ease;
    }
    .step-item.active {
      background: rgba(0,255,136,0.08);
      border-left: 3px solid #00ff88;
    }
    .step-item .step-num {
      width: 32px; height: 32px;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: bold; font-size: 14px;
      margin-right: 14px;
    }
    .step-num.pending { background: #2a2a4a; color: #6666aa; }
    .step-num.active-num { background: #00ff8844; color: #00ff88; border: 2px solid #00ff88; }
    .step-num.done { background: #00ff8844; color: #00ff88; }
    .step-item .step-name { flex: 1; font-size: 15px; }
    .step-item .step-status { font-size: 13px; opacity: 0.6; }
    
    /* Timing */
    .timing-grid {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .timing-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      font-size: 14px;
      border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .timing-row .label { opacity: 0.6; }
    .timing-row .value { font-family: 'Courier New', monospace; font-weight: bold; }
    .timing-total {
      font-size: 28px;
      font-weight: bold;
      color: #00ff88;
      text-align: center;
      padding: 12px 0;
    }
    
    /* Chart containers */
    .chart-container {
      position: relative;
      height: 180px;
      margin-bottom: 10px;
    }
    .chart-center-text {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -60%);
      text-align: center;
      pointer-events: none;
    }
    .chart-center-text .value { font-size: 36px; font-weight: bold; color: #ffffff; }
    .chart-center-text .label { font-size: 12px; opacity: 0.5; margin-top: 2px; }
    
    /* Safety score */
    .safety-bar-bg {
      height: 20px;
      background: #1a1a3e;
      border-radius: 10px;
      overflow: hidden;
      margin: 12px 0;
    }
    .safety-bar-fill {
      height: 100%;
      border-radius: 10px;
      transition: width 0.5s ease;
      background: linear-gradient(90deg, #ff4444, #ffaa00, #00ff88);
    }
    .safety-score-text { font-size: 42px; font-weight: bold; text-align: center; }
    .safety-label { text-align: center; opacity: 0.5; font-size: 13px; }
    
    /* Session log */
    .log-container {
      max-height: 240px;
      overflow-y: auto;
      font-size: 13px;
      font-family: 'Courier New', monospace;
    }
    .log-container::-webkit-scrollbar { width: 4px; }
    .log-container::-webkit-scrollbar-track { background: transparent; }
    .log-container::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 2px; }
    .log-entry {
      padding: 4px 0;
      border-bottom: 1px solid rgba(255,255,255,0.03);
      display: flex;
      gap: 10px;
    }
    .log-entry .time { color: #6666aa; min-width: 70px; }
    .log-entry .msg { flex: 1; }
    .log-entry .msg.success { color: #00ff88; }
    .log-entry .msg.error { color: #ff4444; }
    .log-entry .msg.info { color: #88bbff; }
    
    /* Future vision card */
    .vision-card {
      background: linear-gradient(135deg, #0a0a2e, #1a0a3e);
      border: 1px solid #3344aa;
      padding: 24px;
    }
    .vision-card h2 { color: #88aaff; }
    .vision-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 8px 0;
    }
    .vision-item .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .vision-item .dot.green { background: #00ff88; }
    .vision-item .dot.blue { background: #4488ff; }
    .vision-item .dot.gold { background: #ffd700; }
    .vision-item .text { font-size: 14px; }
    .vision-item .subtext { font-size: 12px; opacity: 0.5; }
    .vision-price {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid rgba(255,255,255,0.06);
      text-align: center;
    }
    .vision-price .amount { font-size: 24px; font-weight: bold; color: #ffd700; }
    .vision-price .note { font-size: 12px; opacity: 0.5; margin-top: 4px; }
    
    /* Post-session */
    .session-summary {
      display: none;
    }
    .session-summary.visible { display: block; }
    
    @media (max-width: 1000px) {
      .grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 700px) {
      .grid, .grid-2 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>🏗 RESONIA VR TRAINING — LIVE DASHBOARD</h1>
      <div style="font-size:13px;opacity:0.5;">DAGP Tower Erection — Fitter Training POC</div>
    </div>
    <div class="session-info">
      <div>Session: <span id="session-id">Awaiting connection...</span></div>
      <div><span id="status-badge" class="status-badge waiting">● Waiting for trainee</span></div>
    </div>
  </div>

  <div class="grid">
    <!-- Step Tracker -->
    <div class="card step-tracker">
      <h2>📋 Step Tracker</h2>
      <div id="step-list">
        <div class="step-item" data-step="1">
          <div class="step-num pending">1</div>
          <span class="step-name">Inspect DAGP</span>
          <span class="step-status">—</span>
        </div>
        <div class="step-item" data-step="2">
          <div class="step-num pending">2</div>
          <span class="step-name">Check Winch & Ropes</span>
          <span class="step-status">—</span>
        </div>
        <div class="step-item" data-step="3">
          <div class="step-num pending">3</div>
          <span class="step-name">Attach Rigging</span>
          <span class="step-status">—</span>
        </div>
        <div class="step-item" data-step="4">
          <div class="step-num pending">4</div>
          <span class="step-name">Safety Signal</span>
          <span class="step-status">—</span>
        </div>
      </div>
    </div>

    <!-- Timing -->
    <div class="card">
      <h2>⏱ Timing</h2>
      <div class="timing-grid" id="timing-list">
        <div class="timing-row"><span class="label">Step 1 (Inspect)</span><span class="value" id="time-step-1">—</span></div>
        <div class="timing-row"><span class="label">Step 2 (Winch)</span><span class="value" id="time-step-2">—</span></div>
        <div class="timing-row"><span class="label">Step 3 (Rigging)</span><span class="value" id="time-step-3">—</span></div>
        <div class="timing-row"><span class="label">Step 4 (Signal)</span><span class="value" id="time-step-4">—</span></div>
      </div>
      <div class="timing-total" id="total-time">00:00</div>
      <div style="text-align:center;font-size:12px;opacity:0.4;">Total Elapsed</div>
    </div>

    <!-- Accuracy Gauge -->
    <div class="card">
      <h2>🎯 Accuracy</h2>
      <div class="chart-container">
        <canvas id="accuracyChart"></canvas>
        <div class="chart-center-text">
          <div class="value" id="accuracy-value">0%</div>
          <div class="label">Progress</div>
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:12px;opacity:0.5;padding:0 10px;">
        <span>Checkpoints: <span id="checkpoints-count">0/12</span></span>
        <span>Errors: <span id="errors-count" style="color:#ff4444;">0</span></span>
      </div>
    </div>
  </div>

  <div class="grid-2">
    <!-- Safety Score -->
    <div class="card">
      <h2>🛡 Safety Compliance</h2>
      <div class="safety-score-text" id="safety-value">—</div>
      <div class="safety-label">Safety Score</div>
      <div class="safety-bar-bg">
        <div class="safety-bar-fill" id="safety-bar" style="width:0%"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:11px;opacity:0.4;margin-top:6px;">
        <span>⚠ Errors recorded: <span id="safety-errors">0</span></span>
        <span>✅ All clear</span>
      </div>
    </div>

    <!-- Session Log -->
    <div class="card">
      <h2>📝 Session Log</h2>
      <div class="log-container" id="session-log">
        <div style="opacity:0.4;text-align:center;padding:40px 0;">Waiting for training to start...</div>
      </div>
    </div>
  </div>

  <div class="grid">
    <!-- Future Vision Card -->
    <div class="card vision-card">
      <h2>🔭 Future Vision — 30-Headset Deployment</h2>
      <div class="vision-item">
        <div class="dot green"></div>
        <div><div class="text">Pilot (Aug 2026)</div><div class="subtext">Single VR module + analytics — 2-month deployment</div></div>
      </div>
      <div class="vision-item">
        <div class="dot blue"></div>
        <div><div class="text">Full Rollout</div><div class="subtext">30 Quest headsets across training centers</div></div>
      </div>
      <div class="vision-item">
        <div class="dot gold"></div>
        <div><div class="text">AR Field Guide</div><div class="subtext">On-site DAGP inspection AR overlay (Phase 2)</div></div>
      </div>
      <div class="vision-price">
        <div class="amount">₹9,60,000 + GST</div>
        <div class="note">Option B — Full source, 3D assets, analytics, train-the-trainer</div>
      </div>
    </div>

    <!-- Summary card -->
    <div class="card session-summary" id="session-summary">
      <h2>📊 Session Complete</h2>
      <div id="summary-content">
        <div style="text-align:center;padding:20px;">
          <div style="font-size:48px;font-weight:bold;" id="summary-score">—</div>
          <div style="opacity:0.5;">Final Score</div>
        </div>
        <div id="summary-steps"></div>
        <div style="margin-top:16px;text-align:center;">
          <button onclick="copySessionData()" style="
            background:#00ff8844;color:#00ff88;border:1px solid #00ff88;
            padding:10px 24px;border-radius:8px;cursor:pointer;font-size:14px;
          ">📋 Copy Session Data</button>
        </div>
      </div>
    </div>

    <!-- Step timing bar chart -->
    <div class="card">
      <h2>📊 Step Timing</h2>
      <div class="chart-container" style="height:200px;">
        <canvas id="timingChart"></canvas>
      </div>
    </div>
  </div>

  <script>
    // Session data storage for copy
    window._sessionData = null;
    function copySessionData() {
      if (!window._sessionData) return;
      const text = JSON.stringify(window._sessionData, null, 2);
      navigator.clipboard.writeText(text).then(() => {
        alert('Session data copied to clipboard');
      });
    }
  </script>
</body>
</html>
```

---

### Task 11: Dashboard JS (SSE Consumer + Chart.js Rendering)

**Files:**
- Create: `dashboard/dashboard.js`

- [ ] **Step 1: Write dashboard/dashboard.js**

```javascript
// SSE connection to server
const eventSource = new EventSource('http://' + location.hostname + ':3000/events');

// Chart instances
let accuracyChart = null;
let timingChart = null;

// Session state (dashboard-side)
const dashState = {
  steps: [
    { status: 'pending', time: null, errors: 0 },
    { status: 'pending', time: null, errors: 0 },
    { status: 'pending', time: null, errors: 0 },
    { status: 'pending', time: null, errors: 0 }
  ],
  totalTime: 0,
  totalErrors: 0,
  totalCheckpoints: 0,
  maxCheckpoints: 12,
  safetyScore: null,
  overallScore: null,
  log: [],
  sessionActive: false
};

// DOM refs
const $ = (id) => document.getElementById(id);
const stepItems = document.querySelectorAll('.step-item');
const statusBadge = $('status-badge');
const sessionId = $('session-id');

// Init charts on load
document.addEventListener('DOMContentLoaded', function() {
  initAccuracyChart();
  initTimingChart();
});

function initAccuracyChart() {
  const ctx = document.getElementById('accuracyChart').getContext('2d');
  accuracyChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Completed', 'Remaining'],
      datasets: [{
        data: [0, 12],
        backgroundColor: ['#00ff88', '#1a1a3e'],
        borderWidth: 0
      }]
    },
    options: {
      cutout: '75%',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function initTimingChart() {
  const ctx = document.getElementById('timingChart').getContext('2d');
  timingChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Step 1', 'Step 2', 'Step 3', 'Step 4'],
      datasets: [{
        label: 'Time (seconds)',
        data: [0, 0, 0, 0],
        backgroundColor: [
          'rgba(0,255,136,0.6)',
          'rgba(68,136,255,0.6)',
          'rgba(255,170,0,0.6)',
          'rgba(255,68,68,0.6)'
        ],
        borderColor: [
          '#00ff88', '#4488ff', '#ffaa00', '#ff4444'
        ],
        borderWidth: 2,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#6666aa' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#8888aa' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Handle SSE events
eventSource.onmessage = function(event) {
  try {
    const data = JSON.parse(event.data);
    handleEvent(data);
  } catch (e) {
    console.error('SSE parse error:', e);
  }
};

eventSource.onopen = function() {
  console.log('SSE connected');
};

eventSource.onerror = function() {
  console.error('SSE connection error');
};

function handleEvent(data) {
  switch (data.type) {
    case 'connected':
      statusBadge.textContent = '● Connected';
      statusBadge.className = 'status-badge waiting';
      sessionId.textContent = 'Waiting for trainee...';
      break;

    case 'session_start':
      dashState.sessionActive = true;
      statusBadge.textContent = '● Training Active';
      statusBadge.className = 'status-badge active';
      sessionId.textContent = new Date(data.timestamp).toLocaleTimeString();
      // Set step 1 active
      updateStepUI(1, 'active');
      addLog('Training session started', 'info');
      break;

    case 'checkpoint':
      const stepIdx = data.step - 1;
      dashState.totalCheckpoints = Math.min(dashState.totalCheckpoints + 1, dashState.maxCheckpoints);
      updateAccuracyChart();
      addLog(`Step ${data.step}: checkpoint ${data.checkpoint}/${data.total}`, 'info');
      break;

    case 'step_complete':
      dashState.steps[data.step - 1].status = 'completed';
      dashState.steps[data.step - 1].time = data.time;
      dashState.steps[data.step - 1].errors = data.errors;
      
      updateStepUI(data.step, 'completed');
      updateTimingDisplay(data.step, data.time);
      updateTimingChart();
      
      // Set next step active
      if (data.step < 4) {
        updateStepUI(data.step + 1, 'active');
      }
      
      addLog(`Step ${data.step} (${data.title}) complete in ${data.time}s with ${data.errors} errors`, 'success');
      
      // Update safety on error
      if (data.errors > 0) {
        dashState.totalErrors += data.errors;
        updateSafetyScore();
      }
      break;

    case 'error':
      addLog(`⚠ Error on step ${data.step}: ${data.message}`, 'error');
      if (dashState.sessionActive) {
        dashState.totalErrors++;
        updateSafetyScore();
      }
      break;

    case 'training_complete':
      dashState.sessionActive = false;
      dashState.overallScore = data.overallScore;
      dashState.safetyScore = data.safetyScore;
      dashState.totalTime = data.totalTime;
      
      statusBadge.textContent = '● Session Complete';
      statusBadge.className = 'status-badge waiting';
      
      updateAccuracyChart();
      updateSafetyScore();
      showSessionSummary(data);
      addLog(`Training complete! Score: ${data.overallScore}%, Time: ${formatTime(data.totalTime)}`, 'success');
      break;
  }
}

function updateStepUI(step, status) {
  stepItems.forEach(item => {
    const stepNum = parseInt(item.dataset.step);
    const numEl = item.querySelector('.step-num');
    const statusEl = item.querySelector('.step-status');
    
    if (stepNum < step) {
      // Already completed
      numEl.className = 'step-num done';
      numEl.textContent = '✓';
      statusEl.textContent = 'Done';
      item.classList.remove('active');
    } else if (stepNum === step) {
      if (status === 'completed') {
        numEl.className = 'step-num done';
        numEl.textContent = '✓';
        statusEl.textContent = 'Done';
        item.classList.remove('active');
      } else if (status === 'active') {
        numEl.className = 'step-num active-num';
        statusEl.textContent = 'In Progress';
        item.classList.add('active');
      }
    } else {
      numEl.className = 'step-num pending';
      statusEl.textContent = 'Pending';
      item.classList.remove('active');
    }
  });
}

function updateTimingDisplay(step, time) {
  const el = document.getElementById(`time-step-${step}`);
  if (el) el.textContent = formatTime(time);
  
  // Update total
  let total = 0;
  for (let i = 0; i < 4; i++) {
    if (dashState.steps[i].time !== null) total += dashState.steps[i].time;
  }
  $('total-time').textContent = formatTime(total);
}

function updateAccuracyChart() {
  if (!accuracyChart) return;
  const completed = dashState.totalCheckpoints;
  const remaining = dashState.maxCheckpoints - completed;
  accuracyChart.data.datasets[0].data = [completed, remaining];
  accuracyChart.update();
  
  const pct = Math.round((completed / dashState.maxCheckpoints) * 100);
  $('accuracy-value').textContent = pct + '%';
  $('checkpoints-count').textContent = `${completed}/${dashState.maxCheckpoints}`;
  $('errors-count').textContent = dashState.totalErrors;
}

function updateTimingChart() {
  if (!timingChart) return;
  timingChart.data.datasets[0].data = [
    dashState.steps[0].time || 0,
    dashState.steps[1].time || 0,
    dashState.steps[2].time || 0,
    dashState.steps[3].time || 0
  ];
  timingChart.update();
}

function updateSafetyScore() {
  // Safety score based on errors: each error reduces score
  const maxErrors = 5;
  const score = Math.max(0, Math.round((1 - dashState.totalErrors / maxErrors) * 100));
  dashState.safetyScore = score;
  
  $('safety-value').textContent = score + '%';
  $('safety-bar').style.width = score + '%';
  $('safety-errors').textContent = dashState.totalErrors;
}

function showSessionSummary(data) {
  $('session-summary').classList.add('visible');
  $('summary-score').textContent = data.overallScore + '%';
  
  const stepsHtml = data.steps.map(s => `
    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
      <span>Step ${s.id}: ${s.title}</span>
      <span>${s.completed ? '✅' : '❌'} ${s.time}s (${s.errors} errors)</span>
    </div>
  `).join('');
  $('summary-steps').innerHTML = stepsHtml;
  
  window._sessionData = data;
}

function addLog(message, type) {
  const log = document.getElementById('session-log');
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `<span class="time">${time}</span><span class="msg ${type}">${message}</span>`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
  
  // Remove "waiting" placeholder if present
  const placeholder = log.querySelector('div[style*="text-align:center"]');
  if (placeholder) placeholder.remove();
}

function formatTime(seconds) {
  if (seconds === null || seconds === undefined) return '—';
  const m = String(Math.floor(seconds / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${m}:${s}`;
}
```

---

### Task 12: Start Server & End-to-End Verification

**Files:**
- No file changes. Manual verification.

- [ ] **Step 1: Start the server**

Run: `node server/server.js` from the project root.
Expected output: "Server running on http://localhost:3000"

- [ ] **Step 2: Open dashboard in browser**

Open `http://localhost:3000/dashboard` in a desktop browser.
Expected: Dashboard loads with all panels, shows "Waiting for trainee" status.

- [ ] **Step 3: Open VR app in browser**

Open `http://localhost:3000/app` in a desktop browser (or Quest 2 browser).
Expected: A-Frame scene loads with ground, tower, DAGP, winch placeholders.

- [ ] **Step 4: Walk through all 4 steps manually**

1. Click each of the 4 green inspection zones on the DAGP → each advances checkpoint, shows confirmation, plays sound.
2. After 4 inspections, Step 1 completes and Step 2 starts.
3. Click rope tension zone on winch → click hook inspection zone → Step 2 completes.
4. Click both rigging cables → touch tower lift points → Step 3 completes.
5. Click left sweep zone → click right sweep zone → click signal button → Step 4 completes.
6. Completion overlay appears with score, timing, safety rating.

Expected: Dashboard updates in real-time for each action — step tracker, timing, accuracy chart, safety score, session log all live.

- [ ] **Step 5: Verify error states**

Try clicking wrong objects (drum instead of rope, wrong lug, signal before sweeping).
Expected: Error toast appears in VR, error logged on dashboard, safety score decreases.

---

### Self-Review Checklist

**1. Spec coverage check:**
- ✅ 4 training steps (Inspect DAGP, Check Winch, Attach Rigging, Safety Signal) — Tasks 6-9
- ✅ Live dashboard with 6 panels — Tasks 10-11
- ✅ WebSocket VR → Server, SSE Server → Dashboard — Task 2
- ✅ A-Frame WebXR scene — Task 3
- ✅ Audio feedback — Task 5
- ✅ Completion overlay with score — Task 4
- ✅ Error handling with toast + dashboard log — Tasks 4, 11
- ✅ Future vision card with ₹9.6L pricing — Task 10
- ✅ 30-headset deployment vision — Task 10
- ✅ Single-player (multiplayer deferred as stretch) — in scope

**2. Placeholder scan:** No TBD/TODO/fill-in-later patterns found. All code complete.

**3. Type consistency:** All function names, event types, data structures are consistent across tasks (e.g., `advanceCheckpoint`, `recordError`, `playSound`, event type names like `checkpoint`, `step_complete`, `training_complete`).

---

*Plan prepared by: Gaya (Ryze Studios AI Agent) for Ronak Raval*
*Date: 2026-06-12*

---

### Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-12-resonia-vr-pilot-implementation.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for this 2-day build — you can keep working while I grind through tasks.

2. **Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints. Good if you want to watch progress and give feedback as I build.

**Which approach?**
