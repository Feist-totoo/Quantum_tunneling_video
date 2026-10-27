"""Render representative adjacent frame pairs from the SheepIt upload copy."""

from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUT = ROOT / "cloud_render" / "sheepit_v3_1080p60" / "validation_frames"
OUT.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.use_file_extension = True
scene.render.use_overwrite = True
scene.render.use_placeholder = False
scene.render.use_persistent_data = True
scene.eevee.taa_render_samples = 8
scene.eevee.volumetric_samples = 8

frames = [205, 206, 600, 601, 1521, 1522, 2040, 2041, 2834, 2835, 3864, 3865, 5398, 5399]
for frame in frames:
    scene.frame_set(frame)
    scene.render.filepath = str(OUT / f"frame_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"VALIDATION_FRAME={frame}")

print(f"VALIDATION_OUTPUT={OUT}")
