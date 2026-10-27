"""Build Blender V3 from V2: XZ probability density, no chart/formula HUD."""

from __future__ import annotations

import bpy
import csv
import json
import math
import os
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
V2_SCRIPT = ROOT / "scripts" / "build_quantum_tunneling_v2.py"
OUTPUT_BLEND = ROOT / "quantum_tunneling_scientific_v3.blend"
SYNC_DIR = ROOT / "sync"
REPORT = ROOT / "docs" / "build_report_v3.json"
BARRIER_HEIGHT_VALUE = 5.6


def remove_object_tree(root):
    if root is None:
        return []
    removed = []
    stack = [root]
    while stack:
        current = stack.pop()
        stack.extend(list(current.children))
        removed.append(current.name)
        bpy.data.objects.remove(current, do_unlink=True)
    return removed


def density_vertices(xs, amplitude, scale=13.5, baseline=0.055, thickness=0.042):
    """Filled rho=|psi|^2 strip in XZ, with constant Y thickness."""
    density = np.asarray(amplitude, dtype=np.float32) ** 2
    vertices = []
    for x_value, rho in zip(xs, density):
        top = baseline + float(rho) * scale
        vertices.extend([
            (float(x_value), -thickness, baseline),
            (float(x_value), thickness, baseline),
            (float(x_value), -thickness, top),
            (float(x_value), thickness, top),
        ])
    return vertices


def density_faces(count):
    faces = []
    for index in range(count - 1):
        a = index * 4
        b = (index + 1) * 4
        faces.extend([
            (a + 2, b + 2, b + 3, a + 3),
            (a, a + 2, b + 2, b),
            (a + 1, b + 1, b + 3, a + 3),
        ])
    return faces


def fill_keyblock(keyblock, vertices):
    for point, coordinate in zip(keyblock.data, vertices):
        point.co = coordinate


def get_fcurves_compat(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbags"):
                for channelbag in strip.channelbags:
                    curves.extend(channelbag.fcurves)
    return curves


def tune_action(id_block, interpolation="LINEAR"):
    animation = getattr(id_block, "animation_data", None)
    if animation and animation.action:
        for curve in get_fcurves_compat(animation.action):
            for point in curve.keyframe_points:
                point.interpolation = interpolation


def smooth_action(id_block, clamped=False):
    animation = getattr(id_block, "animation_data", None)
    if animation and animation.action:
        for curve in get_fcurves_compat(animation.action):
            for point in curve.keyframe_points:
                point.interpolation = "BEZIER"
                handle = "AUTO_CLAMPED" if clamped else "AUTO"
                point.handle_left_type = handle
                point.handle_right_type = handle


def animate_caption(root, start, end):
    root.animation_data_clear()
    keys = []
    if start == 0:
        keys.append((0, 1.0))
    else:
        keys.extend([(start, 0.001), (min(5399, start + 30), 1.0)])
    if end < 5399:
        keys.extend([(max(start + 30, end - 30), 1.0), (end, 0.001)])
    else:
        keys.append((5399, 1.0))
    for frame, factor in keys:
        root.scale = (factor, factor, factor)
        root.keyframe_insert("scale", frame=frame)
    smooth_action(root, clamped=True)


def build_continuous_camera(data):
    """Replace five hard cuts with one C1-smooth camera and target path."""
    removed = []
    for name in [obj.name for obj in bpy.data.objects
                 if obj.name.startswith("HUD_CAM_") and obj.name.endswith("_CaptionRoot")]:
        removed.extend(remove_object_tree(bpy.data.objects.get(name)))
    for obj in list(bpy.data.objects):
        if obj.name.startswith("CAM_0"):
            bpy.data.objects.remove(obj, do_unlink=True)

    camera_collection = bpy.data.collections["50_CAMERAS"]
    annotation_collection = bpy.data.collections["40_ANNOTATION"]
    material = bpy.data.materials["MAT_Text"]
    camera, target = data["create_camera"](
        "CAM_V3_Continuous", 55, (8.5, -16.0, 6.5), (0.3, 0.0, 2.0),
        camera_collection,
    )

    # One uninterrupted camera move.  The former edit points are now broad
    # transition zones; the barrier interaction stays close enough to fill
    # roughly half the vertical frame.
    keys = [
        (0, (8.5, -16.0, 6.5), (0.3, 0.0, 2.0), 55),
        (300, (6.5, -13.0, 5.4), (0.3, 0.0, 2.2), 62),
        (450, (7.5, -15.0, 6.0), (0.3, 0.0, 2.0), 55),
        (510, (-20.0, -10.0, 16.0), (-24.0, 0.0, 0.34), 55),
        # A tiny Y offset preserves the straight-down composition without
        # hitting the tracking constraint's vertical-axis singularity.
        (555, (-31.0, -0.8, 20.0), (-31.0, 0.0, 0.34), 55),
        (660, (-31.0, -0.8, 20.0), (-31.0, 0.0, 0.34), 55),
        (780, (-27.0, -9.0, 15.9), (-27.0, 0.0, 0.34), 55),
        (960, (-22.0, -16.0, 10.5), (-20.0, 0.0, 0.34), 55),
        (1110, (-16.0, -20.0, 8.0), (-16.0, 0.0, 0.34), 55),
        (1260, (-12.5, -22.0, 8.0), (-15.0, 0.0, 0.35), 55),
        (1560, (-9.0, -24.0, 8.2), (-10.0, 0.0, 0.8), 55),
        (1800, (-4.0, -28.0, 8.8), (-4.0, 0.0, 1.4), 55),
        (1980, (0.8, -31.0, 9.5), (0.3, 0.0, 2.8), 55),
        (2400, (0.8, -31.0, 9.5), (0.3, 0.0, 2.8), 55),
        (2700, (1.2, -31.5, 9.6), (0.3, 0.0, 2.8), 55),
        (3060, (2.3, -31.0, 10.0), (0.3, 0.0, 2.8), 55),
        (3420, (-0.8, -31.0, 9.2), (0.3, 0.0, 2.8), 55),
        (3780, (1.8, -31.0, 9.6), (0.3, 0.0, 2.8), 55),
        (4080, (0.8, -31.0, 9.5), (0.3, 0.0, 2.8), 55),
        # Keep the barrier annotation below the upper-left title safe area while
        # the camera arcs from the barrier close-up toward the collapsed particle.
        (4260, (3.0, -28.0, 9.0), (0.3, 0.0, 2.6), 55),
        (4380, (6.2, -12.0, 3.6), (BARRIER_HEIGHT_VALUE, 0.0, 0.28), 55),
        (4500, (6.4, -10.5, 3.2), (BARRIER_HEIGHT_VALUE, 0.0, 0.28), 55),
        (4620, (9.0, -30.0, 11.0), (BARRIER_HEIGHT_VALUE, 0.0, 0.5), 55),
        (4800, (3.0, -50.0, 18.0), (0.0, 0.0, 0.4), 55),
        (4980, (-3.0, -40.0, 14.0), (-3.0, 0.0, 0.65), 55),
        (5160, (-1.2, -27.0, 9.5), (-0.8, 0.0, 0.55), 55),
        (5399, (0.3, -19.0, 7.0), (0.3, 0.0, 0.5), 55),
    ]
    for frame, location, target_location, lens in keys:
        data["key_camera"](camera, target, frame, location, target_location, lens)
    smooth_action(camera, clamped=False)
    smooth_action(target, clamped=False)
    smooth_action(camera.data, clamped=False)

    scene = bpy.context.scene
    scene.timeline_markers.clear()
    marker = scene.timeline_markers.new("V3 / CONTINUOUS CAMERA", frame=0)
    marker.camera = camera
    scene.camera = camera

    captions = [
        ("01  /  BARRIER PARAMETERS", 0, 599),
        ("02  /  PARTICLE TO WAVEPACKET", 600, 1199),
        ("03  /  TUNNELING + PARAMETER STUDY", 1200, 4139),
        ("04  /  COLLAPSE + ENSEMBLE", 4140, 4859),
        ("05  /  MANY TRIALS", 4860, 5399),
    ]
    for index, (body, start, end) in enumerate(captions, 1):
        root = data["create_camera_caption"](
            camera, body, annotation_collection, material, start, end,
            reference_lens=55,
        )
        root.name = f"HUD_V3_Chapter_{index:02d}_CaptionRoot"
        animate_caption(root, start, end)
    return camera, target, keys, removed


def bake_density(obj, snapshots, xs, frame_start=1320, frame_end=2700):
    basis = obj.shape_key_add(name="Basis", from_mix=False)
    fill_keyblock(basis, density_vertices(xs, snapshots[0]["amplitude"]))
    blocks = []
    for snapshot in snapshots[1:]:
        block = obj.shape_key_add(name=f"STEP_{snapshot['step']:04d}", from_mix=False)
        fill_keyblock(block, density_vertices(xs, snapshot["amplitude"]))
        blocks.append((snapshot["step"], block))

    def mapped(step):
        return round(frame_start + step / 899.0 * (frame_end - frame_start))

    for index, (step, block) in enumerate(blocks):
        previous_step = snapshots[index]["step"]
        block.value = 0.0
        block.keyframe_insert("value", frame=mapped(previous_step))
        block.value = 1.0
        block.keyframe_insert("value", frame=mapped(step))
        if index + 1 < len(blocks):
            block.value = 0.0
            block.keyframe_insert("value", frame=mapped(blocks[index + 1][0]))
        else:
            block.value = 1.0
            block.keyframe_insert("value", frame=5399)
    tune_action(obj.data.shape_keys, "LINEAR")


def history_value(history, frame):
    if frame <= 1320:
        step = 0.0
    elif frame >= 2700:
        step = len(history) - 1.0
    else:
        step = (frame - 1320) / (2700 - 1320) * (len(history) - 1)
    i0 = int(math.floor(step))
    i1 = min(i0 + 1, len(history) - 1)
    t = step - i0
    return float((1.0 - t) * history[i0] + t * history[i1])


def export_sync(data):
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    physics = data["physics"]
    lookup = data["lookup"]
    timeline = {
        "schema": "quantum-tunneling-master-timeline-v3",
        "fps": 60,
        "resolution": [1920, 1080],
        "frame_range": [0, 5399],
        "layout": {
            "blender_normalized": [0.0, 0.0, 0.6666667, 1.0],
            "manim_normalized": [0.6666667, 0.0, 1.0, 1.0],
            "full_screen_exceptions": [
                {"frames": [4140, 5399], "reason": "collapse and many-trial visual emphasis"}
            ],
        },
        "segments": [
            {"name": "barrier", "frames": [0, 599]},
            {"name": "particle_to_wavepacket", "frames": [600, 1199]},
            {"name": "probability_overlay_in", "frames": [1200, 1319], "manim_local_start": 0},
            {"name": "tunneling_live", "frames": [1320, 2700], "manim_local_start": 120},
            {"name": "formula", "frames": [2700, 2879], "manim_local_start": 1500},
            {"name": "width_study", "frames": [2880, 3419], "manim_local_start": 1680},
            {"name": "height_study", "frames": [3420, 3959], "manim_local_start": 2220},
            {"name": "comparison_hold", "frames": [3960, 4079], "manim_local_start": 2760},
            {"name": "overlay_out", "frames": [4080, 4139], "manim_local_start": 2880},
            {"name": "collapse_ensemble", "frames": [4140, 4859]},
            {"name": "many_trials", "frames": [4860, 5399]},
        ],
        "source_of_truth": "probability_frames_v3.csv",
        "blender_frame_to_manim_frame": "manim_frame = blender_frame - 1200 while overlay is active",
        "color": {"base": "#55D7FF", "width": "#FF9D45", "height": "#FF4DB8"},
    }
    (SYNC_DIR / "master_timeline_v3.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    csv_path = SYNC_DIR / "probability_frames_v3.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = ["blender_frame", "time_seconds", "manim_frame", "segment",
                  "p_before", "p_after", "p_inside", "log10_before", "log10_after",
                  "width_factor", "height_factor", "comparison_group",
                  "comparison_before", "comparison_after"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for frame in range(1200, 4140, 3):
            if frame <= 2700:
                segment = "tunneling_live" if frame >= 1320 else "probability_overlay_in"
                before = history_value(physics["history_before"], frame)
                after = history_value(physics["history_after"], frame)
                inside = history_value(physics["history_inside"], frame)
                wf = hf = 1.0
                group = "base"
                comp_after = after
            elif frame < 2880:
                segment, wf, hf, group = "formula", 1.0, 1.0, "base"
                before, after, inside = 1.0 - physics["transmission"], physics["transmission"], 0.0
                comp_after = after
            elif frame <= 3419:
                segment, hf, group = "width_study", 1.0, "width"
                wf = data["width_factor_at"](frame) if frame <= 3360 else 1.5 - 0.5 * (frame - 3360) / 60.0
                comp_after = float(np.interp(wf, lookup["width_factors"], lookup["width_t"]))
                before, after, inside = 1.0 - physics["transmission"], physics["transmission"], 0.0
            elif frame <= 3959:
                segment, wf, group = "height_study", 1.0, "height"
                hf = data["height_factor_at"](frame) if frame <= 3900 else 1.3 - 0.3 * (frame - 3900) / 60.0
                comp_after = float(np.interp(hf, lookup["height_factors"], lookup["height_t"]))
                before, after, inside = 1.0 - physics["transmission"], physics["transmission"], 0.0
            else:
                segment, wf, hf, group = "comparison_hold", 1.0, 1.0, "base"
                before, after, inside = 1.0 - physics["transmission"], physics["transmission"], 0.0
                comp_after = after
            writer.writerow({
                "blender_frame": frame, "time_seconds": f"{frame / 60.0:.6f}",
                "manim_frame": frame - 1200, "segment": segment,
                "p_before": f"{before:.10f}", "p_after": f"{after:.10f}",
                "p_inside": f"{inside:.10f}",
                "log10_before": f"{math.log10(max(before, 1e-9)):.10f}",
                "log10_after": f"{math.log10(max(after, 1e-9)):.10f}",
                "width_factor": f"{wf:.6f}", "height_factor": f"{hf:.6f}",
                "comparison_group": group,
                "comparison_before": f"{1.0 - comp_after:.10f}",
                "comparison_after": f"{comp_after:.10f}",
            })


def main():
    data = runpy.run_path(str(V2_SCRIPT), run_name="v2_library")
    # Rebuild the known-good V2 deterministically, then branch the open scene
    # into V3.  V2 remains available as its own saved review version.
    data["main"]()
    physics = data["simulate_packet"]()
    lookup = data["build_parameter_lookup"]()
    data.update({"physics": physics, "lookup": lookup})

    removed = []
    removed += remove_object_tree(bpy.data.objects.get("HUD_Probability_Chart_Root"))
    removed += remove_object_tree(bpy.data.objects.get("HUD_Formula_Root"))

    old = bpy.data.objects.get("GEO_Wave_Amplitude_Envelope_XY")
    if old is None:
        raise RuntimeError("V2 amplitude envelope not found")
    collection = next(iter(old.users_collection))
    material = old.data.materials[0]
    opacity_socket = None
    if material.use_nodes:
        for node in material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                opacity_socket = next((s for s in node.inputs if s.name == "Alpha"), None)
                break
    bpy.data.objects.remove(old, do_unlink=True)

    xs = physics["x"]
    first = physics["snapshots"][0]
    mesh = bpy.data.meshes.new("MESH_Probability_Density_XZ")
    mesh.from_pydata(density_vertices(xs, first["amplitude"]), [], density_faces(len(xs)))
    mesh.update()
    density = bpy.data.objects.new("GEO_Probability_Density_XZ", mesh)
    collection.objects.link(density)
    density.data.materials.append(material)
    density["plane"] = "XZ"
    density["scientific_mapping"] = "rho(x,t)=|psi(x,t)|^2=Re(psi)^2+Im(psi)^2"
    density["vertical_quantity"] = "probability_density"
    bake_density(density, physics["snapshots"], xs)

    if opacity_socket:
        # The material retains the V2 fade animation for morph/collapse.
        pass
    for name in ("GEO_Wave_Real_XY", "GEO_Wave_Imag_XY"):
        obj = bpy.data.objects[name]
        obj["plane"] = "XY"
        obj["role"] = "complex_wavefunction_component"

    mapping = bpy.data.objects.get("TXT_Mapping")
    if mapping and hasattr(mapping.data, "body"):
        mapping.data.body = "PROBABILITY DENSITY / XZ    REAL + IMAG / XY"

    collapsed = bpy.data.objects.get("GEO_Collapsed_Transmitted_Particle")
    if collapsed is None:
        raise RuntimeError("Collapsed particle not found")
    collapsed.location.x = BARRIER_HEIGHT_VALUE
    collapsed["placement_rule"] = "x equals barrier height value"

    continuous_camera, continuous_target, camera_keys, removed_captions = \
        build_continuous_camera(data)

    scene = bpy.context.scene
    scene["project_title"] = "Quantum Tunneling - Hybrid Compositing V3"
    scene["review_status"] = "Awaiting V3 user approval before final render"
    scene["final_render_executed"] = 0
    scene["overlay_hud"] = "External Manim; Blender chart/formula removed"
    scene["sync_manifest"] = "sync/master_timeline_v3.json"
    scene["camera_design"] = "single continuous camera; no hard cuts"
    scene["collapse_particle_x"] = BARRIER_HEIGHT_VALUE
    scene.render.filepath = str(ROOT / "renders" / "final_v3" / "frame_")
    (ROOT / "renders" / "final_v3").mkdir(parents=True, exist_ok=True)
    export_sync(data)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    report = {
        "blend": str(OUTPUT_BLEND),
        "source": "quantum_tunneling_scientific_v2.blend rebuilt through V2 script",
        "removed_chart_formula_objects": len(removed),
        "probability_density": {"object": density.name, "plane": "XZ", "quantity": "|psi|^2"},
        "real_imag_plane": "XY",
        "camera": {
            "object": continuous_camera.name,
            "hard_cuts": 0,
            "key_count": len(camera_keys),
            "close_barrier_frames": [2100, 4080],
            "target_barrier_vertical_fill": 0.5
        },
        "collapse_particle_x": BARRIER_HEIGHT_VALUE,
        "sync": [str(SYNC_DIR / "master_timeline_v3.json"), str(SYNC_DIR / "probability_frames_v3.csv")],
        "final_render_executed": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
