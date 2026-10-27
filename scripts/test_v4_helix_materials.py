"""Render unsaved color-management tests for the V4 helix."""

from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = ROOT / "renders" / "qa_v4" / "material_tests"
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
scene.frame_set(1560)
scene.camera = bpy.data.objects["CAM_V4_Particle_Wave_Follow"]

material = bpy.data.materials["MAT_V4_Complex_Helix"]
node = next(item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED")
material.node_tree.animation_data_clear()
node.inputs["Alpha"].default_value = 1.0

tests = [
    ("current", (0.02, 0.28, 1.0, 1.0), 1.8),
    ("saturated", (0.0, 0.08, 1.0, 1.0), 0.8),
    ("balanced", (0.0, 0.16, 0.8, 1.0), 1.1),
]
for name, color, strength in tests:
    node.inputs["Emission Color"].default_value = color
    node.inputs["Emission Strength"].default_value = strength
    scene.render.filepath = str(OUTPUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"MATERIAL_TEST={name}")
