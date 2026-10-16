"""
Council of Gaya Agent Portrait Generator
Generates pristine 256x256 transparent circular avatar portraits for the 4 Council Specialists:
- LOGOS (North / Top): Center profile, analytical gaze, Cyan (#38BDF8)
- BOB (East / Right): Side profile facing LEFT towards Gaya, Amber (#F59E0B)
- FREYA (South / Bottom): Center profile, creative seer, Emerald (#10B981)
- TVASHTAR (West / Left): Side profile facing RIGHT towards Gaya, Magenta (#EC4899)
"""

import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "agents")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHEET_MECHA = "D:/Ai_Tools/ComfyUI_windows_portable/ComfyUI/output/jarvis_anime_sheet_00001_.png"
SHEET_SENTINEL = "d:/Ai_Tools/antigravity_ai/mini_gaya/art/concepts/Futuristic Android Sentinel Character Sheet-2.png"
GRID_HELMETS = "d:/Ai_Tools/antigravity_ai/mini_gaya/art/concepts/Futuristic AI Helmet Collection Grid.png"

def remove_white_bg(img, threshold=240):
    img = img.convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    # Distance from pure white
    diff = 255.0 - np.maximum(np.maximum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    # Alpha based on darkness: pure white gets alpha 0, dark lines get alpha 255
    alpha = np.clip(diff * (255.0 / (255.0 - threshold)), 0, 255)
    # For pixels where RGB are all > threshold
    mask = (arr[:, :, 0] > threshold) & (arr[:, :, 1] > threshold) & (arr[:, :, 2] > threshold)
    arr[:, :, 3] = np.where(mask, alpha, 255)
    return Image.fromarray(arr.astype(np.uint8))

def colorize_visor(crop_img, target_rgb, intensity=0.7):
    """
    Shifts cyan/white/bright visor highlights towards the agent's target RGB color.
    """
    img = crop_img.convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    
    # Visor pixels are bright (luminance > 120) and have cyan or blue dominance
    lum = (r * 0.299 + g * 0.587 + b * 0.114)
    visor_mask = (lum > 110) & (b > r * 0.8) & (a > 50)
    
    tr, tg, tb = target_rgb
    
    # Blend target color into the bright areas
    factor = np.clip((lum - 110) / 145.0, 0, 1) * intensity
    
    for ch, tch in enumerate([tr, tg, tb]):
        arr[:, :, ch] = np.where(
            visor_mask,
            arr[:, :, ch] * (1 - factor) + tch * factor,
            arr[:, :, ch]
        )
        
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def composite_avatar_token(head_img, theme_rgb, angle_facing="center", size=256):
    """
    Composites head into a 256x256 circular HUD token with subtle ambient rings and outer rim glow.
    """
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    cx, cy = size // 2, size // 2
    r_outer = size // 2 - 6
    r_inner = r_outer - 8
    
    # 1. Subtle background radar disk
    tr, tg, tb = theme_rgb
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), fill=(tr // 8, tg // 8, tb // 8, 120))
    draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), fill=(10, 10, 15, 180))
    
    # 2. Concentric tactical grid lines
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), outline=(tr, tg, tb, 140), width=2)
    draw.ellipse((cx - (r_inner - 14), cy - (r_inner - 14), cx + (r_inner - 14), cy + (r_inner - 14)), outline=(tr, tg, tb, 60), width=1)
    
    # 3. Fit head inside circular mask
    head_w, head_h = head_img.size
    target_h = int(size * 0.82)
    scale = target_h / head_h
    target_w = int(head_w * scale)
    head_resized = head_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Position head horizontally based on gaze
    if angle_facing == "left":
        head_x = cx - target_w // 2 - 8
    elif angle_facing == "right":
        head_x = cx - target_w // 2 + 8
    else:
        head_x = cx - target_w // 2
        
    head_y = cy - target_h // 2 + 4
    
    # Create circular mask for head
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((cx - r_inner + 2, cy - r_inner + 2, cx + r_inner - 2, cy + r_inner - 2), fill=255)
    
    head_canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    head_canvas.paste(head_resized, (head_x, head_y), head_resized)
    
    # Composite masked head
    canvas.paste(head_canvas, (0, 0), mask)
    
    # 4. Outer luminous glow border & tactical cardinal pips
    draw.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), outline=(tr, tg, tb, 220), width=2)
    
    # Cardinal tick marks
    tick_len = 6
    draw.line([(cx, cy - r_inner), (cx, cy - r_inner + tick_len)], fill=(tr, tg, tb, 240), width=2)
    draw.line([(cx, cy + r_inner - tick_len), (cx, cy + r_inner)], fill=(tr, tg, tb, 240), width=2)
    draw.line([(cx - r_inner, cy), (cx - r_inner + tick_len, cy)], fill=(tr, tg, tb, 240), width=2)
    draw.line([(cx + r_inner - tick_len, cy), (cx + r_inner, cy)], fill=(tr, tg, tb, 240), width=2)
    
    return canvas

def generate_agents():
    sheet_mecha_img = Image.open(SHEET_MECHA)
    
    # 1. LOGOS (North / Top): Center profile, analytical gaze, Cyan (#38BDF8 -> RGB 56, 189, 248)
    crop_logos = sheet_mecha_img.crop((95, 25, 265, 215))
    logos_nobg = remove_white_bg(crop_logos)
    logos_colored = colorize_visor(logos_nobg, (56, 189, 248), intensity=0.85)
    logos_token = composite_avatar_token(logos_colored, (56, 189, 248), angle_facing="center")
    logos_path = os.path.join(OUTPUT_DIR, "logos.png")
    logos_token.save(logos_path, "PNG")
    print(f"Generated LOGOS: {logos_path}")

    # 2. TVASHTAR (West / Left): Side profile facing RIGHT towards Gaya, Magenta (#EC4899 -> RGB 236, 72, 153)
    crop_tvashtar = sheet_mecha_img.crop((675, 40, 840, 220))
    tvashtar_nobg = remove_white_bg(crop_tvashtar)
    tvashtar_colored = colorize_visor(tvashtar_nobg, (236, 72, 153), intensity=0.92)
    tvashtar_token = composite_avatar_token(tvashtar_colored, (236, 72, 153), angle_facing="right")
    tvashtar_path = os.path.join(OUTPUT_DIR, "tvashtar.png")
    tvashtar_token.save(tvashtar_path, "PNG")
    print(f"Generated TVASHTAR: {tvashtar_path}")

    # 3. BOB (East / Right): Side profile facing LEFT towards Gaya, Amber (#F59E0B -> RGB 245, 158, 11)
    crop_bob = sheet_mecha_img.crop((675, 40, 840, 220))
    bob_nobg = remove_white_bg(crop_bob)
    bob_mirrored = ImageOps.mirror(bob_nobg) # Flip horizontally so it faces LEFT towards center!
    bob_colored = colorize_visor(bob_mirrored, (245, 158, 11), intensity=0.95)
    bob_token = composite_avatar_token(bob_colored, (245, 158, 11), angle_facing="left")
    bob_path = os.path.join(OUTPUT_DIR, "bob.png")
    bob_token.save(bob_path, "PNG")
    print(f"Generated BOB: {bob_path}")

    # 4. FREYA (South / Bottom): Center profile, creative gaze, Emerald (#10B981 -> RGB 16, 185, 129)
    crop_freya = sheet_mecha_img.crop((95, 25, 265, 215))
    freya_nobg = remove_white_bg(crop_freya)
    freya_colored = colorize_visor(freya_nobg, (16, 185, 129), intensity=0.90)
    freya_token = composite_avatar_token(freya_colored, (16, 185, 129), angle_facing="center")
    freya_path = os.path.join(OUTPUT_DIR, "freya.png")
    freya_token.save(freya_path, "PNG")
    print(f"Generated FREYA: {freya_path}")

if __name__ == "__main__":
    generate_agents()
