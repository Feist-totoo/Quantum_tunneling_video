"""Create and validate a self-contained SheepIt upload copy.

Run with Blender 5.2 in background mode while opening the final V3 blend.
The generated blend contains no video proxies and requires no custom scripts.
"""

from pathlib import Path
import json

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
PACKAGE_DIR = ROOT / "cloud_render" / "sheepit_v3_1080p60"
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_BLEND = PACKAGE_DIR / "quantum_tunneling_v3_sheepit_blender_5_2.blend"
MANIFEST = PACKAGE_DIR / "SHEEPIT_MANIFEST.json"

scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = 5399
scene.frame_step = 1
scene.render.fps = 60
scene.render.fps_base = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 15
scene.render.film_transparent = False
scene.render.filepath = "//frames/frame_"
scene.render.use_file_extension = True
scene.render.use_overwrite = True
scene.render.use_placeholder = False
scene.render.use_persistent_data = True
scene.render.use_sequencer = False
scene.eevee.taa_render_samples = 16
scene.eevee.volumetric_samples = 16

if scene.camera is None:
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
    if not cameras:
        raise RuntimeError("No render camera")
    scene.camera = cameras[0]

external_before_pack = [
    bpy.path.abspath(image.filepath)
    for image in bpy.data.images
    if image.source == "FILE" and image.filepath
]
linked_libraries = [
    bpy.path.abspath(library.filepath)
    for library in bpy.data.libraries
    if library.filepath
]

if external_before_pack:
    bpy.ops.file.pack_all()

bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

handlers = {
    name: len(getattr(bpy.app.handlers, name))
    for name in ("frame_change_pre", "frame_change_post", "render_pre", "render_post")
}
drivers = sum(
    len(obj.animation_data.drivers)
    for obj in bpy.data.objects
    if obj.animation_data and obj.animation_data.drivers
)
vse_count = len(scene.sequence_editor.strips) if scene.sequence_editor and hasattr(scene.sequence_editor, "strips") else 0

manifest = {
    "blenderVersion": bpy.app.version_string,
    "blendFile": OUTPUT_BLEND.name,
    "engine": scene.render.engine,
    "resolution": [1920, 1080],
    "fps": 60,
    "frameStart": 0,
    "frameEnd": 5399,
    "frameCount": 5400,
    "outputFormat": "PNG RGB 8-bit",
    "eeveeRenderSamples": scene.eevee.taa_render_samples,
    "eeveeVolumetricSamples": scene.eevee.volumetric_samples,
    "camera": scene.camera.name,
    "externalFilesBeforePacking": external_before_pack,
    "linkedLibraries": linked_libraries,
    "handlers": handlers,
    "drivers": drivers,
    "vseStrips": vse_count,
    "requiresCustomPython": False,
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"SHEEPIT_BLEND={OUTPUT_BLEND}")
print(f"SHEEPIT_MANIFEST={MANIFEST}")
print("SHEEPIT_READY=" + json.dumps(manifest, ensure_ascii=False))
