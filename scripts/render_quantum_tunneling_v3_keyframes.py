"""Render low-resolution hybrid V3 review frames only."""

import bpy
import os

ROOT = r"C:\Users\liuzh\Desktop\1"
OUT = os.environ.get(
    "V3_REVIEW_OUT",
    os.path.join(ROOT, "renders", "review_v3"),
)
FRAMES = [
    180, 599,
    600, 720, 900, 1080, 1199,
    1200, 1320, 1600, 2000, 2400, 2700,
    2880, 3000, 3240, 3360,
    3420, 3540, 3780, 3900, 4080,
    4140, 4380, 4500, 4620, 4800,
    4860, 5000, 5140, 5280, 5399,
]
frame_override = os.environ.get("V3_REVIEW_FRAMES", "").strip()
if frame_override:
    FRAMES = [int(value) for value in frame_override.split(",") if value.strip()]

scene = bpy.context.scene
os.makedirs(OUT, exist_ok=True)
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.use_persistent_data = True

for frame in FRAMES:
    scene.frame_set(frame)
    scene.render.filepath = os.path.join(OUT, f"v3_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[v3 review] rendered {frame}")

print(f"[v3 review] complete: {len(FRAMES)} frames")
