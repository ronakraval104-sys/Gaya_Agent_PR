"""
JARVIS -- "Command Core" sprite builder (Phase 1: key frames only).

Every frame is built from code: integer-threshold geometry (no anti-aliasing)
plus per-state overrides. The 16x16 mini is a hand-tuned ASCII grid.

Palette is lifted 1:1 from Stark Council "Monolith Signal" tokens
(stark-council/app/globals.css): grayscale hierarchy + traffic-light status.
Color appears on the sprite ONLY when status changes -- same rule as the console.

Run:  python build_sprite.py
Out:  jarvis_sheet_64.png  (7 frames x 64px, in STATES order)
      jarvis_mini_16.png   (idle mini, 16x16)
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# --- palette: Monolith Signal tokens (11 colours + transparent) -------------
PAL = {
    "void": "#0a0a0a",  # --bg
    "s2":   "#141414",  # --surface-2
    "s3":   "#1c1c1c",  # --surface-3
    "line": "#242424",  # --border
    "rim":  "#3a3a3a",  # --border-strong
    "g3":   "#5c5c5c",  # --text-3
    "g2":   "#9c9c9c",  # --text-2
    "g1":   "#d4d4d4",  # --accent-2
    "w":    "#f2f2f2",  # --text / --accent  (the light)
    "warn": "#ffb000",  # --warn  amber = HOLD
    "err":  "#ff2d3f",  # --err   red   = BROKEN
    "ok":   "#2fd36f",  # --ok    green = APPROVED
}

STATES = ["idle", "thinking", "spawning", "hold", "broken", "approved", "asleep"]

N = 64
CX = 32.0          # horizontal centre (pixel-centre space)
CHASSIS_CY = 23.0  # chassis centre
CHASSIS_AP = 19.0  # chassis apothem (half height, flat top/bottom)
CHASSIS_RR = 3.0   # corner rounding
CORE_CY = 31.0     # core centre
CORE_AP = 6.0      # core apothem (pointy-top hex)
SLOT_Y0, SLOT_Y1 = 14, 19   # visor recess rows (inclusive)
BAND_ROWS = (16, 17)        # lit band rows inside the recess
SLOT_INSET = 4.0            # recess keeps this distance from the chassis edge


# --- geometry ----------------------------------------------------------------
def sd_hex(px, py, r):
    """Signed distance to a flat-top hexagon of apothem r (Inigo Quilez)."""
    kx, ky, kz = -0.866025404, 0.5, 0.577350269
    px, py = abs(px), abs(py)
    d = min(kx * px + ky * py, 0.0)
    px -= 2.0 * d * kx
    py -= 2.0 * d * ky
    px -= max(-kz * r, min(px, kz * r))
    py -= r
    return math.hypot(px, py) * (1.0 if py > 0 else -1.0)


def sd_round_hex(px, py, r, rr, pointy=False):
    if pointy:
        px, py = py, px
    return sd_hex(px, py, r - rr) - rr


class Frame:
    def __init__(self):
        self.g = [[None] * N for _ in range(N)]

    def set(self, x, y, c):
        if 0 <= x < N and 0 <= y < N:
            self.g[y][x] = c

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < N and 0 <= y < N else None

    def hline(self, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            self.set(x, y, c)


# --- parts -------------------------------------------------------------------
def chassis_sd(x, y):
    return sd_round_hex(x + 0.5 - CX, y + 0.5 - CHASSIS_CY, CHASSIS_AP, CHASSIS_RR)


def draw_chassis(f, lit=True):
    """Rounded flat-top hex: 1px rim (lit top half), 1px groove, two plates
    split by the visor -- brow plate above, core plate below."""
    for y in range(N):
        for x in range(N):
            d = chassis_sd(x, y)
            if d > 0:
                continue
            py = y + 0.5 - CHASSIS_CY
            if d > -1.0:
                f.set(x, y, ("g3" if lit else "rim") if py < 0 else ("rim" if lit else "line"))
            elif d > -2.0:
                f.set(x, y, "line" if lit else "s3")
            else:
                f.set(x, y, "s3" if y < SLOT_Y0 else "s2")


def slot_extent(y):
    """Leftmost/rightmost recess column on row y (follows the hex flanks)."""
    xs = [x for x in range(N) if chassis_sd(x, y) <= -SLOT_INSET]
    return xs[0], xs[-1]


def draw_visor_slot(f, lip="rim"):
    """Recessed channel whose ends follow the chassis flanks."""
    for y in range(SLOT_Y0, SLOT_Y1 + 1):
        x0, x1 = slot_extent(y)
        f.hline(x0, x1, y, "void")
    x0, x1 = slot_extent(SLOT_Y1 + 1)
    f.hline(x0 + 1, x1 - 1, SLOT_Y1 + 1, lip)   # lower lip catches light


def band(f, col, pad=1, cut_l=0, cut_r=0, ends=("g1", "g2"), rows=BAND_ROWS, dy=0):
    """Lit visor band. Spans the recess minus `pad`, then trimmed by cut_l/cut_r
    (expression = width). `ends` = stepped falloff at each tip, no blending."""
    for y in rows:
        x0, x1 = slot_extent(y)
        x0, x1 = x0 + pad + cut_l, x1 - pad - cut_r
        f.hline(x0, x1, y + dy, col)
        for i, e in enumerate(ends):
            if e:
                f.set(x0 + i, y + dy, e)
                f.set(x1 - i, y + dy, e)


def draw_core(f, rings):
    """Pointy-top hex crystal, faceted not gradiented (crisp at any scale).
    rings = (housing, edge, shade facet, lit facet)."""
    housing, edge, shade, lit = rings
    for y in range(N):
        for x in range(N):
            px, py = x + 0.5 - CX, y + 0.5 - CORE_CY
            d = sd_round_hex(px, py, CORE_AP, 1.5, pointy=True)
            if d > 1.0:
                continue
            if d > 0.0:
                f.set(x, y, "void")            # cut-in seat
            elif d > -1.0:
                f.set(x, y, housing)
            elif d > -2.0:
                f.set(x, y, edge)
            else:
                # light enters top-left: lower-right facet sits in shade
                f.set(x, y, shade if (px + py) > 1.0 else lit)


CHEV_APEX = (45, 50, 55)  # apex row of each chevron, top -> bottom
CHEV_HALF = 12            # half width
CHEV_THICK = 2


def chevron_pixels(apex_y):
    pts = []
    for y in range(apex_y, apex_y + 8):
        for x in range(N):
            ax = abs(x + 0.5 - CX)
            if ax > CHEV_HALF:
                continue
            t = y - (apex_y + math.floor(ax / 3.0))
            if 0 <= t < CHEV_THICK:
                pts.append((x, y, t))
    return pts


def draw_chevrons(f, cols, edge=None):
    """cols = colour per chevron (top->bottom). edge = colour for top edge row."""
    for apex, col in zip(CHEV_APEX, cols):
        for x, y, t in chevron_pixels(apex):
            f.set(x, y, edge if (edge and t == 0) else col)


def satellite(f, cx, cy):
    """Sub-agent orb: a 5x5 rounded square echoing the chassis language."""
    for y in range(cy - 2, cy + 3):
        for x in range(cx - 2, cx + 3):
            corner = abs(x - cx) == 2 and abs(y - cy) == 2
            if corner:
                continue
            edge = abs(x - cx) == 2 or abs(y - cy) == 2
            f.set(x, y, "g3" if edge else "g1")
    f.set(cx, cy, "w")


# --- states ------------------------------------------------------------------
def base(lit=True):
    f = Frame()
    draw_chassis(f, lit)
    draw_visor_slot(f, lip="rim" if lit else "line")
    return f


LIT_CORE = ("rim", "g2", "g1", "w")      # housing, edge, shade, lit
RANK = ("g1", "g2", "g3")


def st_idle():
    f = base()
    band(f, "w")
    draw_core(f, LIT_CORE)
    draw_chevrons(f, RANK)
    return f


def st_thinking():
    f = base()
    # dim rail across the recess: where the scan travels
    x0, x1 = slot_extent(17)
    for x in range(x0 + 1, x1, 2):
        f.set(x, 17, "line")
    # scan head biased right: taller + brighter, stepped tail trailing left
    for xa, xb, c in [(27, 30, "g3"), (31, 34, "g2"), (35, 37, "g1")]:
        f.hline(xa, xb, 16, c)
        f.hline(xa, xb, 17, c)
    for y in (15, 16, 17, 18):
        f.hline(38, 40, y, "w")
    draw_core(f, ("rim", "g3", "g3", "g2"))     # core throttles down while it thinks
    draw_chevrons(f, RANK)
    return f


ORBS = [(5, 9), (58, 9), (5, 37), (58, 37)]


def st_spawning():
    f = base()
    band(f, "w")
    draw_core(f, ("g2", "w", "g1", "w"))        # core at full output
    draw_chevrons(f, RANK)
    # dotted tethers from the chassis flank vertex to each satellite
    for ox, oy in ORBS:
        sx, sy = (10, 23) if ox < 32 else (53, 23)
        n = max(abs(ox - sx), abs(oy - sy))
        for i in range(2, n - 2, 2):
            x = round(sx + (ox - sx) * i / n)
            y = round(sy + (oy - sy) * i / n)
            if f.get(x, y) is None:
                f.set(x, y, "rim")
        satellite(f, ox, oy)
    return f


def st_hold():
    f = base()
    band(f, "warn", cut_l=5, cut_r=5, ends=(None, None))  # narrowed, level
    draw_core(f, ("rim", "warn", "g3", "g3"))   # amber containment ring
    draw_chevrons(f, RANK)
    return f


def st_broken():
    f = base()
    # fragmented red band, one shard dropped a row: signal integrity lost
    x0, _ = slot_extent(16)
    for a, b, dy in [(1, 5, 0), (8, 10, 0), (13, 19, 1), (22, 23, 0), (26, 27, 0)]:
        for y in BAND_ROWS:
            f.hline(x0 + a, x0 + b, y + dy, "err")
    draw_core(f, ("line", "err", "line", "rim"))  # red ring, core gone dark
    draw_chevrons(f, ("rim", "line", "line"))
    # hairline fracture through the brow plate
    for x, y in [(41, 5), (41, 6), (40, 7), (40, 8), (39, 9), (40, 10), (40, 11), (39, 12)]:
        f.set(x, y, "void")
    return f


def st_approved():
    f = base()
    band(f, "ok", ends=("g1", None))
    # dry wit: the right end of the gaze lifts one pixel -- a knowing glance
    _, x1 = slot_extent(16)
    for x in range(x1 - 6, x1):
        f.set(x, 15, f.get(x, 16))
        f.set(x, 16, f.get(x, 17))
        f.set(x, 17, "void")
    draw_core(f, LIT_CORE)
    draw_chevrons(f, ("ok", "ok", "ok"))        # full-rank pulse
    return f


def st_asleep():
    f = base(lit=False)
    band(f, "s3", cut_l=4, cut_r=4, ends=(None, None), rows=(17,))  # band off
    draw_core(f, ("line", "line", "s3", "line"))
    draw_chevrons(f, ("line", "s3", "s3"))
    return f


BUILDERS = {
    "idle": st_idle, "thinking": st_thinking, "spawning": st_spawning,
    "hold": st_hold, "broken": st_broken, "approved": st_approved,
    "asleep": st_asleep,
}


# --- 16x16 mini (hand-tuned, idle) -------------------------------------------
MINI_KEY = {
    ".": None, "o": "g3", "r": "rim", "l": "line", "b": "s3", "s": "s2",
    "v": "void", "W": "w", "w": "g1", "g": "g2",
}
# Hand-tuned, not downsampled: at 16px a scaled hex core collapses into a "+"
# and stacked chevrons checkerboard. So: 8-row hex head (rim / brow / visor /
# 2x2 faceted core) + three 2-row chevrons separated by clean gap rows, same
# g1 > g2 > g3 rank ramp as the 64px idle.
MINI = [
    "....oooooooo....",
    "...obbbbbbbbo...",
    "..ovwWWWWWWwvo..",
    ".obbbbbbbbbbbbo.",
    ".rsssssWwsssssr.",
    "..rsssswgssssr..",
    "...rssssssssr...",
    "....rrrrrrrr....",
    ".....wwwwww.....",
    "...ww......ww...",
    "................",
    ".....gggggg.....",
    "...gg......gg...",
    "................",
    ".....oooooo.....",
    "...oo......oo...",
]


def to_image(grid, w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            if c:
                hx = PAL[c].lstrip("#")
                px[x, y] = (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
    return img


def main():
    sheet = Image.new("RGBA", (N * len(STATES), N), (0, 0, 0, 0))
    used = set()
    for i, name in enumerate(STATES):
        f = BUILDERS[name]()
        for row in f.g:
            used.update(c for c in row if c)
        sheet.paste(to_image(f.g, N, N), (i * N, 0))
    sheet.save(os.path.join(HERE, "jarvis_sheet_64.png"))

    assert len(MINI) == 16 and all(len(r) == 16 for r in MINI), "mini must be 16x16"
    mgrid = [[MINI_KEY[ch] for ch in row] for row in MINI]
    to_image(mgrid, 16, 16).save(os.path.join(HERE, "jarvis_mini_16.png"))

    print(f"sheet: {len(STATES)} frames -> jarvis_sheet_64.png")
    print(f"colours used: {len(used)} -> {sorted(used)}")


if __name__ == "__main__":
    main()
