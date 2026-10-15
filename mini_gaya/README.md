# Mini J — the desktop companion

A full-body JARVIS that lives on the desktop and replaces Coucou as the Claude Code companion.

| | |
|---|---|
| **Approvals** | Allow / Always / Deny / Terminal cards from the PermissionRequest hook; Claude's questions as buttons. Nothing is allowed without a click. |
| **Talk to J** | right-click → *Talk to J…*: a message into the open chat (Claude Code's own session pipe, `cc_peer.py`), a closed one, or a new session. *Type as me* types it as you. |
| **The Deck** | click J: Home (live core, agent grid, Jump in), Today (done + tickable to-do), Sessions (hover to expand, jump / folder / copy), Agents (latest reports) |
| **Morning brief** | on boot / new day: what got done, what's waiting |
| **Life** | walks and floats around, breathes, blinks, watches the cursor, hops on done, shakes when it needs you, dozes, gets dizzy if poked; hides during games |

```
start_jarvis_pet.bat          start J (also in Windows Startup)
swap_coucou_for_jarvis.py     wire / unwire the hooks in ~/.claude/settings.json (--undo)
tests/test_sprite_bridge.py   12 approval-safety fixtures - run with no sprite on port 8767
prep_body.py / prep_layers.py cut the art into light layers (rembg)
```

Files: `jarvis_sprite.py` (sprite, bubbles, cards) · `sprite_deck.py` · `sprite_chat.py` · `sprite_body.py` ·
`sprite_brief.py` · `sprite_ui.py` · `jarvis_sprite_hook.py` (the hook) · `cc_peer.py` (session pipe) ·
`jarvis_state.py` (state from the harness log; also the Claude Code status line).

Art: Katviz's Command Core emblem + Android Sentinel sheet (`art/`). Sounds: Kenney, CC0. Fonts: Space Grotesk / Space Mono, OFL.
Logs: `~/.jarvis/logs/sprite.log`.
