"""Generate authentic Mini Gaya Bodhi Commander sprite art.

Creates high-definition, beautifully proportioned chibi commander assets:
- front, three_quarter, side (base, glow, bloom, full)
- Bodhi Lotus Core layers for notch/tray
- Sacred Gold (#D4AF37 / #FFD73C) & Celestial Obsidian (#0B090A) aesthetic
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
BODY_DIR = os.path.join(HERE, "art", "body")
LAYERS_DIR = os.path.join(HERE, "layers")
H = 512  # canonical height

# Gaya Color Palette
GOLD_LIGHT = (255, 235, 140, 255)
GOLD_MAIN = (235, 185, 55, 255)
GOLD_DARK = (180, 135, 30, 255)
GOLD_SHADOW = (120, 85, 15, 255)

OBSIDIAN_LIGHT = (45, 40, 48, 255)
OBSIDIAN_MAIN = (24, 20, 26, 255)
OBSIDIAN_DARK = (12, 10, 14, 255)

SKIN_MAIN = (255, 230, 215, 255)
SKIN_SHADOW = (235, 195, 180, 255)
BLUSH = (255, 160, 160, 160)

WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def create_body_sprite(view="front"):
    # Canvas setup
    if view == "front":
        W = 200
    elif view == "three_quarter":
        W = 190
    else:  # side
        W = 140

    im = Image.new("RGBA", (W, H), TRANSPARENT)
    draw = ImageDraw.Draw(im)

    glow_im = Image.new("RGBA", (W, H), TRANSPARENT)
    glow_draw = ImageDraw.Draw(glow_im)

    cx = W // 2
    # Vertical anchor points
    # H = 512
    # Head: y 40 to 190 (radius ~65)
    # Torso: y 190 to 287 (HIP = 0.56 -> 512 * 0.56 = 286.7)
    # Legs: y 287 to 485
    # Feet / base: y 485 to 500

    hip_y = int(H * 0.56)

    # 1. Flowing Commander Cape (Back layer)
    if view == "front":
        cape_pts = [(cx - 45, 200), (cx + 45, 200), (cx + 70, 440), (cx + 50, 470),
                    (cx, 460), (cx - 50, 470), (cx - 70, 440)]
        draw.polygon(cape_pts, fill=OBSIDIAN_DARK)
        # Gold hem on cape
        draw.line([(cx - 70, 440), (cx - 50, 470), (cx, 460), (cx + 50, 470), (cx + 70, 440)],
                  fill=GOLD_MAIN, width=4)
    elif view == "three_quarter":
        cape_pts = [(cx - 40, 200), (cx + 35, 200), (cx + 75, 450), (cx + 40, 475),
                    (cx - 10, 465), (cx - 55, 450)]
        draw.polygon(cape_pts, fill=OBSIDIAN_DARK)
        draw.line([(cx - 55, 450), (cx - 10, 465), (cx + 40, 475), (cx + 75, 450)],
                  fill=GOLD_MAIN, width=4)
    else:  # side
        cape_pts = [(cx - 20, 200), (cx + 25, 200), (cx + 55, 460), (cx + 20, 470), (cx - 20, 440)]
        draw.polygon(cape_pts, fill=OBSIDIAN_DARK)
        draw.line([(cx - 20, 440), (cx + 20, 470), (cx + 55, 460)], fill=GOLD_MAIN, width=4)

    # 2. Flowing Golden Hair (Back layer)
    hair_back_color = GOLD_DARK
    if view == "front":
        # Left and right long twin locks
        draw.polygon([(cx - 40, 90), (cx - 75, 170), (cx - 70, 280), (cx - 45, 340), (cx - 35, 270), (cx - 48, 170)],
                     fill=hair_back_color)
        draw.polygon([(cx + 40, 90), (cx + 75, 170), (cx + 70, 280), (cx + 45, 340), (cx + 35, 270), (cx + 48, 170)],
                     fill=hair_back_color)
    elif view == "three_quarter":
        draw.polygon([(cx - 45, 90), (cx - 70, 170), (cx - 65, 280), (cx - 45, 330), (cx - 35, 260)],
                     fill=hair_back_color)
        draw.polygon([(cx + 35, 90), (cx + 80, 180), (cx + 75, 310), (cx + 50, 360), (cx + 35, 270)],
                     fill=hair_back_color)
    else:  # side
        draw.polygon([(cx - 25, 90), (cx - 55, 180), (cx - 50, 320), (cx - 30, 360), (cx - 15, 270)],
                     fill=hair_back_color)

    # 3. Lower Body (Legs and Boots) - Must be split cleanly at hip_y for stride!
    if view == "front":
        # Left leg
        draw.rectangle([cx - 32, hip_y, cx - 10, hip_y + 110], fill=OBSIDIAN_MAIN)
        # Right leg
        draw.rectangle([cx + 10, hip_y, cx + 32, hip_y + 110], fill=OBSIDIAN_MAIN)
        # Gold side stripes on pants
        draw.line([(cx - 30, hip_y), (cx - 30, hip_y + 110)], fill=GOLD_MAIN, width=3)
        draw.line([(cx + 30, hip_y), (cx + 30, hip_y + 110)], fill=GOLD_MAIN, width=3)
        # Left boot (Gold greave + obsidian sole)
        draw.polygon([(cx - 34, hip_y + 100), (cx - 8, hip_y + 100), (cx - 6, hip_y + 190), (cx - 36, hip_y + 190)],
                     fill=GOLD_MAIN)
        draw.rectangle([cx - 38, hip_y + 185, cx - 4, hip_y + 196], fill=OBSIDIAN_DARK)
        # Right boot
        draw.polygon([(cx + 8, hip_y + 100), (cx + 34, hip_y + 100), (cx + 36, hip_y + 190), (cx + 6, hip_y + 190)],
                     fill=GOLD_MAIN)
        draw.rectangle([cx + 4, hip_y + 185, cx + 38, hip_y + 196], fill=OBSIDIAN_DARK)
        # Knee gems
        draw.ellipse([cx - 24, hip_y + 105, cx - 18, hip_y + 115], fill=WHITE)
        draw.ellipse([cx + 18, hip_y + 105, cx + 24, hip_y + 115], fill=WHITE)
    elif view == "three_quarter":
        # Back leg
        draw.rectangle([cx + 8, hip_y, cx + 28, hip_y + 105], fill=OBSIDIAN_DARK)
        draw.polygon([(cx + 6, hip_y + 95), (cx + 30, hip_y + 95), (cx + 32, hip_y + 185), (cx + 4, hip_y + 185)],
                     fill=GOLD_DARK)
        draw.rectangle([cx + 2, hip_y + 180, cx + 34, hip_y + 192], fill=OBSIDIAN_DARK)
        # Front leg
        draw.rectangle([cx - 28, hip_y, cx - 6, hip_y + 110], fill=OBSIDIAN_MAIN)
        draw.line([(cx - 26, hip_y), (cx - 26, hip_y + 110)], fill=GOLD_MAIN, width=3)
        draw.polygon([(cx - 32, hip_y + 100), (cx - 4, hip_y + 100), (cx - 2, hip_y + 190), (cx - 34, hip_y + 190)],
                     fill=GOLD_MAIN)
        draw.rectangle([cx - 36, hip_y + 185, cx, hip_y + 196], fill=OBSIDIAN_DARK)
    else:  # side
        # Single profile leg
        draw.rectangle([cx - 15, hip_y, cx + 15, hip_y + 110], fill=OBSIDIAN_MAIN)
        draw.line([(cx + 10, hip_y), (cx + 10, hip_y + 110)], fill=GOLD_MAIN, width=3)
        draw.polygon([(cx - 18, hip_y + 100), (cx + 18, hip_y + 100), (cx + 26, hip_y + 190), (cx - 16, hip_y + 190)],
                     fill=GOLD_MAIN)
        draw.rectangle([cx - 20, hip_y + 185, cx + 28, hip_y + 196], fill=OBSIDIAN_DARK)

    # 4. Upper Torso & Armor (hip_y upwards to neck y=190)
    torso_w = 40 if view != "side" else 28
    # Obsidian tunic
    draw.polygon([(cx - torso_w, 190), (cx + torso_w, 190),
                  (cx + torso_w - 6, hip_y + 4), (cx - torso_w + 6, hip_y + 4)], fill=OBSIDIAN_MAIN)
    # Sacred Gold Bodhi Sash & Trim
    draw.line([(cx, 190), (cx, hip_y)], fill=GOLD_MAIN, width=4)
    draw.rectangle([cx - torso_w + 4, hip_y - 12, cx + torso_w - 4, hip_y + 2], fill=GOLD_MAIN)
    draw.rectangle([cx - torso_w + 8, hip_y - 8, cx + torso_w - 8, hip_y - 2], fill=OBSIDIAN_DARK)

    # Arms and Shoulders
    if view == "front":
        # Pauldrons (Gold shoulder guards)
        draw.ellipse([cx - torso_w - 18, 190, cx - torso_w + 10, 226], fill=GOLD_MAIN)
        draw.ellipse([cx + torso_w - 10, 190, cx + torso_w + 18, 226], fill=GOLD_MAIN)
        # Arms
        draw.rectangle([cx - torso_w - 14, 222, cx - torso_w, 275], fill=OBSIDIAN_MAIN)
        draw.rectangle([cx + torso_w, 222, cx + torso_w + 14, 275], fill=OBSIDIAN_MAIN)
        # Gold gauntlets
        draw.rectangle([cx - torso_w - 15, 260, cx - torso_w + 1, 285], fill=GOLD_MAIN)
        draw.rectangle([cx + torso_w - 1, 260, cx + torso_w + 15, 285], fill=GOLD_MAIN)
    elif view == "three_quarter":
        draw.ellipse([cx - torso_w - 16, 190, cx - torso_w + 12, 226], fill=GOLD_MAIN)
        draw.ellipse([cx + torso_w - 12, 192, cx + torso_w + 12, 224], fill=GOLD_DARK)
        draw.rectangle([cx - torso_w - 12, 222, cx - torso_w + 2, 275], fill=OBSIDIAN_MAIN)
        draw.rectangle([cx - torso_w - 14, 260, cx - torso_w + 4, 285], fill=GOLD_MAIN)
    else:  # side
        draw.ellipse([cx - 8, 190, cx + 22, 226], fill=GOLD_MAIN)
        draw.rectangle([cx - 4, 222, cx + 12, 275], fill=OBSIDIAN_MAIN)
        draw.rectangle([cx - 6, 260, cx + 14, 285], fill=GOLD_MAIN)

    # 5. Heart Center: THE BODHI LOTUS CORE (Chest Emblem)
    core_y = 222
    core_rad = 14
    if view != "side":
        core_x = cx if view == "front" else cx - 4
        # Gold decorative rim
        draw.ellipse([core_x - core_rad - 4, core_y - core_rad - 4,
                      core_x + core_rad + 4, core_y + core_rad + 4], fill=GOLD_DARK)
        draw.ellipse([core_x - core_rad, core_y - core_rad,
                      core_x + core_rad, core_y + core_rad], fill=OBSIDIAN_DARK)
        # 8-petaled lotus points
        for i in range(8):
            ang = i * (math.pi / 4)
            px = core_x + math.cos(ang) * (core_rad - 2)
            py = core_y + math.sin(ang) * (core_rad - 2)
            draw.line([(core_x, core_y), (px, py)], fill=GOLD_LIGHT, width=2)
        # Inner radiant jewel
        draw.ellipse([core_x - 5, core_y - 5, core_x + 5, core_y + 5], fill=WHITE)

        # GLOW MASK FOR CORE
        glow_draw.ellipse([core_x - core_rad + 2, core_y - core_rad + 2,
                           core_x + core_rad - 2, core_y + core_rad - 2], fill=WHITE)
        glow_draw.ellipse([core_x - 6, core_y - 6, core_x + 6, core_y + 6], fill=WHITE)
    else:
        core_x = cx + 8
        draw.ellipse([core_x - 8, core_y - 12, core_x + 8, core_y + 12], fill=GOLD_DARK)
        glow_draw.ellipse([core_x - 6, core_y - 9, core_x + 6, core_y + 9], fill=WHITE)

    # 6. Head & Face (y: 60 to 190)
    head_y = 120
    head_rad = 54
    face_cx = cx if view == "front" else (cx - 6 if view == "three_quarter" else cx + 4)

    # Face base (porcelain chibi skin)
    draw.ellipse([face_cx - head_rad, head_y - head_rad,
                  face_cx + head_rad, head_y + head_rad], fill=SKIN_MAIN)

    # Rosy cheeks
    if view == "front":
        draw.ellipse([face_cx - 36, head_y + 12, face_cx - 18, head_y + 24], fill=BLUSH)
        draw.ellipse([face_cx + 18, head_y + 12, face_cx + 36, head_y + 24], fill=BLUSH)
    elif view == "three_quarter":
        draw.ellipse([face_cx - 38, head_y + 12, face_cx - 20, head_y + 24], fill=BLUSH)
        draw.ellipse([face_cx + 10, head_y + 12, face_cx + 28, head_y + 24], fill=BLUSH)
    else:
        draw.ellipse([face_cx + 12, head_y + 12, face_cx + 32, head_y + 24], fill=BLUSH)

    # Visor / Luminous Golden Eyes
    eye_y = head_y + 4
    if view == "front":
        # Left eye
        draw.ellipse([face_cx - 32, eye_y - 10, face_cx - 14, eye_y + 10], fill=OBSIDIAN_DARK)
        draw.ellipse([face_cx - 29, eye_y - 7, face_cx - 17, eye_y + 7], fill=GOLD_MAIN)
        draw.ellipse([face_cx - 26, eye_y - 4, face_cx - 20, eye_y + 2], fill=WHITE)
        # Right eye
        draw.ellipse([face_cx + 14, eye_y - 10, face_cx + 32, eye_y + 10], fill=OBSIDIAN_DARK)
        draw.ellipse([face_cx + 17, eye_y - 7, face_cx + 29, eye_y + 7], fill=GOLD_MAIN)
        draw.ellipse([face_cx + 20, eye_y - 4, face_cx + 26, eye_y + 2], fill=WHITE)
        # GLOW MASK FOR EYES
        glow_draw.ellipse([face_cx - 29, eye_y - 7, face_cx - 17, eye_y + 7], fill=WHITE)
        glow_draw.ellipse([face_cx + 17, eye_y - 7, face_cx + 29, eye_y + 7], fill=WHITE)
        # Gentle smile
        draw.arc([face_cx - 8, eye_y + 16, face_cx + 8, eye_y + 24], start=0, end=180, fill=OBSIDIAN_MAIN, width=2)
    elif view == "three_quarter":
        draw.ellipse([face_cx - 34, eye_y - 10, face_cx - 16, eye_y + 10], fill=OBSIDIAN_DARK)
        draw.ellipse([face_cx - 31, eye_y - 7, face_cx - 19, eye_y + 7], fill=GOLD_MAIN)
        draw.ellipse([face_cx - 28, eye_y - 4, face_cx - 22, eye_y + 2], fill=WHITE)
        draw.ellipse([face_cx + 6, eye_y - 10, face_cx + 22, eye_y + 10], fill=OBSIDIAN_DARK)
        draw.ellipse([face_cx + 9, eye_y - 7, face_cx + 19, eye_y + 7], fill=GOLD_MAIN)
        draw.ellipse([face_cx + 11, eye_y - 4, face_cx + 17, eye_y + 2], fill=WHITE)
        glow_draw.ellipse([face_cx - 31, eye_y - 7, face_cx - 19, eye_y + 7], fill=WHITE)
        glow_draw.ellipse([face_cx + 9, eye_y - 7, face_cx + 19, eye_y + 7], fill=WHITE)
        draw.arc([face_cx - 10, eye_y + 16, face_cx + 4, eye_y + 24], start=0, end=180, fill=OBSIDIAN_MAIN, width=2)
    else:  # side
        draw.polygon([(face_cx + 8, eye_y - 8), (face_cx + 26, eye_y), (face_cx + 8, eye_y + 8)], fill=GOLD_MAIN)
        draw.ellipse([face_cx + 12, eye_y - 3, face_cx + 20, eye_y + 3], fill=WHITE)
        glow_draw.polygon([(face_cx + 8, eye_y - 8), (face_cx + 26, eye_y), (face_cx + 8, eye_y + 8)], fill=WHITE)

    # 7. Foreground Hair Bangs & Commander Bodhi Tiara
    # Front bangs in Sacred Gold
    if view == "front":
        draw.polygon([(face_cx - 48, head_y - 30), (face_cx - 30, head_y + 4), (face_cx - 18, head_y - 20),
                      (face_cx, head_y + 2), (face_cx + 18, head_y - 20), (face_cx + 30, head_y + 4),
                      (face_cx + 48, head_y - 30), (face_cx, head_y - 56)], fill=GOLD_MAIN)
        # Highlight locks
        draw.line([(face_cx - 24, head_y - 25), (face_cx - 28, head_y)], fill=GOLD_LIGHT, width=3)
        draw.line([(face_cx + 24, head_y - 25), (face_cx + 28, head_y)], fill=GOLD_LIGHT, width=3)
        draw.line([(face_cx, head_y - 35), (face_cx, head_y - 2)], fill=GOLD_LIGHT, width=3)

        # Bodhi Commander Tiara / Crown
        tiara_y = head_y - 42
        draw.polygon([(face_cx - 40, tiara_y + 6), (face_cx, tiara_y - 16), (face_cx + 40, tiara_y + 6),
                      (face_cx + 26, tiara_y + 12), (face_cx, tiara_y - 2), (face_cx - 26, tiara_y + 12)],
                     fill=GOLD_DARK)
        draw.polygon([(face_cx - 36, tiara_y + 4), (face_cx, tiara_y - 12), (face_cx + 36, tiara_y + 4),
                      (face_cx + 22, tiara_y + 10), (face_cx, tiara_y), (face_cx - 22, tiara_y + 10)],
                     fill=GOLD_MAIN)
        # Central Lotus Tiara Gem
        draw.polygon([(face_cx, tiara_y - 18), (face_cx + 7, tiara_y - 7),
                      (face_cx, tiara_y + 2), (face_cx - 7, tiara_y - 7)], fill=WHITE)
        glow_draw.polygon([(face_cx, tiara_y - 18), (face_cx + 7, tiara_y - 7),
                           (face_cx, tiara_y + 2), (face_cx - 7, tiara_y - 7)], fill=WHITE)
    elif view == "three_quarter":
        draw.polygon([(face_cx - 48, head_y - 30), (face_cx - 32, head_y + 6), (face_cx - 16, head_y - 18),
                      (face_cx + 4, head_y + 4), (face_cx + 22, head_y - 18), (face_cx + 44, head_y - 28),
                      (face_cx, head_y - 56)], fill=GOLD_MAIN)
        tiara_y = head_y - 42
        draw.polygon([(face_cx - 36, tiara_y + 8), (face_cx - 4, tiara_y - 16), (face_cx + 36, tiara_y + 4),
                      (face_cx + 22, tiara_y + 10), (face_cx - 4, tiara_y - 2), (face_cx - 24, tiara_y + 12)],
                     fill=GOLD_MAIN)
        draw.polygon([(face_cx - 4, tiara_y - 18), (face_cx + 3, tiara_y - 7),
                      (face_cx - 4, tiara_y + 2), (face_cx - 11, tiara_y - 7)], fill=WHITE)
        glow_draw.polygon([(face_cx - 4, tiara_y - 18), (face_cx + 3, tiara_y - 7),
                           (face_cx - 4, tiara_y + 2), (face_cx - 11, tiara_y - 7)], fill=WHITE)
    else:  # side
        draw.polygon([(face_cx - 40, head_y - 30), (face_cx - 10, head_y + 8), (face_cx + 12, head_y - 10),
                      (face_cx + 24, head_y + 2), (face_cx + 28, head_y - 36), (face_cx - 10, head_y - 56)], fill=GOLD_MAIN)
        tiara_y = head_y - 42
        draw.polygon([(face_cx - 20, tiara_y + 10), (face_cx + 16, tiara_y - 14), (face_cx + 28, tiara_y + 2)],
                     fill=GOLD_MAIN)
        draw.polygon([(face_cx + 16, tiara_y - 16), (face_cx + 22, tiara_y - 8),
                      (face_cx + 16, tiara_y), (face_cx + 10, tiara_y - 8)], fill=WHITE)
        glow_draw.polygon([(face_cx + 16, tiara_y - 16), (face_cx + 22, tiara_y - 8),
                           (face_cx + 16, tiara_y), (face_cx + 10, tiara_y - 8)], fill=WHITE)

    # 8. Produce Bloom Layer (Gaussian blur on glow channel)
    glow_a = glow_im.getchannel("A")
    bloom_a = glow_a.filter(ImageFilter.GaussianBlur(12))
    bloom_im = Image.merge("RGBA", (Image.new("L", im.size, 255),
                                    Image.new("L", im.size, 255),
                                    Image.new("L", im.size, 255),
                                    bloom_a))

    return im, glow_im, bloom_im


def create_bodhi_core_layers(size=256):
    """Create the standalone Bodhi Lotus Core emblem for Tray and Island."""
    im = Image.new("RGBA", (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(im)

    glow_im = Image.new("RGBA", (size, size), TRANSPARENT)
    glow_draw = ImageDraw.Draw(glow_im)

    c = size // 2
    R = size // 2 - 12

    # Outer Obsidian Ring
    draw.ellipse([c - R, c - R, c + R, c + R], fill=OBSIDIAN_DARK, outline=GOLD_MAIN, width=6)
    # Inner Gold filigree ring
    r_in = int(R * 0.78)
    draw.ellipse([c - r_in, c - r_in, c + r_in, c + r_in], outline=GOLD_DARK, width=3)

    # 8 Dharmic Lotus Petals
    petals = 8
    for i in range(petals):
        ang = i * (2 * math.pi / petals)
        x1 = c + math.cos(ang) * (R - 8)
        y1 = c + math.sin(ang) * (R - 8)
        x2 = c + math.cos(ang + math.pi / petals) * int(R * 0.45)
        y2 = c + math.sin(ang + math.pi / petals) * int(R * 0.45)
        draw.polygon([(c, c), (x1, y1), (x2, y2)], fill=OBSIDIAN_MAIN, outline=GOLD_MAIN)

    # Central Core Jewel
    r_core = int(R * 0.38)
    draw.ellipse([c - r_core, c - r_core, c + r_core, c + r_core], fill=GOLD_MAIN)
    draw.ellipse([c - r_core + 4, c - r_core + 4, c + r_core - 4, c + r_core - 4], fill=OBSIDIAN_DARK)

    # 4-point radiant star
    s_r = int(r_core * 0.65)
    star_pts = [(c, c - s_r), (c + 6, c - 6), (c + s_r, c), (c + 6, c + 6),
                (c, c + s_r), (c - 6, c + 6), (c - s_r, c), (c - 6, c - 6)]
    draw.polygon(star_pts, fill=WHITE)

    # Glow channel
    glow_draw.ellipse([c - r_core + 2, c - r_core + 2, c + r_core - 2, c + r_core - 2], fill=WHITE)
    glow_draw.polygon(star_pts, fill=WHITE)

    glow_a = glow_im.getchannel("A")
    bloom_a = glow_a.filter(ImageFilter.GaussianBlur(14))
    bloom_im = Image.merge("RGBA", (Image.new("L", im.size, 255),
                                    Image.new("L", im.size, 255),
                                    Image.new("L", im.size, 255),
                                    bloom_a))

    return im, glow_im, bloom_im


def main():
    os.makedirs(BODY_DIR, exist_ok=True)
    os.makedirs(LAYERS_DIR, exist_ok=True)

    print("Generating Mini Gaya Bodhi Commander body sprites...")
    for v in ["front", "three_quarter", "side"]:
        base, glow, bloom = create_body_sprite(v)
        full = Image.alpha_composite(base, glow)

        base.save(os.path.join(BODY_DIR, f"{v}_base.png"))
        glow.save(os.path.join(BODY_DIR, f"{v}_glow.png"))
        bloom.save(os.path.join(BODY_DIR, f"{v}_bloom.png"))
        full.save(os.path.join(BODY_DIR, f"{v}_full.png"))
        print(f"  {v}: {base.size[0]}x{base.size[1]} saved to {BODY_DIR}")

    print("Generating Bodhi Lotus Core layers for notch / tray...")
    core_base, core_glow, core_bloom = create_bodhi_core_layers(256)
    core_base.save(os.path.join(LAYERS_DIR, "base.png"))
    core_glow.save(os.path.join(LAYERS_DIR, "glow.png"))
    core_bloom.save(os.path.join(LAYERS_DIR, "bloom.png"))
    print(f"  Core layers saved to {LAYERS_DIR}")

if __name__ == "__main__":
    main()
