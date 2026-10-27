"""Remove orphaned datablocks left by the retired spatial highlight overlays."""

from pathlib import Path

import bpy


V5 = Path(r"C:\Users\liuzh\Desktop\1\quantum_tunneling_scientific_v5_voice_aligned.blend")

if Path(bpy.data.filepath).resolve() != V5.resolve():
    raise RuntimeError(f"Open V5 before running: {V5}")

removed_meshes = []
for mesh in list(bpy.data.meshes):
    if mesh.users == 0 and (
        mesh.name.startswith("GEO_V5_LeftSpace_Highlight")
        or mesh.name.startswith("GEO_V5_RightSpace_Highlight")
    ):
        removed_meshes.append(mesh.name)
        bpy.data.meshes.remove(mesh)

removed_materials = []
retired_prefixes = (
    "MAT_V5_LeftSpace_Highlight",
    "MAT_V5_RightSpace_Highlight",
    "MAT_V5_Left_Helix_Flash",
    "MAT_V5_Left_Envelope_Flash",
    "MAT_V5_Right_Helix_Flash",
    "MAT_V5_Right_Envelope_Flash",
)
for material in list(bpy.data.materials):
    if material.users == 0 and material.name.startswith(retired_prefixes):
        removed_materials.append(material.name)
        bpy.data.materials.remove(material)

bpy.context.scene["final_render_executed"] = 0
bpy.ops.wm.save_as_mainfile(filepath=str(V5), check_existing=False)
print("RETIRED_HIGHLIGHT_DATA_REMOVED", removed_meshes, removed_materials)
