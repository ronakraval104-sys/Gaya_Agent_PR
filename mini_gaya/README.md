# Mini Gaya — Divine Desktop Companion

A full-body animated sprite that lives on your desktop, monitors live Antigravity sessions, holds interactive approvals, and guides the Council of Gaya.

| Feature | Description |
|---|---|
| **Approvals** | Allow / Always / Deny / Terminal cards from permission hooks; tool parameters and questions as buttons. Nothing runs without explicit authorization. |
| **Talk to Gaya** | Right-click → *Talk to Gaya…*: direct communication into active sessions, or voice query answered from local knowledge. |
| **The Deck** | Click the sprite: Home (live Command Core & status), Today (completed + checklist), Sessions (hover to expand, jump/focus), Council (latest verdicts & metrics). |
| **Morning Brief** | On boot / new day: what got done yesterday and what's waiting for you today. |
| **Physics & Life** | Walks, glides, bounces, watches cursor, hops on done, shakes on hold, dozes, and hides during fullscreen media/games. |

```bat
start_gaya_pet.bat            :: Launch Mini Gaya companion
launch_mini_gaya.py           :: Interactive desktop launcher on WinSta0\Default
swap_coucou_for_gaya.py       :: Wire/unwire permission hooks
```

Files: `mini_gaya.py` · `gaya_sprite.py` · `gaya_island.py` · `gaya_state.py` · `gaya_sprite_hook.py` · `sprite_deck.py` · `sprite_chat.py` · `sprite_body.py`.

Logs & Preferences: `~/.gaya/logs/sprite.log` and `~/.gaya/sprite.json`.
