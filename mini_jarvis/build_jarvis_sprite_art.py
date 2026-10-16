"""Generate authentic Anime JARVIS Arc Sentinel sprite art at 1024px Ultra-HD.

Renders crisp 1024px master assets (2x scale native) so the avatar looks
impeccably sharp and detailed on high-DPI displays even at 2.0x desktop scale:
- front, three_quarter, side, back (base, glow, bloom, full)
- Arc Reactor Cyber Core layers for notch/tray (160x160 master -> 80x80)
- Electric Cyan (#00F0FF), Obsidian Carbon (#141820) & Titanium (#3A4454) aesthetic
- Full composite turnaround showcase board (2400x1200 Ultra-HD)
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
BODY_DIR = os.path.join(HERE, "art", "body")
LAYERS_DIR = os.path.join(HERE, "layers")
CONCEPTS_DIR = os.path.join(HERE, "art", "concepts")

# Master resolution: 1024px (2x Large Master)
SCALE = 2.0
H = int(512 * SCALE)  # 1024 px

# JARVIS Color Palette
CYAN_GLOW = (0, 240, 255, 255)
CYAN_MAIN = (0, 190, 235, 255)
CYAN_DARK = (0, 130, 180, 255)
CYAN_WHITE = (220, 250, 255, 255)

TITANIUM_LIGHT = (75, 88, 108, 255)
TITANIUM_MAIN = (48, 58, 74, 255)
TITANIUM_DARK = (32, 40, 52, 255)

CARBON_MAIN = (20, 24, 32, 255)
CARBON_DARK = (12, 14, 18, 255)
CARBON_ACCENT = (28, 34, 46, 255)

GOLD_ACCENT = (235, 185, 55, 255)
GOLD_DARK = (160, 120, 30, 255)

PLATINUM_HAIR = (225, 235, 248, 255)
PLATINUM_HAIR_SHADOW = (165, 180, 205, 255)
PLATINUM_HAIR_HIGHLIGHT = (250, 252, 255, 255)

SKIN_MAIN = (255, 232, 220, 255)
SKIN_SHADOW = (235, 198, 185, 255)
BLUSH = (255, 150, 160, 140)

WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def S(val):
    """Scale a single scalar value."""
    return int(val * SCALE)


def P(x, y):
    """Scale a coordinate pair."""
    return (int(x * SCALE), int(y * SCALE))


def PTS(points):
    """Scale an array of coordinate tuples."""
    return [(int(x * SCALE), int(y * SCALE)) for x, y in points]


def BOX(x0, y0, x1, y1):
    """Scale a bounding box rectangle."""
    return [int(x0 * SCALE), int(y0 * SCALE), int(x1 * SCALE), int(y1 * SCALE)]


def create_body_sprite(view="front"):
    # Base dimensions scaled by 2.0
    if view == "front":
        W = S(210)
    elif view == "three_quarter":
        W = S(195)
    elif view == "side":
        W = S(150)
    else:  # back
        W = S(200)

    im = Image.new("RGBA", (W, H), TRANSPARENT)
    draw = ImageDraw.Draw(im)

    glow_im = Image.new("RGBA", (W, H), TRANSPARENT)
    glow_draw = ImageDraw.Draw(glow_im)

    cx = W // 2
    base_cx = 210 // 2 if view == "front" else (195 // 2 if view == "three_quarter" else (150 // 2 if view == "side" else 100))
    hip_y = S(286)

    # Helper coordinate mapper relative to base_cx
    def M(x_rel, y_abs):
        return (cx + S(x_rel), S(y_abs))

    def MPTS(points):
        return [(cx + S(xr), S(ya)) for xr, ya in points]

    # -------------------------------------------------------------
    # 1. Back Layer: Tactical Cyber Cape & Thrusters
    # -------------------------------------------------------------
    if view == "front":
        cape_pts = MPTS([(-48, 205), (48, 205), (75, 435), (52, 475),
                         (0, 455), (-52, 475), (-75, 435)])
        draw.polygon(cape_pts, fill=CARBON_DARK)
        # Cyan neon hem border
        draw.line(MPTS([(-75, 435), (-52, 475), (0, 455), (52, 475), (75, 435)]),
                  fill=CYAN_MAIN, width=S(3))
        glow_draw.line(MPTS([(-75, 435), (-52, 475), (0, 455), (52, 475), (75, 435)]),
                       fill=WHITE, width=S(3))

    elif view == "three_quarter":
        cape_pts = MPTS([(-42, 205), (38, 205), (80, 445), (45, 480),
                         (-10, 465), (-58, 445)])
        draw.polygon(cape_pts, fill=CARBON_DARK)
        draw.line(MPTS([(-58, 445), (-10, 465), (45, 480), (80, 445)]),
                  fill=CYAN_MAIN, width=S(3))
        glow_draw.line(MPTS([(-58, 445), (-10, 465), (45, 480), (80, 445)]),
                       fill=WHITE, width=S(3))

    elif view == "side":
        cape_pts = MPTS([(-22, 205), (28, 205), (60, 455), (22, 472), (-18, 440)])
        draw.polygon(cape_pts, fill=CARBON_DARK)
        draw.line(MPTS([(-18, 440), (22, 472), (60, 455)]), fill=CYAN_MAIN, width=S(3))
        glow_draw.line(MPTS([(-18, 440), (22, 472), (60, 455)]), fill=WHITE, width=S(3))

    else:  # back view
        cape_pts = MPTS([(-52, 200), (52, 200), (82, 440), (55, 480),
                         (0, 460), (-55, 480), (-82, 440)])
        draw.polygon(cape_pts, fill=CARBON_DARK)
        draw.rectangle([cx - S(8), S(200), cx + S(8), S(380)], fill=TITANIUM_DARK)
        draw.line([(cx, S(210)), (cx, S(370))], fill=CYAN_MAIN, width=S(4))
        glow_draw.line([(cx, S(210)), (cx, S(370))], fill=WHITE, width=S(4))
        draw.line(MPTS([(-82, 440), (-55, 480), (0, 460), (55, 480), (82, 440)]),
                  fill=CYAN_MAIN, width=S(3))
        glow_draw.line(MPTS([(-82, 440), (-55, 480), (0, 460), (55, 480), (82, 440)]),
                       fill=WHITE, width=S(3))

    # -------------------------------------------------------------
    # 2. Back Layer: Platinum Spiky Cyber Hair (Behind neck)
    # -------------------------------------------------------------
    hair_back_col = PLATINUM_HAIR_SHADOW
    if view == "front":
        draw.polygon(MPTS([(-45, 95), (-78, 155), (-65, 220), (-42, 185)]), fill=hair_back_col)
        draw.polygon(MPTS([(45, 95), (78, 155), (65, 220), (42, 185)]), fill=hair_back_col)
    elif view == "three_quarter":
        draw.polygon(MPTS([(-48, 95), (-75, 160), (-60, 220), (-38, 180)]), fill=hair_back_col)
        draw.polygon(MPTS([(40, 95), (82, 165), (70, 230), (44, 190)]), fill=hair_back_col)
    elif view == "side":
        draw.polygon(MPTS([(-30, 95), (-65, 160), (-52, 220), (-20, 185)]), fill=hair_back_col)
    else:  # back
        draw.ellipse([cx - S(62), S(50), cx + S(62), S(175)], fill=PLATINUM_HAIR)
        draw.polygon(MPTS([(-55, 120), (-75, 175), (-40, 165)]), fill=hair_back_col)
        draw.polygon(MPTS([(55, 120), (75, 175), (40, 165)]), fill=hair_back_col)
        draw.polygon(MPTS([(-20, 150), (0, 195), (20, 150)]), fill=hair_back_col)

    # -------------------------------------------------------------
    # 3. Lower Body (Legs, Greaves, Thruster Boots) - Below hip_y
    # -------------------------------------------------------------
    if view in ("front", "back"):
        # Left Leg
        draw.rectangle([cx - S(34), hip_y, cx - S(12), hip_y + S(115)], fill=CARBON_MAIN)
        draw.polygon(MPTS([(-36, 286 + 90), (-10, 286 + 90), (-10, 286 + 175), (-38, 286 + 175)]),
                     fill=TITANIUM_MAIN)
        # Right Leg
        draw.rectangle([cx + S(12), hip_y, cx + S(34), hip_y + S(115)], fill=CARBON_MAIN)
        draw.polygon(MPTS([(10, 286 + 90), (36, 286 + 90), (38, 286 + 175), (10, 286 + 175)]),
                     fill=TITANIUM_MAIN)
        # Knee Armor Guards
        draw.rectangle([cx - S(32), hip_y + S(75), cx - S(14), hip_y + S(95)], fill=TITANIUM_LIGHT)
        draw.rectangle([cx + S(14), hip_y + S(75), cx + S(32), hip_y + S(95)], fill=TITANIUM_LIGHT)
        # Cyber Knee Glow lines
        draw.line([(cx - S(28), hip_y + S(85)), (cx - S(18), hip_y + S(85))], fill=CYAN_MAIN, width=S(2))
        draw.line([(cx + S(18), hip_y + S(85)), (cx + S(28), hip_y + S(85))], fill=CYAN_MAIN, width=S(2))
        glow_draw.line([(cx - S(28), hip_y + S(85)), (cx - S(18), hip_y + S(85))], fill=WHITE, width=S(2))
        glow_draw.line([(cx + S(18), hip_y + S(85)), (cx + S(28), hip_y + S(85))], fill=WHITE, width=S(2))
        # Boots
        draw.rectangle([cx - S(36), hip_y + S(175), cx - S(8), hip_y + S(205)], fill=CARBON_DARK)
        draw.rectangle([cx + S(8), hip_y + S(175), cx + S(36), hip_y + S(205)], fill=CARBON_DARK)
        # Thruster Soles
        draw.line([(cx - S(34), hip_y + S(204)), (cx - S(10), hip_y + S(204))], fill=CYAN_GLOW, width=S(3))
        draw.line([(cx + S(10), hip_y + S(204)), (cx + S(34), hip_y + S(204))], fill=CYAN_GLOW, width=S(3))
        glow_draw.line([(cx - S(34), hip_y + S(204)), (cx - S(10), hip_y + S(204))], fill=WHITE, width=S(3))
        glow_draw.line([(cx + S(10), hip_y + S(204)), (cx + S(34), hip_y + S(204))], fill=WHITE, width=S(3))

    elif view == "three_quarter":
        # Front Leg (Left)
        draw.rectangle([cx - S(36), hip_y, cx - S(10), hip_y + S(115)], fill=CARBON_MAIN)
        draw.polygon(MPTS([(-38, 286 + 85), (-8, 286 + 85), (-8, 286 + 175), (-40, 286 + 175)]),
                     fill=TITANIUM_MAIN)
        draw.rectangle([cx - S(38), hip_y + S(175), cx - S(6), hip_y + S(205)], fill=CARBON_DARK)
        draw.line([(cx - S(36), hip_y + S(204)), (cx - S(8), hip_y + S(204))], fill=CYAN_GLOW, width=S(3))
        glow_draw.line([(cx - S(36), hip_y + S(204)), (cx - S(8), hip_y + S(204))], fill=WHITE, width=S(3))
        # Rear Leg (Right)
        draw.rectangle([cx + S(8), hip_y + S(5), cx + S(28), hip_y + S(115)], fill=CARBON_DARK)
        draw.polygon(MPTS([(6, 286 + 85), (30, 286 + 85), (32, 286 + 170), (8, 286 + 170)]),
                     fill=TITANIUM_DARK)
        draw.rectangle([cx + S(6), hip_y + S(170), cx + S(32), hip_y + S(200)], fill=CARBON_DARK)
        draw.line([(cx + S(8), hip_y + S(199)), (cx + S(30), hip_y + S(199))], fill=CYAN_GLOW, width=S(3))
        glow_draw.line([(cx + S(8), hip_y + S(199)), (cx + S(30), hip_y + S(199))], fill=WHITE, width=S(3))
        # Knee guard front
        draw.rectangle([cx - S(34), hip_y + S(75), cx - S(12), hip_y + S(92)], fill=TITANIUM_LIGHT)
        draw.line([(cx - S(30), hip_y + S(84)), (cx - S(16), hip_y + S(84))], fill=CYAN_MAIN, width=S(2))
        glow_draw.line([(cx - S(30), hip_y + S(84)), (cx - S(16), hip_y + S(84))], fill=WHITE, width=S(2))

    else:  # side view
        draw.rectangle([cx - S(20), hip_y, cx + S(16), hip_y + S(115)], fill=CARBON_MAIN)
        draw.polygon(MPTS([(-22, 286 + 85), (18, 286 + 85), (20, 286 + 175), (-24, 286 + 175)]),
                     fill=TITANIUM_MAIN)
        draw.polygon(MPTS([(-28, 286 + 80), (-18, 286 + 72), (-18, 286 + 95), (-28, 286 + 90)]),
                     fill=TITANIUM_LIGHT)
        draw.line([(cx - S(26), hip_y + S(85)), (cx - S(20), hip_y + S(85))], fill=CYAN_MAIN, width=S(2))
        glow_draw.line([(cx - S(26), hip_y + S(85)), (cx - S(20), hip_y + S(85))], fill=WHITE, width=S(2))
        draw.polygon(MPTS([(-30, 286 + 175), (20, 286 + 175), (22, 286 + 205), (-36, 286 + 205)]),
                     fill=CARBON_DARK)
        draw.line([(cx - S(34), hip_y + S(204)), (cx + S(18), hip_y + S(204))], fill=CYAN_GLOW, width=S(3))
        glow_draw.line([(cx - S(34), hip_y + S(204)), (cx + S(18), hip_y + S(204))], fill=WHITE, width=S(3))

    # -------------------------------------------------------------
    # 4. Upper Body (Tactical Cyber Armor Torso) - Above hip_y
    # -------------------------------------------------------------
    if view == "front":
        draw.polygon(MPTS([(-40, 195), (40, 195), (34, 286), (-34, 286)]), fill=CARBON_MAIN)
        draw.polygon(MPTS([(-36, 198), (36, 198), (28, 250), (0, 265), (-28, 250)]), fill=TITANIUM_MAIN)
        draw.rectangle([cx - S(22), S(268), cx + S(22), S(276)], fill=TITANIUM_DARK)
        draw.rectangle([cx - S(20), S(278), cx + S(20), S(284)], fill=TITANIUM_DARK)
        draw.line(MPTS([(-36, 202), (-24, 240), (0, 252)]), fill=GOLD_ACCENT, width=S(2))
        draw.line(MPTS([(36, 202), (24, 240), (0, 252)]), fill=GOLD_ACCENT, width=S(2))

        # ARC REACTOR CHEST CORE
        arc_y = S(228)
        arc_r = S(17)
        draw.ellipse([cx - arc_r, arc_y - arc_r, cx + arc_r, arc_y + arc_r], fill=CARBON_DARK, outline=TITANIUM_LIGHT, width=S(2))
        draw.ellipse([cx - arc_r + S(3), arc_y - arc_r + S(3), cx + arc_r - S(3), arc_y + arc_r - S(3)], fill=CYAN_DARK)
        draw.ellipse([cx - S(9), arc_y - S(9), cx + S(9), arc_y + S(9)], fill=CYAN_GLOW)
        draw.ellipse([cx - S(4), arc_y - S(4), cx + S(4), arc_y + S(4)], fill=CYAN_WHITE)
        glow_draw.ellipse([cx - arc_r, arc_y - arc_r, cx + arc_r, arc_y + arc_r], fill=WHITE)

        # Arms and Pauldrons
        draw.rectangle([cx - S(52), S(205), cx - S(36), S(275)], fill=CARBON_MAIN)
        draw.ellipse([cx - S(58), S(198), cx - S(34), S(224)], fill=TITANIUM_LIGHT)
        draw.rectangle([cx - S(54), S(245), cx - S(34), S(280)], fill=TITANIUM_MAIN)
        draw.ellipse([cx - S(50), S(280), cx - S(36), S(292)], fill=SKIN_MAIN)
        glow_draw.line([(cx - S(54), S(260)), (cx - S(34), S(260))], fill=WHITE, width=S(2))
        draw.line([(cx - S(54), S(260)), (cx - S(34), S(260))], fill=CYAN_MAIN, width=S(2))

        draw.rectangle([cx + S(36), S(205), cx + S(52), S(275)], fill=CARBON_MAIN)
        draw.ellipse([cx + S(34), S(198), cx + S(58), S(224)], fill=TITANIUM_LIGHT)
        draw.rectangle([cx + S(34), S(245), cx + S(54), S(280)], fill=TITANIUM_MAIN)
        draw.ellipse([cx + S(36), S(280), cx + S(50), S(292)], fill=SKIN_MAIN)
        glow_draw.line([(cx + S(34), S(260)), (cx + S(54), S(260))], fill=WHITE, width=S(2))
        draw.line([(cx + S(34), S(260)), (cx + S(54), S(260))], fill=CYAN_MAIN, width=S(2))

    elif view == "three_quarter":
        draw.polygon(MPTS([(-35, 195), (35, 195), (28, 286), (-28, 286)]), fill=CARBON_MAIN)
        draw.polygon(MPTS([(-32, 198), (32, 198), (24, 250), (-5, 265), (-28, 250)]), fill=TITANIUM_MAIN)
        arc_x = cx - S(4)
        arc_y = S(228)
        arc_r = S(16)
        draw.ellipse([arc_x - arc_r, arc_y - arc_r, arc_x + arc_r, arc_y + arc_r], fill=CARBON_DARK, outline=TITANIUM_LIGHT, width=S(2))
        draw.ellipse([arc_x - S(8), arc_y - S(8), arc_x + S(8), arc_y + S(8)], fill=CYAN_GLOW)
        draw.ellipse([arc_x - S(3), arc_y - S(3), arc_x + S(3), arc_y + S(3)], fill=CYAN_WHITE)
        glow_draw.ellipse([arc_x - arc_r, arc_y - arc_r, arc_x + arc_r, arc_y + arc_r], fill=WHITE)

        draw.rectangle([cx - S(48), S(205), cx - S(32), S(275)], fill=CARBON_MAIN)
        draw.ellipse([cx - S(54), S(198), cx - S(30), S(224)], fill=TITANIUM_LIGHT)
        draw.rectangle([cx - S(50), S(245), cx - S(30), S(280)], fill=TITANIUM_MAIN)
        draw.ellipse([cx - S(46), S(280), cx - S(32), S(292)], fill=SKIN_MAIN)
        glow_draw.line([(cx - S(50), S(260)), (cx - S(30), S(260))], fill=WHITE, width=S(2))
        draw.line([(cx - S(50), S(260)), (cx - S(30), S(260))], fill=CYAN_MAIN, width=S(2))

        draw.rectangle([cx + S(30), S(205), cx + S(44), S(265)], fill=CARBON_DARK)
        draw.ellipse([cx + S(28), S(198), cx + S(48), S(220)], fill=TITANIUM_MAIN)

    elif view == "side":
        draw.polygon(MPTS([(-24, 195), (22, 195), (18, 286), (-20, 286)]), fill=CARBON_MAIN)
        draw.polygon(MPTS([(-26, 198), (16, 198), (12, 250), (-22, 250)]), fill=TITANIUM_MAIN)
        draw.polygon(MPTS([(-27, 218), (-21, 222), (-21, 234), (-27, 238)]), fill=CYAN_GLOW)
        glow_draw.polygon(MPTS([(-27, 218), (-21, 222), (-21, 234), (-27, 238)]), fill=WHITE)

        draw.rectangle([cx - S(14), S(205), cx + S(6), S(275)], fill=CARBON_MAIN)
        draw.ellipse([cx - S(18), S(198), cx + S(10), S(224)], fill=TITANIUM_LIGHT)
        draw.rectangle([cx - S(16), S(245), cx + S(8), S(280)], fill=TITANIUM_MAIN)
        draw.ellipse([cx - S(12), S(280), cx + S(4), S(292)], fill=SKIN_MAIN)
        glow_draw.line([(cx - S(16), S(260)), (cx + S(8), S(260))], fill=WHITE, width=S(2))
        draw.line([(cx - S(16), S(260)), (cx + S(8), S(260))], fill=CYAN_MAIN, width=S(2))

    else:  # back view
        draw.polygon(MPTS([(-40, 195), (40, 195), (34, 286), (-34, 286)]), fill=CARBON_MAIN)
        draw.polygon(MPTS([(-26, 198), (26, 198), (18, 275), (-18, 275)]), fill=TITANIUM_MAIN)
        draw.rectangle([cx - S(30), S(215), cx - S(12), S(255)], fill=CARBON_DARK, outline=TITANIUM_LIGHT, width=S(1))
        draw.rectangle([cx + S(12), S(215), cx + S(30), S(255)], fill=CARBON_DARK, outline=TITANIUM_LIGHT, width=S(1))
        draw.ellipse([cx - S(28), S(250), cx - S(14), S(258)], fill=CYAN_GLOW)
        draw.ellipse([cx + S(14), S(250), cx + S(28), S(258)], fill=CYAN_GLOW)
        glow_draw.ellipse([cx - S(28), S(250), cx - S(14), S(258)], fill=WHITE)
        glow_draw.ellipse([cx + S(14), S(250), cx + S(28), S(258)], fill=WHITE)

    # -------------------------------------------------------------
    # 5. Head & Anime Face (y: 40 to 190)
    # -------------------------------------------------------------
    if view != "back":
        draw.rectangle([cx - S(14), S(160), cx + S(14), S(198)], fill=SKIN_SHADOW)
        if view == "front":
            face_pts = MPTS([(-52, 90), (52, 90), (46, 145), (25, 172),
                             (0, 180), (-25, 172), (-46, 145)])
        elif view == "three_quarter":
            face_pts = MPTS([(-50, 90), (48, 90), (42, 145), (18, 172),
                             (-8, 180), (-32, 172), (-48, 145)])
        else:  # side
            face_pts = MPTS([(-35, 90), (38, 90), (34, 145), (15, 170),
                             (-22, 180), (-34, 165)])
        draw.polygon(face_pts, fill=SKIN_MAIN)

        if view == "front":
            # Left Eye
            draw.ellipse([cx - S(38), S(126), cx - S(16), S(152)], fill=CARBON_MAIN)
            draw.ellipse([cx - S(34), S(130), cx - S(20), S(150)], fill=CYAN_DARK)
            draw.ellipse([cx - S(32), S(134), cx - S(22), S(148)], fill=CYAN_GLOW)
            draw.ellipse([cx - S(30), S(132), cx - S(24), S(138)], fill=WHITE)
            glow_draw.ellipse([cx - S(32), S(134), cx - S(22), S(148)], fill=WHITE)
            # Right Eye
            draw.ellipse([cx + S(16), S(126), cx + S(38), S(152)], fill=CARBON_MAIN)
            draw.ellipse([cx + S(20), S(130), cx + S(34), S(150)], fill=CYAN_DARK)
            draw.ellipse([cx + S(22), S(134), cx + S(32), S(148)], fill=CYAN_GLOW)
            draw.ellipse([cx + S(24), S(132), cx + S(30), S(138)], fill=WHITE)
            glow_draw.ellipse([cx + S(22), S(134), cx + S(32), S(148)], fill=WHITE)
            draw.ellipse([cx - S(44), S(148), cx - S(24), S(158)], fill=BLUSH)
            draw.ellipse([cx + S(24), S(148), cx + S(44), S(158)], fill=BLUSH)
            draw.line([(cx - S(8), S(164)), (cx, S(167)), (cx + S(8), S(164))], fill=(180, 110, 100, 255), width=S(2))

        elif view == "three_quarter":
            draw.ellipse([cx - S(36), S(126), cx - S(14), S(152)], fill=CARBON_MAIN)
            draw.ellipse([cx - S(32), S(130), cx - S(18), S(150)], fill=CYAN_DARK)
            draw.ellipse([cx - S(30), S(134), cx - S(20), S(148)], fill=CYAN_GLOW)
            draw.ellipse([cx - S(28), S(132), cx - S(22), S(138)], fill=WHITE)
            glow_draw.ellipse([cx - S(30), S(134), cx - S(20), S(148)], fill=WHITE)

            draw.ellipse([cx + S(14), S(128), cx + S(30), S(150)], fill=CARBON_MAIN)
            draw.ellipse([cx + S(16), S(132), cx + S(28), S(148)], fill=CYAN_GLOW)
            draw.ellipse([cx + S(18), S(132), cx + S(24), S(138)], fill=WHITE)
            glow_draw.ellipse([cx + S(16), S(132), cx + S(28), S(148)], fill=WHITE)
            draw.ellipse([cx - S(40), S(148), cx - S(20), S(158)], fill=BLUSH)
            draw.line([(cx - S(10), S(165)), (cx - S(2), S(167)), (cx + S(5), S(164))], fill=(180, 110, 100, 255), width=S(2))

        else:  # side
            draw.polygon(MPTS([(-28, 132), (-12, 126), (-14, 146)]), fill=CARBON_MAIN)
            draw.polygon(MPTS([(-24, 133), (-14, 130), (-16, 144)]), fill=CYAN_GLOW)
            draw.ellipse([cx - S(20), S(132), cx - S(16), S(138)], fill=WHITE)
            glow_draw.polygon(MPTS([(-24, 133), (-14, 130), (-16, 144)]), fill=WHITE)
            draw.ellipse([cx - S(26), S(148), cx - S(10), S(158)], fill=BLUSH)
            draw.line([(cx - S(24), S(164)), (cx - S(16), S(166))], fill=(180, 110, 100, 255), width=S(2))

        # Holographic Arc Visor & Ear Fins
        if view == "front":
            visor_pts = MPTS([(-50, 118), (50, 118), (42, 134), (0, 138), (-42, 134)])
            draw.polygon(visor_pts, fill=(0, 210, 255, 170))
            draw.line(MPTS([(-50, 118), (50, 118)]), fill=CYAN_WHITE, width=S(2))
            glow_draw.polygon(visor_pts, fill=WHITE)

            # Left Ear Fin
            draw.polygon(MPTS([(-58, 120), (-72, 85), (-54, 105), (-48, 135)]), fill=TITANIUM_LIGHT)
            draw.ellipse([cx - S(58), S(122), cx - S(44), S(142)], fill=CARBON_DARK, outline=CYAN_MAIN, width=S(2))
            draw.ellipse([cx - S(53), S(128), cx - S(49), S(136)], fill=CYAN_GLOW)
            glow_draw.ellipse([cx - S(53), S(128), cx - S(49), S(136)], fill=WHITE)

            # Right Ear Fin
            draw.polygon(MPTS([(58, 120), (72, 85), (54, 105), (48, 135)]), fill=TITANIUM_LIGHT)
            draw.ellipse([cx + S(44), S(122), cx + S(58), S(142)], fill=CARBON_DARK, outline=CYAN_MAIN, width=S(2))
            draw.ellipse([cx + S(49), S(128), cx + S(53), S(136)], fill=CYAN_GLOW)
            glow_draw.ellipse([cx + S(49), S(128), cx + S(53), S(136)], fill=WHITE)

        elif view == "three_quarter":
            visor_pts = MPTS([(-48, 118), (46, 118), (38, 134), (-2, 138), (-40, 134)])
            draw.polygon(visor_pts, fill=(0, 210, 255, 170))
            draw.line(MPTS([(-48, 118), (46, 118)]), fill=CYAN_WHITE, width=S(2))
            glow_draw.polygon(visor_pts, fill=WHITE)

            draw.polygon(MPTS([(-56, 120), (-70, 85), (-52, 105), (-46, 135)]), fill=TITANIUM_LIGHT)
            draw.ellipse([cx - S(56), S(122), cx - S(42), S(142)], fill=CARBON_DARK, outline=CYAN_MAIN, width=S(2))
            draw.ellipse([cx - S(51), S(128), cx - S(47), S(136)], fill=CYAN_GLOW)
            glow_draw.ellipse([cx - S(51), S(128), cx - S(47), S(136)], fill=WHITE)

        else:  # side
            visor_pts = MPTS([(-32, 120), (10, 118), (8, 134), (-26, 136)])
            draw.polygon(visor_pts, fill=(0, 210, 255, 170))
            draw.line(MPTS([(-32, 120), (10, 118)]), fill=CYAN_WHITE, width=S(2))
            glow_draw.polygon(visor_pts, fill=WHITE)

            draw.polygon(MPTS([(12, 118), (32, 85), (24, 110), (16, 138)]), fill=TITANIUM_LIGHT)
            draw.ellipse([cx + S(4), S(120), cx + S(22), S(144)], fill=CARBON_DARK, outline=CYAN_MAIN, width=S(2))
            draw.ellipse([cx + S(10), S(127), cx + S(16), S(137)], fill=CYAN_GLOW)
            glow_draw.ellipse([cx + S(10), S(127), cx + S(16), S(137)], fill=WHITE)

    # -------------------------------------------------------------
    # 6. Front Platinum Anime Hair Bangs & Spikes
    # -------------------------------------------------------------
    if view != "back":
        if view == "front":
            draw.ellipse([cx - S(60), S(42), cx + S(60), S(125)], fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-45, 75), (-55, 125), (-32, 105)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-30, 80), (-24, 120), (-10, 100)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-12, 80), (0, 128), (14, 98)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(10, 80), (26, 120), (32, 100)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(30, 75), (55, 125), (42, 105)]), fill=PLATINUM_HAIR)
            draw.line(MPTS([(0, 55), (-8, 25), (6, 18), (12, 32)]), fill=PLATINUM_HAIR, width=S(4))

        elif view == "three_quarter":
            draw.ellipse([cx - S(58), S(42), cx + S(58), S(125)], fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-42, 75), (-52, 125), (-30, 105)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-28, 80), (-18, 125), (-5, 100)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-8, 80), (8, 128), (20, 98)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(15, 80), (38, 122), (42, 102)]), fill=PLATINUM_HAIR)
            draw.line(MPTS([(-5, 55), (-14, 25), (0, 18), (8, 32)]), fill=PLATINUM_HAIR, width=S(4))

        else:  # side
            draw.ellipse([cx - S(42), S(42), cx + S(46), S(125)], fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-32, 75), (-38, 125), (-18, 105)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(-18, 80), (-8, 128), (10, 100)]), fill=PLATINUM_HAIR)
            draw.polygon(MPTS([(5, 80), (24, 122), (32, 102)]), fill=PLATINUM_HAIR)
            draw.line(MPTS([(-8, 55), (-18, 25), (-4, 18), (4, 32)]), fill=PLATINUM_HAIR, width=S(4))

    # -------------------------------------------------------------
    # 7. Holographic Floating Arc Reactor Orbit Ring
    # -------------------------------------------------------------
    ring_y = hip_y - S(12)
    rx = W // 2
    rw = S(88)
    rh = S(14)
    draw.ellipse([rx - rw, ring_y - rh, rx + rw, ring_y + rh], outline=(0, 210, 255, 140), width=S(2))
    glow_draw.ellipse([rx - rw, ring_y - rh, rx + rw, ring_y + rh], outline=(255, 255, 255, 220), width=S(2))

    # Split Layers
    dim_glow = Image.eval(glow_im.getchannel("A"), lambda x: 255 - int(x * 0.45))
    r, g, b, a = im.split()
    base = Image.merge("RGBA", (*[ImageChops.multiply(c, dim_glow) for c in (r, g, b)], a))

    white = Image.new("L", im.size, 255)
    glow_alpha = glow_im.getchannel("A")
    glow = Image.merge("RGBA", (white, white, white, glow_alpha))
    bloom = Image.merge("RGBA", (white, white, white, glow_alpha.filter(ImageFilter.GaussianBlur(S(14)))))

    return base, glow, bloom, im


def generate_layers_core():
    """Generate 160x160 master and 80x80 notch/tray Arc Reactor Core emblem."""
    S_CORE = 160
    im = Image.new("RGBA", (S_CORE, S_CORE), TRANSPARENT)
    draw = ImageDraw.Draw(im)

    glow = Image.new("RGBA", (S_CORE, S_CORE), TRANSPARENT)
    gdraw = ImageDraw.Draw(glow)

    cx, cy = S_CORE // 2, S_CORE // 2

    # Outer titanium chassis
    draw.ellipse([cx - 64, cy - 64, cx + 64, cy + 64], fill=CARBON_DARK, outline=TITANIUM_LIGHT, width=4)
    # 8 Radial emitter teeth
    for i in range(8):
        ang = i * (math.pi / 4)
        x0 = cx + math.cos(ang) * 48
        y0 = cy + math.sin(ang) * 48
        x1 = cx + math.cos(ang) * 62
        y1 = cy + math.sin(ang) * 62
        draw.line([(x0, y0), (x1, y1)], fill=TITANIUM_LIGHT, width=6)

    # Arc Reactor Coil Ring
    draw.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=CARBON_MAIN, outline=CYAN_DARK, width=4)
    gdraw.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], outline=WHITE, width=4)

    # Glowing Cyan Core
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=CYAN_GLOW)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=CYAN_WHITE)
    gdraw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=WHITE)

    white = Image.new("L", (S_CORE, S_CORE), 255)
    ga = glow.getchannel("A")
    glow_final = Image.merge("RGBA", (white, white, white, ga))
    bloom_final = Image.merge("RGBA", (white, white, white, ga.filter(ImageFilter.GaussianBlur(10))))

    mask_visor = Image.new("L", (S_CORE, S_CORE), 0)
    vdraw = ImageDraw.Draw(mask_visor)
    vdraw.rectangle([cx - 48, cy - 16, cx + 48, cy + 12], fill=255)

    mask_core = Image.new("L", (S_CORE, S_CORE), 0)
    cdraw = ImageDraw.Draw(mask_core)
    cdraw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=255)

    mask_chev = Image.new("L", (S_CORE, S_CORE), 0)
    chdraw = ImageDraw.Draw(mask_chev)
    chdraw.line([(cx - 36, cy + 32), (cx, cy + 44), (cx + 36, cy + 32)], fill=255, width=8)

    # Downsample cleanly to 80x80 runtime standard with LANCZOS
    os.makedirs(LAYERS_DIR, exist_ok=True)
    im.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "base.png"))
    glow_final.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "glow.png"))
    bloom_final.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "bloom.png"))
    mask_visor.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "mask_visor.png"))
    mask_core.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "mask_core.png"))
    mask_chev.resize((80, 80), Image.LANCZOS).save(os.path.join(LAYERS_DIR, "mask_chev.png"))
    print("Arc Reactor Core layers generated (160px master -> 80px runtime)")


def create_showcase_sheet():
    """Create a composite 2400x1200 turnaround concept showcase board."""
    SW, SH = 2400, 1200
    board = Image.new("RGBA", (SW, SH), (14, 18, 24, 255))
    bdraw = ImageDraw.Draw(board)

    # Grid background lines
    for x in range(0, SW, 60):
        bdraw.line([(x, 0), (x, SH)], fill=(22, 28, 38, 255), width=1)
    for y in range(0, SH, 60):
        bdraw.line([(0, y), (SW, y)], fill=(22, 28, 38, 255), width=1)

    # Title header
    bdraw.text((70, 45), "JARVIS // ARC SENTINEL AVATAR SYSTEM", fill=CYAN_GLOW)
    bdraw.text((70, 85), "ANIME CHIBI COMMANDER EDITION · 1024PX ULTRA-HD SPRITE ARSENAL (2X MASTER)", fill=(140, 160, 190, 255))

    # Color Palette Swatches
    swatches = [
        ("ARC CYAN", (0, 240, 255)),
        ("AZURE", (0, 190, 235)),
        ("TITANIUM", (75, 88, 108)),
        ("OBSIDIAN", (20, 24, 32)),
        ("PLATINUM", (225, 235, 248)),
        ("GOLD", (235, 185, 55)),
    ]
    sx = 1500
    for label, col in swatches:
        bdraw.rectangle([sx, 50, sx + 40, 85], fill=col + (255,), outline=(60, 75, 95, 255))
        bdraw.text((sx + 50, 60), label, fill=(160, 180, 210, 255))
        sx += 140

    views = ["front", "three_quarter", "side", "back"]
    labels = ["FRONT VIEW", "THREE-QUARTER", "SIDE STRIDE", "REAR SPINE"]
    spacing = SW // 4

    for idx, (v, lbl) in enumerate(zip(views, labels)):
        fpath = os.path.join(BODY_DIR, f"{v}_full.png")
        if os.path.exists(fpath):
            fig = Image.open(fpath)
            target_h = 920
            target_w = int(fig.width * target_h / fig.height)
            fig_scaled = fig.resize((target_w, target_h), Image.LANCZOS)
            px = idx * spacing + (spacing - target_w) // 2
            py = 180
            # Ground platform ellipse
            bdraw.ellipse([px - 20, py + target_h - 25, px + target_w + 20, py + target_h + 20],
                          outline=CYAN_DARK, width=2)
            bdraw.ellipse([px + target_w // 2 - 50, py + target_h - 15, px + target_w // 2 + 50, py + target_h + 10],
                          fill=(0, 240, 255, 60))
            board.alpha_composite(fig_scaled, (px, py))
            bdraw.text((px + target_w // 2 - 60, py + target_h + 30), lbl, fill=CYAN_MAIN)

    os.makedirs(CONCEPTS_DIR, exist_ok=True)
    out_path = os.path.join(CONCEPTS_DIR, "jarvis_anime_turnaround_sheet.png")
    board.save(out_path)
    print(f"Ultra-HD Showcase turnaround sheet generated: {out_path} ({SW}x{SH})")


def main():
    os.makedirs(BODY_DIR, exist_ok=True)
    views = ["front", "three_quarter", "side", "back"]

    print("Generating Anime JARVIS 1024px Ultra-HD sprite assets (2x Large Master)...")
    for v in views:
        base, glow, bloom, full = create_body_sprite(v)
        base.save(os.path.join(BODY_DIR, f"{v}_base.png"))
        glow.save(os.path.join(BODY_DIR, f"{v}_glow.png"))
        bloom.save(os.path.join(BODY_DIR, f"{v}_bloom.png"))
        full.save(os.path.join(BODY_DIR, f"{v}_full.png"))
        print(f"  + {v:<14} ({full.width}x{full.height}) base, glow, bloom, full")

    generate_layers_core()
    create_showcase_sheet()
    print("All 1024px Anime JARVIS sprite assets successfully generated!")


if __name__ == "__main__":
    main()
