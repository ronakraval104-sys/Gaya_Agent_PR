"""Cut the full-body JARVIS out of Boss's character sheet and split it into
light layers, so the body glows in JARVIS's state colour like the head does.

    python prep_body.py [sheet.png]

Output: art/body/<view>_{base,glow,bloom}.png  (views: front, three_quarter, side, back)
Background removal: rembg (U2Net, local, runs offline after first model download).
"""
import os
import sys

from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "art", "concepts", "Mini_Gaya_Turnaround_Sheet_Pristine.png")
OUT = os.path.join(HERE, "art", "body")
VIEWS = ["front", "three_quarter", "side", "back"]
H = 512


def split_light(im):
    r, g, b, a = im.split()
    hsv = im.convert("RGB").convert("HSV")
    h, s, v = hsv.split()

    import numpy as np
    h_arr = np.array(h)
    s_arr = np.array(s)
    v_arr = np.array(v, dtype=float)
    a_arr = np.array(a)

    # Gold/amber hue (yellow-amber in PIL 0-255: 15 to 75) + bright (V > 120, S > 40)
    is_gold = (h_arr >= 15) & (h_arr <= 75) & (s_arr >= 40) & (v_arr >= 120)
    # High specular highlights
    is_spec = (v_arr >= 240)
    glow_mask = (is_gold | is_spec) & (a_arr > 50)

    glow_intensity = np.where(glow_mask, np.clip((v_arr - 100.0) * (255.0 / 155.0), 0, 255), 0).astype(np.uint8)
    glow_a = Image.fromarray(glow_intensity, mode="L")

    dim = Image.eval(glow_a, lambda x: 255 - int(x * 0.4))
    base = Image.merge("RGBA", (*[ImageChops.multiply(c, dim) for c in (r, g, b)], a))
    white = Image.new("L", im.size, 255)
    glow = Image.merge("RGBA", (white, white, white, glow_a))
    bloom = Image.merge("RGBA", (white, white, white, glow_a.filter(ImageFilter.GaussianBlur(12))))
    return base, glow, bloom


def main():
    from rembg import remove
    src = sys.argv[1] if len(sys.argv) > 1 else SHEET
    sheet = Image.open(src).convert("RGBA")
    W = sheet.width
    # Four turnaround figures: front (0..0.277), 3/4 (0.277..0.531), side (0.531..0.739), back (0.739..1.0)
    cols = [(0.0, 0.277), (0.277, 0.531), (0.531, 0.739), (0.739, 1.0)]
    os.makedirs(OUT, exist_ok=True)
    for name, (a0, a1) in zip(VIEWS, cols):
        part = remove(sheet.crop((int(a0 * W), 0, int(a1 * W), sheet.height)))
        box = part.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        fig = part.crop(box)
        fig = fig.resize((max(1, round(fig.width * H / fig.height)), H), Image.LANCZOS)
        base, glow, bloom = split_light(fig)
        for kind, img in (("base", base), ("glow", glow), ("bloom", bloom), ("full", fig)):
            img.save(os.path.join(OUT, "%s_%s.png" % (name, kind)))
        print("%-14s %dx%d" % (name, fig.width, fig.height))


if __name__ == "__main__":
    main()

