from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = PROJECT_ROOT / "renders" / "qa_v3_fullrender" / "frames"
FRAMES = [0, 600, 1600, 1739, 1780, 1880, 1985, 2040, 2880, 3420, 4140, 4860, 5399]

OUTPUT.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_percentage = 25
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.use_overwrite = True

for frame in FRAMES:
    scene.frame_set(frame)
    scene.render.filepath = str(OUTPUT / f"frame_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED_FRAME={frame}")
