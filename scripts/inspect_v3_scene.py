"""Emit a compact structural report for the current V3 Blender scene."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = ROOT / "docs" / "v3_scene_structure.json"


def fcurves(action):
    if action is None:
        return []
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    result = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in getattr(strip, "channelbags", []):
                result.extend(channelbag.fcurves)
    return result


def action_report(id_block):
    animation = getattr(id_block, "animation_data", None)
    action = animation.action if animation else None
    rows = []
    for curve in fcurves(action):
        frames = sorted({round(point.co.x, 4) for point in curve.keyframe_points})
        rows.append({
            "path": curve.data_path,
            "index": curve.array_index,
            "frames": frames,
        })
    return {"name": action.name if action else None, "fcurves": rows}


def object_report(obj):
    result = {
        "name": obj.name,
        "type": obj.type,
        "collection": [collection.name for collection in obj.users_collection],
        "location": [round(value, 5) for value in obj.location],
        "rotation_euler": [round(value, 5) for value in obj.rotation_euler],
        "scale": [round(value, 5) for value in obj.scale],
        "hide_render": obj.hide_render,
        "parent": obj.parent.name if obj.parent else None,
        "custom": {key: obj[key] for key in obj.keys() if key != "_RNA_UI"},
        "action": action_report(obj),
    }
    if obj.type == "CAMERA":
        result["camera_data"] = {
            "lens": obj.data.lens,
            "clip_start": obj.data.clip_start,
            "action": action_report(obj.data),
        }
    if obj.data and hasattr(obj.data, "materials"):
        result["materials"] = [material.name if material else None for material in obj.data.materials]
    shape_keys = getattr(obj.data, "shape_keys", None) if obj.data else None
    if shape_keys:
        result["shape_keys"] = {
            "count": len(shape_keys.key_blocks),
            "names": [block.name for block in shape_keys.key_blocks],
            "action": action_report(shape_keys),
        }
    if obj.type == "CURVE":
        result["curve"] = {
            "dimensions": obj.data.dimensions,
            "bevel_depth": obj.data.bevel_depth,
            "splines": [
                {
                    "type": spline.type,
                    "points": len(spline.points),
                    "bezier_points": len(spline.bezier_points),
                }
                for spline in obj.data.splines
            ],
        }
    if obj.type == "MESH":
        result["mesh"] = {
            "vertices": len(obj.data.vertices),
            "edges": len(obj.data.edges),
            "polygons": len(obj.data.polygons),
        }
    return result


def sampled_state(obj, frames):
    scene = bpy.context.scene
    rows = []
    for frame in frames:
        scene.frame_set(frame)
        rows.append({
            "frame": frame,
            "location": [round(value, 5) for value in obj.matrix_world.translation],
            "scale": [round(value, 5) for value in obj.scale],
            "hide_render": obj.hide_render,
            "hide_viewport": obj.hide_viewport,
        })
    return rows


def material_report(material):
    result = {
        "name": material.name,
        "blend_method": getattr(material, "surface_render_method", None),
        "diffuse_color": [round(value, 5) for value in material.diffuse_color],
        "action": action_report(material),
        "nodes": [],
    }
    if material.use_nodes:
        for node in material.node_tree.nodes:
            sockets = []
            for socket in node.inputs:
                animation = action_report(material.node_tree)
                if socket.name in {"Base Color", "Emission Color", "Emission Strength", "Alpha"}:
                    value = socket.default_value
                    try:
                        value = [round(item, 5) for item in value]
                    except TypeError:
                        value = round(float(value), 5)
                    sockets.append({"name": socket.name, "value": value})
            if sockets:
                result["nodes"].append({"name": node.name, "type": node.type, "inputs": sockets})
        result["node_tree_action"] = action_report(material.node_tree)
    return result


def mesh_samples(obj):
    scene = bpy.context.scene
    rows = []
    for frame in (600, 900, 1080, 1199, 1200, 1320, 1740, 2040, 2700):
        scene.frame_set(frame)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        vertices = [[round(value, 5) for value in vertex.co] for vertex in list(mesh.vertices)[:16]]
        evaluated.to_mesh_clear()
        rows.append({"frame": frame, "vertices": vertices})
    return rows


scene = bpy.context.scene
keywords = (
    "CAM_", "Target", "Particle", "Wave", "Probability", "Barrier", "V0", "Width",
    "Arrow", "Mapping", "Real", "Imag", "Envelope", "Collapsed",
)
selected = [obj for obj in bpy.data.objects if any(word.lower() in obj.name.lower() for word in keywords)]
sample_frames = [0, 300, 450, 510, 555, 599, 600, 660, 780, 900, 960, 1110, 1199, 1200, 1320, 1740, 2040, 2700, 2880, 3420, 4140, 4380, 4860, 5399]

report = {
    "blend": bpy.data.filepath,
    "scene_camera": scene.camera.name if scene.camera else None,
    "frame_range": [scene.frame_start, scene.frame_end],
    "markers": [
        {"name": marker.name, "frame": marker.frame, "camera": marker.camera.name if marker.camera else None}
        for marker in scene.timeline_markers
    ],
    "objects": [object_report(obj) for obj in sorted(selected, key=lambda item: item.name)],
    "materials": [
        material_report(material)
        for material in bpy.data.materials
        if any(word.lower() in material.name.lower() for word in ("wave", "particle", "barrier"))
    ],
    "mesh_samples": {
        name: mesh_samples(bpy.data.objects[name])
        for name in ("GEO_Wave_Real_XY", "GEO_Wave_Imag_XY", "GEO_Probability_Density_XZ")
    },
    "samples": {
        obj.name: sampled_state(obj, sample_frames)
        for obj in selected
        if any(word.lower() in obj.name.lower() for word in ("particle", "wave", "probability", "camera", "cam_"))
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"WROTE {OUTPUT}")
