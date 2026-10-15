"""Split the Command Core emblem into layers the pet can recolour live.

base.png   - the body with its lights dimmed out
glow.png   - the light (white, alpha = intensity)  -> tinted per state
bloom.png  - blurred halo of the light
mask_visor / mask_core / mask_chev - regions for state effects
"""
import os
from PIL import Image, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "art", "head", "Futuristic Robotic Core Emblem.png")
OUT = os.path.join(HERE, "layers")
SIZE = 512

# regions in the 512 px OUTPUT (x0, y0, x1, y1) - read off layers/_check.png
VISOR = (95, 140, 418, 205)
CORE = (190, 220, 320, 355)
CHEV = (220, 365, 295, 450)


def main():
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    bbox = im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
    # square crop around content
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    half = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) / 2 + 20
    box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
    scale = SIZE / (box[2] - box[0])

    def region(r):
        m = Image.new("L", (SIZE, SIZE), 0)
        m.paste(255, r)
        return m.filter(ImageFilter.GaussianBlur(6))

    im = im.crop(box).resize((SIZE, SIZE), Image.LANCZOS)
    r, g, b, a = im.split()
    hsv = im.convert("RGB").convert("HSV")
    _, s, v = hsv.split()
    # light = bright and low-saturation
    g_int = Image.eval(v, lambda x: 0 if x < 110 else min(255, int((x - 110) * 255 / 145)))
    low_sat = Image.eval(s, lambda x: 255 if x < 60 else max(0, 255 - (x - 60) * 4))
    glow_a = ImageChops.multiply(ImageChops.multiply(g_int, low_sat), a)

    # base: original with the light pulled down so tints don't fight it
    dim = Image.eval(glow_a, lambda x: 255 - int(x * 0.82))
    base_rgb = [ImageChops.multiply(ch, dim) for ch in (r, g, b)]
    Image.merge("RGBA", (*base_rgb, a)).save(os.path.join(OUT, "base.png"))

    white = Image.new("L", (SIZE, SIZE), 255)
    Image.merge("RGBA", (white, white, white, glow_a)).save(os.path.join(OUT, "glow.png"))
    bloom = glow_a.filter(ImageFilter.GaussianBlur(14))
    Image.merge("RGBA", (white, white, white, bloom)).save(os.path.join(OUT, "bloom.png"))

    for name, rr in (("visor", VISOR), ("core", CORE), ("chev", CHEV)):
        region(rr).save(os.path.join(OUT, "mask_%s.png" % name))
    print("layers ->", OUT, "scale %.3f" % scale)


if __name__ == "__main__":
    main()
