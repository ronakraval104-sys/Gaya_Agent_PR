"""Full-body Anime JARVIS - renders the Arc Sentinel commander from art/body.

Poses by state:
  standing (idle/thinking/spawning/approved/broken) : three-quarter view, breathing
  needs Boss (hold)                                 : turns to face you (front view)
  walking                                           : side view facing travel direction,
                                                      legs swing from the hip, step bob + sway
  dozing / asleep                                   : front view, lights banked
The white light layer is recoloured per state, exactly like the Arc Reactor head core.
"""
import math
import os

from PIL import Image
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient, QTransform

from sprite_ui import ui_font
from jarvis_island import STATE_RGB, to_pixmap

HERE = os.path.dirname(os.path.abspath(__file__))
BODY_DIR = os.path.join(HERE, "art", "body")
VIEWS = ("front", "three_quarter", "side")
HIP = 0.56            # hip line as a fraction of height (legs below it swing)
WALK_HZ = 1.5         # steps per second
STRIDE_DEG = 24       # leg swing either side of vertical
# ground speed = stride length x step rate
WALK_SPEED = 2 * 0.44 * 132 * math.sin(math.radians(STRIDE_DEG)) * WALK_HZ   # px/s at 132 px tall


def available():
    return all(os.path.exists(os.path.join(BODY_DIR, "%s_base.png" % v)) for v in VIEWS)


def compose(view, rgb, glow_k, bloom_k, body_k, h_px):
    base_path = os.path.join(BODY_DIR, view + "_base.png")
    if not os.path.exists(base_path):
        base_path = os.path.join(BODY_DIR, "front_base.png")
    base = Image.open(base_path).convert("RGBA")
    if body_k < 1:
        base.putalpha(base.getchannel("A").point(lambda v: int(v * body_k)))
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    out.alpha_composite(base)
    for name, k in (("bloom", bloom_k), ("glow", glow_k)):
        if k <= 0:
            continue
        lpath = os.path.join(BODY_DIR, "%s_%s.png" % (view, name))
        if not os.path.exists(lpath):
            continue
        a = Image.open(lpath).getchannel("A").point(lambda v: min(255, int(v * k)))
        lay = Image.new("RGBA", base.size, rgb + (255,))
        lay.putalpha(a)
        out.alpha_composite(lay)
    w = max(1, round(out.width * h_px / out.height))
    # Downsample from 1024px master with Lanczos for razor-sharp Retina fidelity
    return out.resize((w, h_px), Image.LANCZOS)


class Body:
    def __init__(self, dpr, height):
        self.h = height
        # Render high-res buffer to stay razor-sharp at 2.0x scale
        px = round(height * dpr * 2)
        self.pm = {}
        for v in VIEWS:
            for s, rgb in STATE_RGB.items():
                self.pm[(v, s)] = (to_pixmap(compose(v, rgb, .45, .2, 1, px), dpr * 2),
                                   to_pixmap(compose(v, rgb, 1, .8, 1, px), dpr * 2))
        self.sleep = to_pixmap(compose("front", STATE_RGB["asleep"], .08, 0, .7, px), dpr * 2)
        self.width = max(self.pm[(v, "idle")][0].width() / (dpr * 2) for v in VIEWS)

    def paint(self, sprite, p, t, st, doze, hop, shake, pad):
        H = self.h
        walking = getattr(sprite, "walking", False)
        facing = getattr(sprite, "facing", 1)
        if doze:
            view = "front"
        elif walking:
            view = "side"
        elif st == "hold" or sprite.drag:
            view = "front"
        else:
            view = "three_quarter"
        dim, bright = self.pm.get((view, st), self.pm.get((view, "idle"), self.pm[("front", "idle")]))
        dpr_factor = dim.devicePixelRatio()
        w = dim.width() / dpr_factor
        feet_y = pad + H
        bw = getattr(sprite, "base_w", sprite.width())
        cx = bw / 2 + shake

        # step cycle - legs swing from hip, torso glides
        phase = t * 2 * math.pi * WALK_HZ
        step_bob = -(0.5 + 0.5 * math.cos(2 * phase)) * 1.2 if walking else 0
        breathe = 1 + 0.010 * math.sin(t * 1.6) if not walking else 1.0
        sway = math.sin(phase) * 0.8 if walking else math.sin(t * 0.8) * 0.6
        lean = max(-10.0, min(10.0, sprite.vel[0] * 0.8)) if not walking else 3.0

        # ground shadow under thruster boots
        sh_w = w * (0.85 - 0.25 * (abs(hop) / 14))
        g = QRadialGradient(QPointF(bw / 2, feet_y + 2), sh_w / 2)
        g.setColorAt(0, QColor(0, 0, 0, 130))
        g.setColorAt(1, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawEllipse(QPointF(bw / 2, feet_y + 2), sh_w / 2, 5)

        # Aura
        rgb = STATE_RGB.get(st, STATE_RGB["idle"])
        k_aura = {"hold": 0.45, "approved": 0.35, "broken": 0.35, "spawning": 0.22}.get(st, 0.0)
        if k_aura and not doze:
            k_aura += 0.08 * math.sin(t * 2)
            a = QRadialGradient(QPointF(cx, feet_y - H * 0.5), H * 0.5)
            a.setColorAt(0, QColor(*rgb, int(255 * k_aura * 0.5)))
            a.setColorAt(0.6, QColor(*rgb, int(255 * k_aura * 0.15)))
            a.setColorAt(1, QColor(*rgb, 0))
            p.setBrush(a)
            p.drawEllipse(QPointF(cx, feet_y - H * 0.5), H * 0.36, H * 0.52)

        # ---------------------------------------------------------
        # Holographic Arc Reactor HUD Ring floating behind head
        # ---------------------------------------------------------
        hud_y = feet_y - H * 0.76 + hop * 0.4
        hud_r = H * 0.22
        k_hud = 0.32 + 0.12 * math.sin(t * 2.5) if not doze else 0.08
        if st == "hold":
            k_hud = 0.60 + 0.18 * math.sin(t * 4.5)

        # Outer Holographic Glow
        a_hud = QRadialGradient(QPointF(cx, hud_y), hud_r * 1.3)
        a_hud.setColorAt(0, QColor(*rgb, int(255 * k_hud * 0.6)))
        a_hud.setColorAt(0.6, QColor(*rgb, int(255 * k_hud * 0.2)))
        a_hud.setColorAt(1, QColor(*rgb, 0))
        p.setBrush(a_hud)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, hud_y), hud_r * 1.3, hud_r * 1.3)

        # Rotating Arc Targeting Ring & Telemetry Reticles
        p.save()
        p.translate(cx, hud_y)
        p.rotate(t * 22.0 if not doze else 0.0)
        pen_cyan = QPen(QColor(*rgb, int(255 * k_hud)), 1.5)
        p.setPen(pen_cyan)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(0, 0), hud_r * 0.88, hud_r * 0.88)
        p.drawEllipse(QPointF(0, 0), hud_r * 0.60, hud_r * 0.60)
        # 4 Stark HUD Crosshair brackets
        for spoke in range(4):
            ang = spoke * (math.pi / 2)
            p.drawLine(QPointF(math.cos(ang) * hud_r * 0.55, math.sin(ang) * hud_r * 0.55),
                       QPointF(math.cos(ang) * hud_r * 0.98, math.sin(ang) * hud_r * 0.98))
        # 8 Minor tick marks
        for tick in range(8):
            ang = tick * (math.pi / 4) + (math.pi / 8)
            p.drawLine(QPointF(math.cos(ang) * hud_r * 0.75, math.sin(ang) * hud_r * 0.75),
                       QPointF(math.cos(ang) * hud_r * 0.88, math.sin(ang) * hud_r * 0.88))
        p.restore()

        # Repulsor thruster sparks on hop
        if abs(hop) > 2 and not doze:
            p.save()
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 240, 255, int(220 * (abs(hop) / 14))))
            for idx, off in enumerate([-26, -12, 12, 26]):
                sy = feet_y - H * 0.35 + math.sin(t * 14 + idx) * 18
                p.drawEllipse(QPointF(cx + off, sy), 2.5, 2.5)
            p.restore()

        # Character Puppet Render
        p.save()
        p.translate(cx, feet_y + hop + step_bob)
        p.rotate(sway + lean + (math.sin(t * 18) * 12 * sprite.anim["dizzy"]))
        # Side art faces LEFT naturally; mirror when travelling RIGHT (facing == 1)
        mirror = (view in ("side", "three_quarter") and facing == 1)
        p.scale((-1 if mirror else 1) * (1.06 if sprite.hover else 1.0), breathe * (1.06 if sprite.hover else 1.0))
        k = 0.55 + 0.45 * math.sin(t * 2 * math.pi / {"idle": 3.6, "thinking": 1.4, "spawning": .9, "hold": 1.1,
                                                        "broken": .5, "approved": 1.0}.get(st, 3.6))
        if sprite.hover:
            k = max(k, .9)
        if st in ("idle", "thinking") and (t % 5.5) < 0.11:
            k = 0.0  # Arc visor blink

        def draw_puppet(pm, opacity):
            src = QRectF(0, 0, pm.width(), pm.height())
            if not walking:
                p.setOpacity(opacity)
                p.drawPixmap(QRectF(-w / 2, -H, w, H), pm, src)
                return
            # puppet walk: lower body drawn twice as swinging legs, torso on top
            hip_y_local = -H * (1 - HIP)
            legs_src = QRectF(0, pm.height() * HIP, pm.width(), pm.height() * (1 - HIP))
            legs_dst = QRectF(-w / 2, hip_y_local, w, H * (1 - HIP))
            theta = STRIDE_DEG * math.sin(phase)
            for ang, mult in ((-theta, 0.78), (theta, 1.0)):
                p.save()
                p.translate(0, hip_y_local)
                p.rotate(ang)
                p.translate(0, -hip_y_local)
                p.setOpacity(opacity * mult)
                p.drawPixmap(legs_dst, pm, legs_src)
                p.restore()
            torso_pct = HIP + 0.04
            p.setOpacity(opacity)
            p.drawPixmap(QRectF(-w / 2, -H, w, H * torso_pct), pm, QRectF(0, 0, pm.width(), pm.height() * torso_pct))

        if doze:
            draw_puppet(self.sleep, 1.0)
        else:
            draw_puppet(dim, 1.0)
            draw_puppet(bright, k)
        p.setOpacity(1)
        p.restore()

        # Permission request count badge
        if sprite.requests:
            n = len(sprite.requests)
            bx, by = cx + w * 0.42, feet_y - H * 0.96
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 75, 75))
            p.drawEllipse(QPointF(bx, by), 8, 8)
            p.setPen(QColor(255, 255, 255))
            p.setFont(ui_font(8.5, True))
            p.drawText(QRectF(bx - 8, by - 8, 16, 16), Qt.AlignCenter, str(n))

        if doze:
            p.setPen(QColor(140, 180, 240, 160))
            p.setFont(ui_font(8.5, True))
            for i in range(3):
                ph = (t * 0.4 + i / 3) % 1
                p.setOpacity(1 - ph)
                p.drawText(QPointF(cx + 12 + ph * 14, feet_y - H * 0.9 - ph * 22), "z")
            p.setOpacity(1)
