import json
import os
import sys
import time
import urllib.request
import urllib.parse
import shutil

COMFY_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR = r"D:\Ai_Tools\ComfyUI_windows_portable\ComfyUI\output"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "art", "concepts")
os.makedirs(TARGET_DIR, exist_ok=True)

workflow = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "animaPencilXL_v500.safetensors"
        }
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "masterpiece, best quality, ultra-detailed anime character sheet, full turnaround character sheet, (front view:1.2), (three-quarter view:1.2), (side view:1.1), (back view:1.1), 1boy, handsome young male anime android, sleek carbon obsidian cyber armor, brushed titanium plating, glowing vibrant neon cyan arc reactor on chest, glowing cyan holographic visor, glowing teal circuits, intricate mechanical joints, crisp anime pencil lines, cel shaded, clean white background, full body, standing, high resolution",
            "clip": ["1", 1]
        }
    },
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, messy background, complex background, dark background, realistic photo, 3d render, deformed, sketch",
            "clip": ["1", 1]
        }
    },
    "4": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "width": 1536,
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
            "seed": 987654321,
            "steps": 28,
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
            "filename_prefix": "jarvis_anime_sheet",
            "images": ["6", 0]
        }
    }
}

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_HOST}/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_history(prompt_id):
    with urllib.request.urlopen(f"{COMFY_HOST}/history/{prompt_id}") as resp:
        return json.loads(resp.read().decode('utf-8'))

def main():
    print("Dispatching SDXL generation to ComfyUI (animaPencilXL_v500)...")
    res = queue_prompt(workflow)
    prompt_id = res.get("prompt_id")
    print(f"Prompt queued successfully: ID {prompt_id}")
    
    start_t = time.time()
    while True:
        hist = get_history(prompt_id)
        if prompt_id in hist:
            print(f"Prompt {prompt_id} completed in {round(time.time() - start_t, 1)}s!")
            outputs = hist[prompt_id].get("outputs", {})
            for node_id, out in outputs.items():
                if "images" in out:
                    for img in out["images"]:
                        filename = img["filename"]
                        subfolder = img.get("subfolder", "")
                        src_path = os.path.join(OUTPUT_DIR, subfolder, filename)
                        dst_path = os.path.join(TARGET_DIR, "jarvis_turnaround_comfyui.png")
                        if os.path.exists(src_path):
                            shutil.copy2(src_path, dst_path)
                            print(f"Copied master sheet to: {dst_path}")
                            print(f"File size: {os.path.getsize(dst_path)} bytes")
                            return dst_path
            break
        print(f"Generating... ({round(time.time() - start_t, 1)}s elapsed)")
        time.sleep(2)

if __name__ == "__main__":
    main()
