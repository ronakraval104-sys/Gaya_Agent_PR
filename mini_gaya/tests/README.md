Approval-bridge safety tests (EDIDTH rounds 1-4, 2026-10-12).
Run with NO sprite running (they use port 8767):
  python test_sprite_bridge.py   -> must print 12/12
  python probe_arm.py / probe_r3.py / probe_r4.py -> every non-plain case must show Allow locked
Re-run after ANY change to jarvis_sprite.py or gaya_sprite_hook.py.
