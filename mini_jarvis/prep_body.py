"""Cut full-body Anime JARVIS out of the ComfyUI turnaround sheet and split into
cyan light layers, so the body glows in JARVIS's state colors (Arc Cyan, Amber, Emerald).

Output:
  art/body/<view>_{base,glow,bloom,full}.png
  views: front, three_quarter, side, back
Resolution: H=1024 (Crisp high-res master, ultra-sharp at 2.0x scale)
"""
import os
import sys
import numpy as np
from PIL import Image, ImageChops, ImageFilter
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "art", "concepts", "jarvis_turnaround_comfyui.png")
OUT = os.path.join(HERE, "art", "body")
VIEWS = [
    ("front", 22, 367),
    ("three_quarter", 367, 628),
    ("side", 628, 842),
    ("back", 842, 1180),
]
H = 1024  # High-definition master height for 2.0x retina desktop scale


def split_cyan_light(im):
    r, g, b, a = im.split()
    hsv = im.convert("RGB").convert("HSV")
    h, s, v = hsv.split()

    h_arr = np.array(h)
    s_arr = np.array(s)
    v_arr = np.array(v, dtype=float)
    a_arr = np.array(a)

    # Cyan / Electric Blue in PIL HSV: ~100 to 160, saturated (s>30), bright (v>80)
    is_cyan = (h_arr >= 100) & (h_arr <= 160) & (s_arr >= 30) & (v_arr >= 80)
    # High specular metallic / visor highlights
    is_spec = (v_arr >= 238)
    glow_mask = (is_cyan | is_spec) & (a_arr > 40)

    # Gradient glow intensity
    glow_intensity = np.where(glow_mask, np.clip((v_arr - 80.0) * (255.0 / 175.0), 0, 255), 0).astype(np.uint8)
    glow_a = Image.fromarray(glow_intensity, mode="L")

    # Darken underneath the glow on base so neon light layers pop vibrantly
    dim = Image.eval(glow_a, lambda x: 255 - int(x * 0.45))
    base = Image.merge("RGBA", (*[ImageChops.multiply(c, dim) for c in (r, g, b)], a))

    white = Image.new("L", im.size, 255)
    glow = Image.merge("RGBA", (white, white, white, glow_a))
    bloom = Image.merge("RGBA", (white, white, white, glow_a.filter(ImageFilter.GaussianBlur(18))))
    return base, glow, bloom


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SHEET
    if not os.path.exists(src):
        print(f"Error: source sheet {src} not found!")
        sys.exit(1)
    
    sheet = Image.open(src).convert("RGB")
    print(f"Processing master sheet {src} ({sheet.width}x{sheet.height})...")
    os.makedirs(OUT, exist_ok=True)

    for name, x0, x1 in VIEWS:
        # Crop y between 20 and 876 to exclude any top/bottom border
        sub = sheet.crop((x0, 20, x1, 876))
        part = remove(sub)
        box = part.getchannel("A").point(lambda v: 255 if v > 35 else 0).getbbox()
        if not box:
            print(f"Warning: no figure detected for {name}, using uncropped")
            box = (0, 0, part.width, part.height)
        fig = part.crop(box)
        target_w = max(1, round(fig.width * H / fig.height))
        fig = fig.resize((target_w, H), Image.LANCZOS)

        base, glow, bloom = split_cyan_light(fig)
        for kind, img in (("base", base), ("glow", glow), ("bloom", bloom), ("full", fig)):
            save_path = os.path.join(OUT, f"{name}_{kind}.png")
            img.save(save_path)
        print(f"Exported {name} -> {fig.width}x{fig.height} px (base, glow, bloom, full)")

    print("All body layers extracted successfully!")


if __name__ == "__main__":
    main()
