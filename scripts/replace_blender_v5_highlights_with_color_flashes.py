"""Replace V5 highlight overlays with object-local inverse-colour flashes.

The barrier and its labels are intentionally untouched.  Left/right spatial
cues are rendered by flashing only the wave-packet geometry on that side of
the barrier.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
V5 = ROOT / "quantum_tunneling_scientific_v5_voice_aligned.blend"
REPORT_JSON = ROOT / "sync" / "blender_v5_voice_alignment.json"
REPORT_MD = ROOT / "sync" / "BlenderV5_语音对齐动作表.md"
COLLECTION_NAME = "60_SYNC_HIGHLIGHTS"


def get_fcurves(action):
    if action is None:
        return []
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in getattr(strip, "channelbags", []):
                curves.extend(channelbag.fcurves)
    return curves


def principled(material_name: str):
    material = bpy.data.materials[material_name]
    return next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")


def remove_socket_keys_at(socket, frames) -> None:
    node_tree = socket.id_data
    animation = node_tree.animation_data
    action = animation.action if animation else None
    path = socket.path_from_id("default_value")
    frame_set = {round(float(frame), 3) for frame in frames}
    for curve in get_fcurves(action):
        if curve.data_path != path:
            continue
        for point in reversed(list(curve.keyframe_points)):
            if round(float(point.co.x), 3) in frame_set:
                curve.keyframe_points.remove(point)
        curve.update()


def key_socket(socket, frame: int, value, interpolation: str = "LINEAR") -> None:
    socket.default_value = value
    socket.keyframe_insert(data_path="default_value", frame=frame)
    action = socket.id_data.animation_data.action
    path = socket.path_from_id("default_value")
    for curve in get_fcurves(action):
        if curve.data_path != path:
            continue
        for point in curve.keyframe_points:
            if abs(point.co.x - frame) < 0.01:
                point.interpolation = interpolation
                if interpolation == "BEZIER":
                    point.handle_left_type = "AUTO_CLAMPED"
                    point.handle_right_type = "AUTO_CLAMPED"


def inverse_rgb(color):
    return tuple(1.0 - float(channel) for channel in color[:3]) + (1.0,)


def replace_component_highlight(
    material_name: str,
    start: int,
    peak_start: int,
    peak_end: int,
    restore: int,
    end: int,
    old_highlight_frames,
):
    node = principled(material_name)
    base_socket = node.inputs["Base Color"]
    emission_socket = node.inputs["Emission Color"]
    strength_socket = node.inputs["Emission Strength"]

    # Remove the former long-duration saturation/+2 emission highlight.
    remove_socket_keys_at(emission_socket, old_highlight_frames)
    remove_socket_keys_at(strength_socket, old_highlight_frames)

    base_color = tuple(base_socket.default_value)
    emission_color = tuple(emission_socket.default_value)
    inverted_base = inverse_rgb(base_color)
    inverted_emission = inverse_rgb(emission_color)

    for frame, base, emission in (
        (start - 1, base_color, emission_color),
        (start, base_color, emission_color),
        (peak_start, inverted_base, inverted_emission),
        (peak_end, inverted_base, inverted_emission),
        (restore, base_color, emission_color),
        (end, base_color, emission_color),
        (end + 1, base_color, emission_color),
    ):
        key_socket(base_socket, frame, base, "LINEAR")
        key_socket(emission_socket, frame, emission, "LINEAR")

    bpy.data.materials[material_name]["highlight_style"] = "inverse-colour flash then restore"
    return {
        "material": material_name,
        "frames": [start, peak_start, peak_end, restore, end],
        "base_emission": [round(v, 4) for v in emission_color[:3]],
        "inverse_emission": [round(v, 4) for v in inverted_emission[:3]],
    }


def delete_old_region_overlays():
    removed_objects = []
    for name in ("GEO_V5_LeftSpace_Highlight", "GEO_V5_RightSpace_Highlight"):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            removed_objects.append(name)
            bpy.data.objects.remove(obj, do_unlink=True)
    removed_materials = []
    for name in ("MAT_V5_LeftSpace_Highlight", "MAT_V5_RightSpace_Highlight"):
        material = bpy.data.materials.get(name)
        if material is not None and material.users == 0:
            removed_materials.append(name)
            bpy.data.materials.remove(material)
    return removed_objects, removed_materials


def build_spatial_flash_material(name: str, side: str, color, start: int, end: int):
    old = bpy.data.materials.get(name)
    if old is not None:
        bpy.data.materials.remove(old, do_unlink=True)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (620, 0)
    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (400, 0)
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    transparent.location = (170, -110)
    emission = nodes.new("ShaderNodeEmission")
    emission.location = (170, 90)
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = 4.6

    geometry = nodes.new("ShaderNodeNewGeometry")
    geometry.location = (-620, 40)
    separate = nodes.new("ShaderNodeSeparateXYZ")
    separate.location = (-450, 40)
    compare = nodes.new("ShaderNodeMath")
    compare.location = (-270, 40)
    compare.operation = "LESS_THAN" if side == "left" else "GREATER_THAN"
    compare.inputs[1].default_value = -0.32 if side == "left" else 0.32
    flash = nodes.new("ShaderNodeValue")
    flash.name = "Flash_Factor"
    flash.label = f"{side.title()} wave packet inverse-colour flash"
    flash.location = (-270, -120)
    flash.outputs[0].default_value = 0.0
    multiply = nodes.new("ShaderNodeMath")
    multiply.location = (-40, 0)
    multiply.operation = "MULTIPLY"

    links.new(geometry.outputs["Position"], separate.inputs["Vector"])
    links.new(separate.outputs["X"], compare.inputs[0])
    links.new(compare.outputs[0], multiply.inputs[0])
    links.new(flash.outputs[0], multiply.inputs[1])
    links.new(multiply.outputs[0], mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])

    # One crisp flash: normal -> strict inverse -> normal.
    for frame, value in (
        (1, 0.0),
        (start - 1, 0.0),
        (start, 0.0),
        (start + 6, 1.0),
        (start + 12, 1.0),
        (start + 19, 0.0),
        (end, 0.0),
        (end + 1, 0.0),
        (3578, 0.0),
    ):
        key_socket(flash.outputs[0], frame, value, "LINEAR")

    material["highlight_style"] = f"{side} wave packet only; barrier excluded"
    material["barrier_boundary_x"] = -0.32 if side == "left" else 0.32
    return material


def duplicate_wave_for_flash(source_name: str, duplicate_name: str, material, collection):
    old = bpy.data.objects.get(duplicate_name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    source = bpy.data.objects[source_name]
    duplicate = source.copy()
    duplicate.data = source.data
    duplicate.name = duplicate_name
    collection.objects.link(duplicate)
    if not duplicate.material_slots:
        raise RuntimeError(f"Wave source has no material slot: {source_name}")
    duplicate.material_slots[0].link = "OBJECT"
    duplicate.material_slots[0].material = material
    duplicate.delta_location.y -= 0.018
    if hasattr(duplicate, "visible_shadow"):
        duplicate.visible_shadow = False
    duplicate["purpose"] = "inverse-colour wave-only flash; not a spatial overlay"
    return duplicate


def build_wave_side_flashes():
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(collection)

    # Colours are strict RGB complements of the formula-phase wave colours.
    specs = {
        "left": {"start": 1256, "end": 1316},
        "right": {"start": 1306, "end": 1376},
    }
    created = []
    for side, timing in specs.items():
        helix_material = build_spatial_flash_material(
            f"MAT_V5_{side.title()}_Helix_Flash",
            side,
            (1.0, 0.58, 0.0),
            timing["start"],
            timing["end"],
        )
        envelope_material = build_spatial_flash_material(
            f"MAT_V5_{side.title()}_Envelope_Flash",
            side,
            (1.0, 0.22, 0.0),
            timing["start"],
            timing["end"],
        )
        created.append(duplicate_wave_for_flash(
            "GEO_V4_Complex_Wavefunction_Helix",
            f"GEO_V5_{side.title()}_Wave_Flash_Helix",
            helix_material,
            collection,
        ).name)
        created.append(duplicate_wave_for_flash(
            "GEO_Probability_Density_XZ",
            f"GEO_V5_{side.title()}_Wave_Flash_Envelope",
            envelope_material,
            collection,
        ).name)
    return created


def rename_markers():
    for marker in bpy.context.scene.timeline_markers:
        marker.name = marker.name.replace("LEFT_REGION", "LEFT_WAVEPACKET_FLASH")
        marker.name = marker.name.replace("RIGHT_REGION", "RIGHT_WAVEPACKET_FLASH")


def verify(component_results, created_objects):
    scene = bpy.context.scene
    barrier = bpy.data.objects["GEO_Barrier_Plain"]
    barrier_materials = [slot.material.name for slot in barrier.material_slots if slot.material]
    if any("Flash" in name or "Highlight" in name for name in barrier_materials):
        raise RuntimeError("Barrier was incorrectly assigned a flash material")
    if bpy.data.objects.get("GEO_V5_LeftSpace_Highlight") or bpy.data.objects.get("GEO_V5_RightSpace_Highlight"):
        raise RuntimeError("Old spatial overlay still exists")

    samples = []
    for frame, expected_side in ((1255, None), (1262, "left"), (1275, None), (1305, None), (1312, "right"), (1325, None)):
        scene.frame_set(frame)
        entry = {"frame": frame, "expected_inverse_side": expected_side}
        for side in ("Left", "Right"):
            material = bpy.data.materials[f"MAT_V5_{side}_Helix_Flash"]
            flash = material.node_tree.nodes["Flash_Factor"].outputs[0].default_value
            entry[side.lower() + "_factor"] = round(float(flash), 4)
        samples.append(entry)
    return {
        "component_flashes": component_results,
        "wave_flash_objects": created_objects,
        "barrier_materials_unchanged": barrier_materials,
        "spatial_flash_samples": samples,
    }


def update_reports(result):
    payload = json.loads(REPORT_JSON.read_text(encoding="utf-8")) if REPORT_JSON.exists() else {}
    payload["inverse_colour_highlight_correction"] = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "final_render_executed": False,
        "old_region_overlays_removed": True,
        **result,
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    note = (
        "\n## 反色闪烁高亮修正\n\n"
        "- 实部与虚部改为短促的 `原色 → RGB反色 → 原色` 闪烁，不再持续增亮。\n"
        "- 已删除势垒左右空间的矩形色块；左右提示只作用于对应侧的螺旋波函数和概率包络。\n"
        "- 势垒、`V0`、`W` 及指示箭头不参与左右空间闪烁。\n"
        "- 仅保存 Blender 工程，未执行最终动画渲染。\n"
    )
    text = REPORT_MD.read_text(encoding="utf-8") if REPORT_MD.exists() else "# Blender V5 语音对齐动作表\n"
    if "## 反色闪烁高亮修正" in text:
        text = text.split("## 反色闪烁高亮修正", 1)[0].rstrip() + "\n"
    REPORT_MD.write_text(text + note, encoding="utf-8")


def main():
    if Path(bpy.data.filepath).resolve() != V5.resolve():
        raise RuntimeError(f"Open V5 before running this script: {V5}")

    component_results = [
        replace_component_highlight(
            "MAT_Wave_Real_Red",
            start=656, peak_start=661, peak_end=665, restore=672, end=711,
            old_highlight_frames=(655, 656, 711, 712),
        ),
        replace_component_highlight(
            "MAT_Wave_Imag_Blue",
            start=676, peak_start=681, peak_end=685, restore=692, end=711,
            old_highlight_frames=(675, 676, 711, 712),
        ),
    ]
    removed_objects, removed_materials = delete_old_region_overlays()
    created_objects = build_wave_side_flashes()
    rename_markers()
    result = verify(component_results, created_objects)
    result["removed_region_objects"] = removed_objects
    result["removed_region_materials"] = removed_materials

    scene = bpy.context.scene
    scene["highlight_style"] = "inverse colour flashes; wave-only spatial cues"
    scene["final_render_executed"] = 0
    update_reports(result)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(V5), check_existing=False)
    print("V5_HIGHLIGHTS_REPLACED=" + json.dumps(result, ensure_ascii=False))


main()
