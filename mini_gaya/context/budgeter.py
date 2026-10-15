import json
import os
import time
from typing import List, Optional

WARN_THRESHOLD = 0.75

def calculate_pressure(step_count: int, transcript_bytes: int, max_steps: int = 40, max_bytes: int = 150000) -> float:
    step_ratio = step_count / max(1, max_steps)
    byte_ratio = transcript_bytes / max(1, max_bytes)
    return round(min(1.0, max(step_ratio, byte_ratio)), 3)

def should_warn_pressure(pressure: float) -> bool:
    return pressure >= WARN_THRESHOLD

def create_session_checkpoint(conversation_id: str, summary: str, open_tasks: Optional[List[str]] = None, output_dir: Optional[str] = None) -> str:
    if not output_dir:
        output_dir = os.path.expanduser(f"~/.gemini/antigravity/brain/{conversation_id}/checkpoints")
    os.makedirs(output_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    chk_file = os.path.join(output_dir, f"checkpoint_{stamp}.json")
    data = {
        "conversation_id": conversation_id,
        "timestamp": time.time(),
        "summary": summary,
        "open_tasks": open_tasks or []
    }
    with open(chk_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return chk_file
