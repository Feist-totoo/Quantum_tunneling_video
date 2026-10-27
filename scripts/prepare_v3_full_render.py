from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT_BLEND = PROJECT_ROOT / "quantum_tunneling_scientific_v3_fullrender.blend"
FRAME_DIR = PROJECT_ROOT / "renders" / "final_v3_full" / "frames"


def principled(material_name: str):
    material = bpy.data.materials.get(material_name)
    if material is None or not material.use_nodes:
        raise RuntimeError(f"Missing node material: {material_name}")
    node = next((item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED"), None)
    if node is None:
        raise RuntimeError(f"Missing Principled BSDF: {material_name}")
    return node


def keyframe_socket(socket, values):
    for frame, value in values:
        socket.default_value = value
        socket.keyframe_insert(data_path="default_value", frame=frame)


def set_emission(material_name: str, color_keys, strength_keys):
    node = principled(material_name)
    keyframe_socket(node.inputs["Emission Color"], color_keys)
    keyframe_socket(node.inputs["Emission Strength"], strength_keys)


for name in [
    "TXT_CAM_V3_Continuous_Caption",
    "TXT_CAM_V3_Continuous_Caption.001",
    "TXT_CAM_V3_Continuous_Caption.002",
    "TXT_CAM_V3_Continuous_Caption.003",
    "TXT_CAM_V3_Continuous_Caption.004",
    "TXT_Mapping",
]:
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.hide_render = True
        obj.hide_viewport = True


# 1740–2039 对应右侧公式的三步语义高亮：势垒差、波函数衰减、厚度指数。
barrier_blue = (0.02, 0.38, 0.72, 1.0)
barrier_orange = (1.0, 0.24, 0.035, 1.0)
barrier_purple = (0.58, 0.18, 0.78, 1.0)
set_emission(
    "MAT_Barrier_Plain_70pct_Transparent",
    [
        (1739, barrier_blue),
        (1780, barrier_orange),
        (1840, barrier_blue),
        (1935, barrier_blue),
        (1985, barrier_purple),
        (2020, barrier_blue),
        (2040, barrier_blue),
    ],
    [(1739, 0.0), (1780, 3.2), (1840, 0.25), (1935, 0.25), (1985, 3.5), (2020, 0.55), (2040, 0.0)],
)

set_emission(
    "MAT_Wave_Amplitude_Envelope",
    [(1810, (0.05, 0.55, 0.9, 1.0)), (1880, (0.2, 0.95, 1.0, 1.0)), (1970, (0.05, 0.55, 0.9, 1.0))],
    [(1810, 0.0), (1880, 4.2), (1945, 1.1), (1970, 0.0)],
)
set_emission(
    "MAT_Wave_Real_Red",
    [(1810, (0.45, 0.01, 0.02, 1.0)), (1880, (1.0, 0.05, 0.07, 1.0)), (1970, (0.45, 0.01, 0.02, 1.0))],
    [(1810, 0.0), (1880, 2.6), (1945, 0.7), (1970, 0.0)],
)
set_emission(
    "MAT_Wave_Imag_Blue",
    [(1810, (0.0, 0.12, 0.5, 1.0)), (1880, (0.15, 0.45, 1.0, 1.0)), (1970, (0.0, 0.12, 0.5, 1.0))],
    [(1810, 0.0), (1880, 2.6), (1945, 0.7), (1970, 0.0)],
)


scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = 5399
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 16
scene.eevee.volumetric_samples = 16
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 60
scene.render.fps_base = 1.0
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.filepath = str(FRAME_DIR / "frame_")
scene.render.use_file_extension = True
scene.render.use_placeholder = True
scene.render.use_overwrite = False
scene.render.film_transparent = False

FRAME_DIR.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
print(f"READY_BLEND={OUTPUT_BLEND}")
print(f"FRAME_OUTPUT={FRAME_DIR}")
