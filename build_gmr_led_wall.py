"""
GMR LED Video Wall — 3D Model Generator (v2 - All Box Primitives)
Client: Jay Pandya / Visual Rhyme
Reference: GMR group.pdf (Dwg: R-LED-FRAME-001)
Output: GLB file for import into 3ds Max

Specs:
  - 12x4 cabinet matrix (337.5x600mm each)
  - 2 deg curve between columns (~9.67m radius)
  - ACP border: 6" top, 3" left/right/bottom
  - Lower half (rows 2-3) covered by opaque sheet + ACP
  - Support structure per reference drawing
"""

import trimesh
import numpy as np
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
import math
import os

# ═══════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════

NUM_COLS = 12
NUM_ROWS = 4
CAB_W = 337.5        # cabinet width (mm)
CAB_H = 600.0        # cabinet height (mm)
CAB_D = 75.0         # cabinet depth (mm)
CURVE_DEG = 2.0      # degrees between adjacent columns
RADIUS = CAB_W / (2.0 * math.sin(math.radians(CURVE_DEG / 2.0)))

SCREEN_W_ARC = NUM_COLS * CAB_W          # 4050mm along arc
SCREEN_H = NUM_ROWS * CAB_H              # 2400mm

ACP_TOP = 152.4       # 6 inches (mm)
ACP_SIDE = 76.2       # 3 inches (mm)

STRUCT_WIDTH = 7200.0
STRUCT_DEPTH = 4000.0
STRUCT_HEIGHT = 2500.0
COL_SIZE = 38.1       # 1.5" square column
BEAM_W = 100.0
BEAM_H = 50.0
SUB_W = 40.0          # sub-frame tube size
BASE_PLATE = 300.0

SEGMENTS_CURVE = 48   # segments for smooth curved sweeps

# Curve direction: +1 = concave (edges forward), -1 = convex (edges back)
CURVE_SIGN = 1
# Offset to push entire screen in front of structure (Z >= 0)
SCREEN_Z_OFFSET = CAB_D + 20  # 95mm — cabinet back clears structure front

# ═══════════════════════════════════════════════
#  MATERIALS
# ═══════════════════════════════════════════════

mat_led_body = PBRMaterial(
    baseColorFactor=[0.07, 0.07, 0.09, 1.0],
    metallicFactor=0.3, roughnessFactor=0.6,
    name="LED_Cabinet_Body")
mat_led_face = PBRMaterial(
    baseColorFactor=[0.015, 0.015, 0.025, 1.0],
    metallicFactor=0.0, roughnessFactor=0.9,
    emissiveFactor=[0.003, 0.003, 0.008],
    name="LED_Face")
mat_steel = PBRMaterial(
    baseColorFactor=[0.35, 0.35, 0.37, 1.0],
    metallicFactor=0.8, roughnessFactor=0.4,
    name="Steel_Structure")
mat_steel_dark = PBRMaterial(
    baseColorFactor=[0.15, 0.15, 0.17, 1.0],
    metallicFactor=0.6, roughnessFactor=0.6,
    name="Steel_Dark")
mat_acp = PBRMaterial(
    baseColorFactor=[0.88, 0.88, 0.90, 1.0],
    metallicFactor=0.05, roughnessFactor=0.25,
    name="ACP_White")
mat_opaque = PBRMaterial(
    baseColorFactor=[0.10, 0.10, 0.12, 1.0],
    metallicFactor=0.1, roughnessFactor=0.85,
    name="Opaque_Sheet")
mat_subframe = PBRMaterial(
    baseColorFactor=[0.25, 0.25, 0.27, 1.0],
    metallicFactor=0.5, roughnessFactor=0.5,
    name="SubFrame")
mat_neoprene = PBRMaterial(
    baseColorFactor=[0.08, 0.08, 0.08, 1.0],
    metallicFactor=0.0, roughnessFactor=1.0,
    name="Neoprene_Pad")

# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════

def deg2rad(d):
    return d * math.pi / 180.0

def col_angle(col):
    return (col - (NUM_COLS - 1) / 2.0) * CURVE_DEG

def cabinet_pose(col, row):
    """Returns (position [x,y,z], y-rotation in rad)
       CONCAVE: edges forward (+Z), center back. Rotation flips to match."""
    theta = col_angle(col)
    tr = deg2rad(theta)
    x = RADIUS * math.sin(tr)
    z = CURVE_SIGN * (RADIUS * (1.0 - math.cos(tr))) + SCREEN_Z_OFFSET
    y = row * CAB_H + CAB_H / 2.0
    # Flip rotation for concave: cabinets face outward from curve center
    rot = tr if CURVE_SIGN < 0 else -tr
    return np.array([x, y, z]), rot

def make_box(extents, material, transform=None):
    mesh = trimesh.primitives.Box(extents=extents)
    mesh.visual = TextureVisuals(material=material)
    if transform is not None:
        mesh.apply_transform(transform)
    return mesh

def tf(pos, rot_y_rad=0.0):
    T = trimesh.transformations.translation_matrix(pos)
    if abs(rot_y_rad) > 1e-10:
        R = trimesh.transformations.rotation_matrix(rot_y_rad, [0, 1, 0])
        return np.dot(T, R)
    return T

# Alias for readability
def transform_4x4(pos, rot_y_rad):
    return tf(pos, rot_y_rad)

def point_on_arc(theta_deg, z_offset=0.0):
    """Returns (x, z) on the curve at given theta angle."""
    tr = deg2rad(theta_deg)
    x = RADIUS * math.sin(tr)
    z = CURVE_SIGN * (RADIUS * (1.0 - math.cos(tr))) + z_offset
    return x, z

def arc_segment_boxes(span_width, bar_height, bar_depth, y_pos,
                      material, num_seg=24, z_offset=0.0):
    """
    Create a curved bar along the screen arc using individual box segments.
    Each box is a small segment approximating the curve.
    CONCAVE: curve goes +Z direction, rotation flips.
    """
    half_span = span_width / 2.0
    meshes = []
    for i in range(num_seg):
        t0 = i / num_seg
        t1 = (i + 1) / num_seg
        
        # Find theta for left and right edges of this segment
        x0 = -half_span + t0 * span_width
        x1 = -half_span + t1 * span_width
        
        # Clamp to radius
        x0_clamped = max(min(x0, RADIUS * 0.99), -RADIUS * 0.99)
        x1_clamped = max(min(x1, RADIUS * 0.99), -RADIUS * 0.99)
        
        theta0 = math.asin(x0_clamped / RADIUS)
        theta1 = math.asin(x1_clamped / RADIUS)
        
        # CONCAVE: +Z direction
        z0 = CURVE_SIGN * (RADIUS * (1.0 - math.cos(theta0)))
        z1 = CURVE_SIGN * (RADIUS * (1.0 - math.cos(theta1)))
        
        cx = (x0 + x1) / 2.0
        cz = (z0 + z1) / 2.0 + z_offset
        seg_angle = (theta0 + theta1) / 2.0
        
        # Flip rotation sign for concave
        seg_rot = -seg_angle if CURVE_SIGN > 0 else seg_angle
        
        seg_width = math.sqrt((x1 - x0)**2 + (z1 - z0)**2)
        
        m = make_box(
            [seg_width, bar_height, bar_depth],
            material,
            tf([cx, y_pos, cz], seg_rot)
        )
        meshes.append(m)
    return meshes


# ═══════════════════════════════════════════════
#  BUILD SCENE
# ═══════════════════════════════════════════════

scene = trimesh.Scene()

print("=" * 60)
print("GMR LED Video Wall Builder (v2 - Box Sweep)")
print(f"Radius: {RADIUS:.1f}mm  |  Screen: {SCREEN_W_ARC:.0f}x{SCREEN_H:.0f}mm")
print("=" * 60)

# ───── 1. SUPPORT STRUCTURE ─────
print("\n[1/5] Building support structure...")

# Structure Z offset — front beam set back slightly from screen to avoid intersection
STRUCT_Z_OFFSET = -20  # mm — structure sits behind cabinet mounting plane

# Base frame — front & rear beams
for z_pos, label in [(STRUCT_Z_OFFSET, "Front"), (-STRUCT_DEPTH, "Rear")]:
    scene.add_geometry(
        make_box([STRUCT_WIDTH, BEAM_H, BEAM_W], mat_steel,
                 tf([0, BEAM_H/2, z_pos])),
        node_name=f"BaseFrame_{label}")

# Side beams
for sign, label in [(-1, "Left"), (1, "Right")]:
    scene.add_geometry(
        make_box([BEAM_W, BEAM_H, STRUCT_DEPTH], mat_steel,
                 tf([sign * (STRUCT_WIDTH/2 - BEAM_W/2), BEAM_H/2, -STRUCT_DEPTH/2])),
        node_name=f"BaseFrame_Side_{label}")

# Cross beams
for x_pos in np.linspace(-STRUCT_WIDTH/3, STRUCT_WIDTH/3, 3):
    scene.add_geometry(
        make_box([BEAM_W, BEAM_H, STRUCT_DEPTH], mat_steel_dark,
                 tf([x_pos, BEAM_H/2, -STRUCT_DEPTH/2])),
        node_name=f"BaseFrame_Cross_{x_pos:.0f}")

# Extend columns from structure to reach mounting grid
COL_Z_EXTEND = 60  # mm — columns reach forward to connect with mounting rails
# Vertical columns — extended forward to meet mounting grid
col_positions = np.linspace(-STRUCT_WIDTH * 0.35, STRUCT_WIDTH * 0.35, 6)
for i, x_pos in enumerate(col_positions):
    scene.add_geometry(
        make_box([COL_SIZE, STRUCT_HEIGHT, COL_SIZE + COL_Z_EXTEND], mat_steel,
                 tf([x_pos, STRUCT_HEIGHT/2, (STRUCT_Z_OFFSET + COL_Z_EXTEND)/2])),
        node_name=f"Column_{i+1}")

# Horizontal beams across columns
for h_frac, label in [(0.5, "Mid"), (0.85, "Upper")]:
    scene.add_geometry(
        make_box([STRUCT_WIDTH * 0.8, BEAM_W, BEAM_H], mat_steel,
                 tf([0, STRUCT_HEIGHT * h_frac, STRUCT_Z_OFFSET/2])),
        node_name=f"MainBeam_{label}")

# Base plates + neoprene — at structure front
for i, x_pos in enumerate(col_positions):
    scene.add_geometry(
        make_box([BASE_PLATE, 10, BASE_PLATE], mat_steel_dark,
                 tf([x_pos, BEAM_H + 5, STRUCT_Z_OFFSET/2])),
        node_name=f"BasePlate_{i+1}")
    scene.add_geometry(
        make_box([BASE_PLATE, 5, BASE_PLATE], mat_neoprene,
                 tf([x_pos, -2.5, STRUCT_Z_OFFSET/2])),
        node_name=f"NeoprenePad_{i+1}")

# Rear bracing grid
for i, x_pos in enumerate(col_positions):
    scene.add_geometry(
        make_box([COL_SIZE, STRUCT_HEIGHT * 0.6, COL_SIZE], mat_steel_dark,
                 tf([x_pos, STRUCT_HEIGHT * 0.5, -STRUCT_DEPTH * 0.7])),
        node_name=f"RearBrace_V_{i+1}")
for h_pos in [STRUCT_HEIGHT * 0.3, STRUCT_HEIGHT * 0.7]:
    scene.add_geometry(
        make_box([STRUCT_WIDTH * 0.7, COL_SIZE, COL_SIZE], mat_steel_dark,
                 tf([0, h_pos, -STRUCT_DEPTH * 0.7])),
        node_name=f"RearBrace_H_{h_pos:.0f}")

print("  Support structure complete")

# ───── 2. CABINET MOUNTING SUB-FRAME ─────
print("[2/5] Building cabinet mounting grid...")

# Vertical mounting rails behind each column
for col in range(NUM_COLS):
    pos, rot = cabinet_pose(col, NUM_ROWS // 2)
    scene.add_geometry(
        make_box([SUB_W, SCREEN_H + 100, SUB_W], mat_subframe,
                 transform_4x4([pos[0], SCREEN_H/2 + 50, pos[2] - CAB_D/2 - 20], rot)),
        node_name=f"MountRail_V_{col}")

# Horizontal mounting rails (straight segments between columns)
for row in range(NUM_ROWS):
    y_pos = row * CAB_H + CAB_H / 2
    for col in range(NUM_COLS - 1):
        p0, r0 = cabinet_pose(col, row)
        p1, r1 = cabinet_pose(col + 1, row)
        mx = (p0[0] + p1[0]) / 2
        mz = (p0[2] + p1[2]) / 2
        seg_len = math.sqrt((p1[0] - p0[0])**2 + (p1[2] - p0[2])**2)
        avg_rot = (r0 + r1) / 2
        scene.add_geometry(
            make_box([seg_len - 5, SUB_W, SUB_W], mat_subframe,
                     tf([mx, y_pos, mz - CAB_D/2 - 20], avg_rot)),
            node_name=f"MountRail_H_R{row}_C{col}")

print("  Mounting grid complete")

# ───── 3. LED CABINETS ─────
print("[3/5] Building LED cabinets (48 total)...")

for row in range(NUM_ROWS):
    for col in range(NUM_COLS):
        pos, rot = cabinet_pose(col, row)
        trf = transform_4x4(pos, rot)
        
        # Cabinet body
        scene.add_geometry(
            make_box([CAB_W, CAB_H, CAB_D], mat_led_body, trf),
            node_name=f"Cabinet_R{row+1}_C{col+1}")
        
        # LED face (thin emissive surface on front)
        face_pos = pos + np.array([0, 0, CAB_D/2 + 0.5])
        scene.add_geometry(
            make_box([CAB_W - 4, CAB_H - 4, 1], mat_led_face,
                     transform_4x4(face_pos, rot)),
            node_name=f"LEDFace_R{row+1}_C{col+1}")

print("  48 cabinets created")

# ───── 4. ACP BORDER ─────
print("[4/5] Building ACP border...")

# ACP sits at the front face of the cabinets
ACP_Z_OFFSET = SCREEN_Z_OFFSET + CAB_D / 2  # 132.5mm

# Top ACP — curved, following screen arc, at cabinet front face
top_acp = arc_segment_boxes(
    SCREEN_W_ARC + 2 * ACP_SIDE, ACP_TOP, 3.0,
    SCREEN_H + ACP_TOP / 2, mat_acp, num_seg=SEGMENTS_CURVE,
    z_offset=ACP_Z_OFFSET)
for i, seg in enumerate(top_acp):
    scene.add_geometry(seg, node_name=f"ACP_Top_Seg{i+1}")
print(f"  Top ACP (curved, {len(top_acp)} segments): OK")

# Bottom ACP — curved, at cabinet front face
bot_acp = arc_segment_boxes(
    SCREEN_W_ARC + 2 * ACP_SIDE, ACP_SIDE, 3.0,
    -ACP_SIDE / 2, mat_acp, num_seg=SEGMENTS_CURVE,
    z_offset=ACP_Z_OFFSET)
for i, seg in enumerate(bot_acp):
    scene.add_geometry(seg, node_name=f"ACP_Bot_Seg{i+1}")
print(f"  Bottom ACP (curved, {len(bot_acp)} segments): OK")

# Side ACP borders — flush with cabinet front face
acp_side_h = SCREEN_H + ACP_TOP + ACP_SIDE
mid_row = NUM_ROWS // 2

for sign, label in [(-1, "Left"), (1, "Right")]:
    col_idx = 0 if sign < 0 else NUM_COLS - 1
    pos, rot = cabinet_pose(col_idx, mid_row)
    col_a = col_angle(col_idx)
    # Edge of cabinet at front face
    edge_x = pos[0] + sign * (CAB_W / 2) * math.cos(deg2rad(col_a))
    edge_z = pos[2] + sign * (CAB_W / 2) * math.sin(deg2rad(col_a))
    
    scene.add_geometry(
        make_box([ACP_SIDE, acp_side_h, 5], mat_acp,
                 tf([edge_x + sign * ACP_SIDE / 2,
                     (SCREEN_H - ACP_SIDE) / 2 + ACP_TOP / 2,
                     ACP_Z_OFFSET])),
        node_name=f"ACP_Border_{label}")
print("  Side ACP borders: OK")

# ───── 5. LOWER HALF COVERING ─────
print("[5/5] Building lower half covering...")

# Opaque sheet covering bottom 2 rows — at cabinet front face plane
cover_y_center = SCREEN_H / 4  # center of bottom half
cover_height = SCREEN_H / 2 - 10  # slightly smaller than 2 rows

opaque_segs = arc_segment_boxes(
    SCREEN_W_ARC - 10, cover_height, 3.0,
    cover_y_center, mat_opaque, num_seg=SEGMENTS_CURVE,
    z_offset=ACP_Z_OFFSET + 2)  # slightly in front of cabinet face
for i, seg in enumerate(opaque_segs):
    scene.add_geometry(seg, node_name=f"Opaque_Seg{i+1}")
print(f"  Opaque sheet (curved, {len(opaque_segs)} segments): OK")

# ACP cover on top of opaque sheet (slightly smaller, in front)
acp_cover_segs = arc_segment_boxes(
    SCREEN_W_ARC - 20, cover_height - 10, 2.0,
    cover_y_center, mat_acp, num_seg=SEGMENTS_CURVE,
    z_offset=ACP_Z_OFFSET + 4)  # slightly in front of opaque
for i, seg in enumerate(acp_cover_segs):
    scene.add_geometry(seg, node_name=f"ACP_Cover_Seg{i+1}")
print(f"  ACP cover on lower half (curved, {len(acp_cover_segs)} segments): OK")

# ═══════════════════════════════════════════════
#  EXPORT
# ═══════════════════════════════════════════════

output_path = os.path.join("D:/Ai_Tools/Open_code/project_folder", "GMR_LED_Wall.glb")

print(f"\n{'=' * 60}")
print(f"Exporting to: {output_path}")
scene.export(output_path)

file_size = os.path.getsize(output_path)
print(f"Export complete!")
print(f"   File: GMR_LED_Wall.glb")
print(f"   Size: {file_size / 1024:.1f} KB")
print(f"   Objects: {len(scene.geometry)}")
print()
print("Import into 3ds Max:")
print("   1. File > Import > GMR_LED_Wall.glb")
print("   2. Objects named: Cabinet_R1_C1, LEDFace_*, ACP_*, etc.")
print("   3. PBR materials preserved (metallic/roughness)")
print()
print("Dimensions Summary:")
print(f"   Screen: {SCREEN_W_ARC:.0f}x{SCREEN_H:.0f}mm (12x4 cabinets)")
print(f"   Curve radius: {RADIUS:.0f}mm  ({CURVE_DEG} deg between columns)")
print(f"   ACP border: {ACP_TOP:.0f}mm top, {ACP_SIDE:.0f}mm sides")
print(f"   Structure: {STRUCT_WIDTH:.0f}x{STRUCT_DEPTH:.0f}x{STRUCT_HEIGHT:.0f}mm")
