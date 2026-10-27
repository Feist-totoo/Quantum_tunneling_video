"""Render a low-cost V4 keyframe review set without touching final settings."""

from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = ROOT / "renders" / "qa_v4" / "frames"
FRAMES = [
    0, 300, 450, 509, 510, 600, 720, 780, 900,
    960, 1080, 1120, 1190, 1250, 1320, 1440, 1560,
    1620, 1740, 1880, 2040, 4380, 4500, 4860, 5399,
]


scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.use_file_extension = True
scene.render.use_overwrite = True
if hasattr(scene, "eevee"):
    scene.eevee.taa_render_samples = 8
    scene.eevee.volumetric_samples = 8

intro = bpy.data.objects["CAM_V4_Barrier_Intro"]
follow = bpy.data.objects["CAM_V4_Particle_Wave_Follow"]
OUTPUT.mkdir(parents=True, exist_ok=True)

for frame in FRAMES:
    scene.frame_set(frame)
    scene.camera = intro if frame < 510 else follow
    scene.render.filepath = str(OUTPUT / f"frame_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"REVIEW_FRAME={frame}")

print(f"REVIEW_OUTPUT={OUTPUT}")
