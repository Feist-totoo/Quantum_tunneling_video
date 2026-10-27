"""Replace temporary overlay duplicates with direct wave-material colour masks."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
V5 = ROOT / "quantum_tunneling_scientific_v5_voice_aligned.blend"
REPORT_JSON = ROOT / "sync" / "blender_v5_voice_alignment.json"


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


def key_socket(socket, frame, value, interpolation="BEZIER"):
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


def capture_socket_animation(socket):
    node_tree = socket.id_data
    animation = node_tree.animation_data
    action = animation.action if animation else None
    path = socket.path_from_id("default_value")
    curves = [curve for curve in get_fcurves(action) if curve.data_path == path]
    frames = sorted({round(float(point.co.x), 4) for curve in curves for point in curve.keyframe_points})
    interpolation = {}
    for curve in curves:
        for point in curve.keyframe_points:
            interpolation.setdefault(round(float(point.co.x), 4), point.interpolation)
    scene = bpy.context.scene
    current = scene.frame_current
    samples = []
    for frame in frames:
        whole = int(frame)
        scene.frame_set(whole, subframe=float(frame) - whole)
        samples.append((frame, tuple(socket.default_value), interpolation.get(frame, "BEZIER")))
    scene.frame_set(current)
    return samples


def remove_socket_animation(socket):
    node_tree = socket.id_data
    animation = node_tree.animation_data
    action = animation.action if animation else None
    path = socket.path_from_id("default_value")
    for curve in get_fcurves(action):
        if curve.data_path != path:
            continue
        for point in reversed(list(curve.keyframe_points)):
            curve.keyframe_points.remove(point)
        curve.update()


def remove_overlay_duplicates():
    removed = []
    names = (
        "GEO_V5_Left_Wave_Flash_Helix",
        "GEO_V5_Left_Wave_Flash_Envelope",
        "GEO_V5_Right_Wave_Flash_Helix",
        "GEO_V5_Right_Wave_Flash_Envelope",
    )
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            removed.append(name)
            bpy.data.objects.remove(obj, do_unlink=True)
    for material in list(bpy.data.materials):
        if material.name.startswith("MAT_V5_Left_") or material.name.startswith("MAT_V5_Right_"):
            if material.users == 0:
                bpy.data.materials.remove(material)
    return removed


def build_direct_flash(material_name: str):
    material = bpy.data.materials[material_name]
    material.use_nodes = True
    tree = material.node_tree
    nodes = tree.nodes
    links = tree.links
    principled = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    emission_socket = principled.inputs["Emission Color"]
    base_socket = principled.inputs["Base Color"]

    emission_animation = capture_socket_animation(emission_socket)
    current_emission = tuple(emission_socket.default_value)
    current_base = tuple(base_socket.default_value)
    remove_socket_animation(emission_socket)

    for node in list(nodes):
        if node.name.startswith("QA_SpatialFlash_"):
            nodes.remove(node)

    emission_source = nodes.new("ShaderNodeRGB")
    emission_source.name = "QA_SpatialFlash_EmissionSource"
    emission_source.label = "Original animated wave emission"
    emission_source.location = (-720, 240)
    emission_source.outputs[0].default_value = current_emission
    for frame, value, interpolation in emission_animation:
        key_socket(emission_source.outputs[0], frame, value, interpolation)

    emission_inverse = nodes.new("ShaderNodeVectorMath")
    emission_inverse.name = "QA_SpatialFlash_EmissionInverse"
    emission_inverse.operation = "SUBTRACT"
    emission_inverse.location = (-400, 300)
    emission_inverse.inputs[0].default_value = (1.0, 1.0, 1.0)
    links.new(emission_source.outputs[0], emission_inverse.inputs[1])

    base_source = nodes.new("ShaderNodeRGB")
    base_source.name = "QA_SpatialFlash_BaseSource"
    base_source.location = (-720, 40)
    base_source.outputs[0].default_value = current_base
    base_inverse = nodes.new("ShaderNodeVectorMath")
    base_inverse.name = "QA_SpatialFlash_BaseInverse"
    base_inverse.operation = "SUBTRACT"
    base_inverse.location = (-400, 80)
    base_inverse.inputs[0].default_value = (1.0, 1.0, 1.0)
    links.new(base_source.outputs[0], base_inverse.inputs[1])

    geometry = nodes.new("ShaderNodeNewGeometry")
    geometry.name = "QA_SpatialFlash_Geometry"
    geometry.location = (-940, -220)
    separate = nodes.new("ShaderNodeSeparateXYZ")
    separate.name = "QA_SpatialFlash_SeparateXYZ"
    separate.location = (-760, -220)
    links.new(geometry.outputs["Position"], separate.inputs[0])

    left_compare = nodes.new("ShaderNodeMath")
    left_compare.name = "QA_SpatialFlash_LeftMask"
    left_compare.operation = "LESS_THAN"
    left_compare.location = (-570, -190)
    left_compare.inputs[1].default_value = -0.32
    links.new(separate.outputs["X"], left_compare.inputs[0])
    right_compare = nodes.new("ShaderNodeMath")
    right_compare.name = "QA_SpatialFlash_RightMask"
    right_compare.operation = "GREATER_THAN"
    right_compare.location = (-570, -330)
    right_compare.inputs[1].default_value = 0.32
    links.new(separate.outputs["X"], right_compare.inputs[0])

    left_flash = nodes.new("ShaderNodeValue")
    left_flash.name = "QA_SpatialFlash_LeftFactor"
    left_flash.location = (-760, -440)
    right_flash = nodes.new("ShaderNodeValue")
    right_flash.name = "QA_SpatialFlash_RightFactor"
    right_flash.location = (-760, -520)
    for socket, start, end in (
        (left_flash.outputs[0], 1256, 1316),
        (right_flash.outputs[0], 1306, 1376),
    ):
        for frame, value in (
            (1, 0.0), (start - 1, 0.0), (start, 0.0),
            (start + 6, 1.0), (start + 12, 1.0),
            (start + 19, 0.0), (end, 0.0), (end + 1, 0.0), (3578, 0.0),
        ):
            key_socket(socket, frame, value, "LINEAR")

    left_product = nodes.new("ShaderNodeMath")
    left_product.name = "QA_SpatialFlash_LeftProduct"
    left_product.operation = "MULTIPLY"
    left_product.location = (-350, -220)
    links.new(left_compare.outputs[0], left_product.inputs[0])
    links.new(left_flash.outputs[0], left_product.inputs[1])
    right_product = nodes.new("ShaderNodeMath")
    right_product.name = "QA_SpatialFlash_RightProduct"
    right_product.operation = "MULTIPLY"
    right_product.location = (-350, -340)
    links.new(right_compare.outputs[0], right_product.inputs[0])
    links.new(right_flash.outputs[0], right_product.inputs[1])
    combined = nodes.new("ShaderNodeMath")
    combined.name = "QA_SpatialFlash_CombinedFactor"
    combined.operation = "MAXIMUM"
    combined.location = (-120, -280)
    links.new(left_product.outputs[0], combined.inputs[0])
    links.new(right_product.outputs[0], combined.inputs[1])

    emission_mix = nodes.new("ShaderNodeMixRGB")
    emission_mix.name = "QA_SpatialFlash_EmissionMix"
    emission_mix.blend_type = "MIX"
    emission_mix.location = (0, 240)
    links.new(combined.outputs[0], emission_mix.inputs[0])
    links.new(emission_source.outputs[0], emission_mix.inputs[1])
    links.new(emission_inverse.outputs[0], emission_mix.inputs[2])
    links.new(emission_mix.outputs[0], emission_socket)

    base_mix = nodes.new("ShaderNodeMixRGB")
    base_mix.name = "QA_SpatialFlash_BaseMix"
    base_mix.blend_type = "MIX"
    base_mix.location = (0, 60)
    links.new(combined.outputs[0], base_mix.inputs[0])
    links.new(base_source.outputs[0], base_mix.inputs[1])
    links.new(base_inverse.outputs[0], base_mix.inputs[2])
    links.new(base_mix.outputs[0], base_socket)

    material["spatial_highlight_implementation"] = "direct inverse-colour material mask; no duplicate overlay"
    return {
        "material": material_name,
        "emission_keyframes_migrated": len(emission_animation),
        "left_boundary": -0.32,
        "right_boundary": 0.32,
    }


def verify(results):
    scene = bpy.context.scene
    barrier = bpy.data.objects["GEO_Barrier_Plain"]
    barrier_materials = [slot.material.name for slot in barrier.material_slots if slot.material]
    if barrier_materials != ["MAT_Barrier_Plain_70pct_Transparent"]:
        raise RuntimeError(f"Barrier material changed: {barrier_materials}")
    if any(bpy.data.objects.get(name) for name in (
        "GEO_V5_Left_Wave_Flash_Helix", "GEO_V5_Left_Wave_Flash_Envelope",
        "GEO_V5_Right_Wave_Flash_Helix", "GEO_V5_Right_Wave_Flash_Envelope",
    )):
        raise RuntimeError("Temporary overlay duplicate still exists")

    samples = []
    for frame in (1255, 1262, 1275, 1305, 1312, 1325):
        scene.frame_set(frame)
        entry = {"frame": frame}
        for material_name in ("MAT_V4_Complex_Helix", "MAT_Wave_Amplitude_Envelope"):
            nodes = bpy.data.materials[material_name].node_tree.nodes
            entry[material_name] = {
                "left": round(float(nodes["QA_SpatialFlash_LeftFactor"].outputs[0].default_value), 4),
                "right": round(float(nodes["QA_SpatialFlash_RightFactor"].outputs[0].default_value), 4),
            }
        samples.append(entry)
    return {"materials": results, "samples": samples, "barrier_materials": barrier_materials}


def main():
    if Path(bpy.data.filepath).resolve() != V5.resolve():
        raise RuntimeError(f"Open V5 before running: {V5}")
    removed = remove_overlay_duplicates()
    results = [
        build_direct_flash("MAT_V4_Complex_Helix"),
        build_direct_flash("MAT_Wave_Amplitude_Envelope"),
    ]
    verification = verify(results)
    verification["temporary_overlay_objects_removed"] = removed
    payload = json.loads(REPORT_JSON.read_text(encoding="utf-8")) if REPORT_JSON.exists() else {}
    correction = payload.setdefault("inverse_colour_highlight_correction", {})
    correction["spatial_implementation"] = "direct wave-material mask; no transparent duplicate geometry"
    correction["spatial_verification"] = verification
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    bpy.context.scene["highlight_style"] = "direct inverse-colour wave masks; barrier excluded"
    bpy.context.scene["final_render_executed"] = 0
    bpy.context.scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(V5), check_existing=False)
    print("V5_SPATIAL_FLASH_DIRECT=" + json.dumps(verification, ensure_ascii=False))


main()
