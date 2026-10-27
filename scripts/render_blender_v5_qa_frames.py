import bpy
import os
from pathlib import Path


scene = bpy.context.scene
qa_dir = Path(os.environ.get("QT_V5_QA_DIR", r"C:\Users\liuzh\Desktop\1\renders\qa_v5"))
qa_dir.mkdir(parents=True, exist_ok=True)

default_frames = [
    1, 120, 235,
    346, 380, 405, 470, 505,
    506, 565, 624, 656, 676, 711,
    712, 750, 780, 820, 886,
    887, 950, 1021, 1135,
    1145, 1256, 1306, 1376, 1456,
    2142, 2401, 2709,
    2716, 2745, 2805, 2848,
    2851, 2878, 2928, 2961,
    3006, 3084, 3160, 3239, 3350, 3440, 3500, 3578,
]
frame_override = os.environ.get("QT_V5_QA_FRAMES", "").strip()
frames = [int(value) for value in frame_override.split(",") if value.strip()] if frame_override else default_frames

scene.render.resolution_x = 650
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

if hasattr(scene, "eevee"):
    scene.eevee.taa_render_samples = min(scene.eevee.taa_render_samples, 16)

for frame in frames:
    scene.frame_set(frame)
    scene.render.filepath = str(qa_dir / f"v5_f{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"QA_RENDERED={frame}")

print(f"QA_COMPLETE={qa_dir}")
