"""
ComfyUI Local Divine Gods Generator
Generates true mythological character portraits for the 4 Council Specialists:
- Freya: Norse Goddess of the Hunt & Beauty (Emerald #10B981)
- Bob: Divine Master Builder / Architect God (Amber #F59E0B)
- Logos: Sage Professor / Philosopher of Cosmic Reason (Cyan #38BDF8)
- Tvashtar: Vedic Divine Blacksmith / Celestial Artificer (Magenta #EC4899)

Strictly adheres to:
1. Local ComfyUI execution only.
2. Immediate termination of ComfyUI service after generation to free GPU VRAM.
3. Transparent circular avatar token formatting (256x256) into council_of_gaya/public/agents/.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
import numpy as np
from PIL import Image, ImageOps, ImageDraw

COMFY_DIR = "D:/Ai_Tools/ComfyUI_windows_portable"
COMFY_PORT = 8188
COMFY_URL = f"http://127.0.0.1:{COMFY_PORT}"
OUTPUT_DIR = os.path.join(COMFY_DIR, "ComfyUI", "output")
AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "agents")
os.makedirs(AGENTS_DIR, exist_ok=True)

CKPT_NAME = "animaPencilXL_v500.safetensors"

TARGETS = [
    {
        "id": "logos",
        "name": "LOGOS",
        "color": (56, 189, 248),
        "seed": 331144,
        "prefix": "god_logos",
        "positive": "masterpiece, best quality, ultra-detailed anime portrait, 1man, venerable divine professor and sage philosopher, Logos god of cosmic mind and reason, wise silver hair, trimmed neat beard, piercing intelligent eyes, thoughtful analytical gaze looking forward and down, wearing celestial scholar robes embroidered with geometric diagrams, glowing celestial scrolls and holographic mathematical matrices, cyan and sapphire glowing starlight aura, clean simple dark background, character avatar portrait, upper body, sharp crisp lines",
        "negative": "robot, mecha, android, visor, metal helmet, cyber armor, deformed, bad anatomy, bad hands, blurry, low quality, worst quality, text, watermark"
    },
    {
        "id": "bob",
        "name": "Bob",
        "color": (245, 158, 11),
        "seed": 884422,
        "prefix": "god_bob",
        "positive": "masterpiece, best quality, ultra-detailed anime portrait, 1man, divine master builder, Bob the Builder as a noble artisan architect god, rugged handsome features, short beard, confident warm smile, side profile facing left, looking to the left, wearing reinforced leather artisan tunic, golden runic hammer held over shoulder, glowing golden forge embers and architectural blueprints in background, warm amber and gold divine aura, clean simple dark background, character avatar portrait, upper body",
        "negative": "robot, mecha, android, visor, metal helmet, cybernetic, deformed, bad anatomy, bad hands, blurry, low quality, worst quality, text, watermark"
    },
    {
        "id": "freya",
        "name": "Freya",
        "color": (16, 185, 129),
        "seed": 552277,
        "prefix": "god_freya",
        "positive": "masterpiece, best quality, ultra-detailed anime portrait, 1girl, gorgeous Norse goddess Freya, goddess of the hunt and beauty, ethereal celestial maiden, long golden blonde braided hair, falcon feather circlet crown, noble serene gaze looking forward and up, emerald green rune-inscribed mantle, holding a sacred golden recurve bow, glowing emerald forest mist and green auroral light, clean simple dark background, character avatar portrait, upper body, beautiful face",
        "negative": "robot, mecha, android, visor, metal helmet, cyber armor, deformed, bad anatomy, bad hands, blurry, low quality, worst quality, text, watermark"
    },
    {
        "id": "tvashtar",
        "name": "Tvashtar",
        "color": (236, 72, 153),
        "seed": 771199,
        "prefix": "god_tvashtar",
        "positive": "masterpiece, best quality, ultra-detailed anime portrait, 1man, Tvashtar the ancient Vedic divine blacksmith and celestial artisan god, powerful sculpted muscular bronze god, radiant glowing eyes, side profile facing right, looking to the right, dark hair tied back, glowing Sanskrit tattoos on arm, holding a glowing cosmic forge hammer sparking with molten magenta and ruby lightning, celestial anvil sparks, creator of divine weapons, intense creative focus, clean simple dark background, character avatar portrait, upper body",
        "negative": "robot, mecha, android, visor, metal helmet, cybernetic mask, deformed, bad anatomy, bad hands, blurry, low quality, worst quality, text, watermark"
    }
]

def kill_comfy_processes():
    print("Ensuring any previous ComfyUI instances are terminated...")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-NetTCPConnection -LocalPort {COMFY_PORT} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

def wait_for_comfy(timeout=90):
    print(f"Waiting for ComfyUI to respond on http://127.0.0.1:{COMFY_PORT}...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(f"{COMFY_URL}/system_stats")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    print("ComfyUI server online & ready!")
                    return True
        except Exception:
            time.sleep(1.5)
    return False

def make_prompt_payload(positive_text, negative_text, filename_prefix, seed=12345):
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": CKPT_NAME
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive_text,
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_text,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 896,
                "height": 896,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": 26,
                "cfg": 7.0,
                "sampler_name": "euler_ancestral",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": filename_prefix,
                "images": ["6", 0]
            }
        }
    }

def queue_prompt(prompt_dict):
    data = json.dumps({"prompt": prompt_dict}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["prompt_id"]

def wait_for_prompt(prompt_id, timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(f"{COMFY_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if prompt_id in data:
                    item = data[prompt_id]
                    outputs = item.get("outputs", {})
                    if "7" in outputs and "images" in outputs["7"]:
                        imgs = outputs["7"]["images"]
                        if imgs:
                            return imgs[0]["filename"]
        except Exception:
            pass
        time.sleep(2)
    return None

def crop_circular_god_avatar(img_path, theme_rgb, size=256):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # Crop square around head & shoulders
    # Center crop with slight bias towards upper half (where face is)
    crop_size = min(w, h)
    left = (w - crop_size) // 2
    top = max(0, int(h * 0.04))
    if top + crop_size > h:
        top = h - crop_size
    cropped = img.crop((left, top, left + crop_size, top + crop_size))
    resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
    
    # Build HUD Token Canvas
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    cx, cy = size // 2, size // 2
    r_outer = size // 2 - 6
    r_inner = r_outer - 8
    
    tr, tg, tb = theme_rgb
    
    # Circular mask for image
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), fill=255)
    
    # Paste image into circle
    canvas.paste(resized, (0, 0), mask)
    
    # Outer illuminated celestial ring
    draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), outline=(tr, tg, tb, 230), width=2)
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), outline=(tr, tg, tb, 100), width=1)
    
    # Cardinal tick marks
    tick_len = 6
    draw.line([(cx, cy - r_inner), (cx, cy - r_inner + tick_len)], fill=(tr, tg, tb, 255), width=2)
    draw.line([(cx, cy + r_inner - tick_len), (cx, cy + r_inner)], fill=(tr, tg, tb, 255), width=2)
    draw.line([(cx - r_inner, cy), (cx - r_inner + tick_len, cy)], fill=(tr, tg, tb, 255), width=2)
    draw.line([(cx + r_inner - tick_len, cy), (cx + r_inner, cy)], fill=(tr, tg, tb, 255), width=2)
    
    return canvas

def run_pipeline():
    kill_comfy_processes()
    time.sleep(1)
    
    print("Launching ComfyUI in the background...")
    # Start ComfyUI process
    bat_path = os.path.join(COMFY_DIR, "run_nvidia_gpu.bat")
    proc = subprocess.Popen(
        ["cmd.exe", "/c", bat_path],
        cwd=COMFY_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"ComfyUI process spawned with PID {proc.pid}")
    
    try:
        if not wait_for_comfy(timeout=100):
            print("ERROR: ComfyUI failed to start in time.")
            return False
            
        for t in TARGETS:
            print(f"\n--- Generating God Portrait: {t['name']} ({t['id']}) ---")
            payload = make_prompt_payload(t["positive"], t["negative"], t["prefix"], seed=t["seed"])
            prompt_id = queue_prompt(payload)
            print(f"Queued prompt_id: {prompt_id}. Awaiting generation...")
            
            fname = wait_for_prompt(prompt_id, timeout=120)
            if not fname:
                print(f"FAILED to generate {t['name']}")
                continue
                
            src_path = os.path.join(OUTPUT_DIR, fname)
            print(f"Generated raw image: {src_path}")
            
            # Crop and format into final circular avatar token
            dest_path = os.path.join(AGENTS_DIR, f"{t['id']}.png")
            token_img = crop_circular_god_avatar(src_path, t["color"])
            token_img.save(dest_path, "PNG")
            print(f"Saved divine avatar token: {dest_path}")
            
        print("\nAll 4 divine god portraits generated and deployed successfully!")
        return True
    finally:
        print("\nTerminating ComfyUI service to completely free up GPU VRAM...")
        try:
            proc.terminate()
        except Exception:
            pass
        kill_comfy_processes()
        print("VRAM Hygiene Complete: ComfyUI terminated, port 8188 closed.")

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
