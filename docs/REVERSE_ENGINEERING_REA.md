# 🦾 Reverse Engineer Anything (REA) — Tvashtar's Mandate

In the Council of Gaya architecture, reverse-engineering closed targets is strictly isolated from standard application builders (Bob) and designers (Freya). **🦾 Tvashtar** is the sole designated agent responsible for:
- Binary disassembly & decompilation
- Electron & JavaScript bundle unpacking (ASAR)
- Android APK decompilation
- Protocol & IPC boundary reconstruction

---

## 🛠️ The REA Arsenal
- **Skill**: [`skills/reverse-engineer-anything/`](../skills/reverse-engineer-anything/) (v42)
- **MCP Server**: `rea-agents@latest`
- **Supported Providers**:
  - Ghidra 12.1+ / Hopper Disassembler / IDA Pro
  - JADX Headless (Android APKs & DEX)
  - ASAR unpackers & source map extractors
  - Network & process tracing (PTY & packet observation)

---

## 🔄 Separation of Concerns & Handoff Loop
1. **Target Identification**: User or Gaya identifies a closed binary, packaged web app, or undocumented network API.
2. **Tvashtar REA Strike**: Tvashtar disassembles the target, extracts strings, symbols, IPC interfaces, and schemas, and emits a structured `[🦾 Tvashtar]` protocol block.
3. **Bob Build**: Bob takes the recovered specs and implements clean, maintainable code.
4. **Freya Design**: Freya crafts UI matching or elevating the reverse-engineered visual experience.
5. **LOGOS Gate**: LOGOS audits the implementation against safety and accuracy.
