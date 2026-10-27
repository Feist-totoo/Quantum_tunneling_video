"""Render three unsaved camera-angle tests at frame 1560."""

from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = ROOT / "renders" / "qa_v4" / "camera_tests"
OUTPUT.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.use_overwrite = True
if hasattr(scene, "eevee"):
    scene.eevee.taa_render_samples = 8

camera = bpy.data.objects["CAM_V4_Particle_Wave_Follow"]
target = bpy.data.objects["CAM_V4_Particle_Wave_Follow_Target"]
scene.camera = camera
scene.frame_set(1560)
camera.animation_data_clear()
target.animation_data_clear()
camera.data.animation_data_clear()

tests = [
    ("x_minus_8", (-18.0, -24.0, 8.2), (-10.0, 0.0, 0.8)),
    ("x_minus_12", (-22.0, -22.0, 8.2), (-10.0, 0.0, 0.8)),
    ("x_plus_6", (-4.0, -24.0, 8.2), (-10.0, 0.0, 0.8)),
]
for name, location, target_location in tests:
    camera.location = location
    target.location = target_location
    scene.render.filepath = str(OUTPUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"CAMERA_TEST={name}")
