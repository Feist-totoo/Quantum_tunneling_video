"""Retarget Blender V4 to the approved narration timeline without rendering.

Run with Blender 5.2 in background mode while opening the V4 .blend.  The
script retimes every Action, reorders the height/width studies, rebuilds the
camera markers, adds the narration-driven highlight cues, and saves a new V5
file.  The retained V4 source is never overwritten.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT_BLEND = ROOT / "quantum_tunneling_scientific_v5_voice_aligned.blend"
REPORT_JSON = ROOT / "sync" / "blender_v5_voice_alignment.json"
REPORT_MD = ROOT / "sync" / "BlenderV5_语音对齐动作表.md"
GLOBAL_OFFSET = 5544  # global frame = local Blender frame + 5544


# Inclusive old and new ranges.  A03 is intentionally collapsed at the end of
# A02, matching the cue-sheet note "A03切掉".  Height (A19-A21) deliberately
# precedes width (A16-A18).
SEGMENTS = [
    ("A01", 0, 89, 1, 235, "势垒从背景中建立"),
    ("A02", 90, 299, 236, 345, "势垒尺寸与形态展示"),
    ("A03", 300, 509, 345, 345, "剪掉：势垒构图回落"),
    ("A04", 510, 599, 346, 380, "切到粒子前方15度镜头"),
    ("A05", 600, 719, 381, 405, "镜头随粒子向+X运动"),
    ("A06", 720, 899, 406, 470, "镜头抬升并开始转向俯视"),
    ("A07", 900, 1049, 471, 505, "完成正上方构图"),
    ("A08", 1050, 1120, 506, 624, "粒子分解为实部与虚部"),
    ("A09", 1121, 1179, 625, 711, "实部、虚部独立展示"),
    ("A10", 1180, 1319, 712, 780, "平面分量拟合为三维复波函数"),
    ("A11", 1320, 1559, 781, 886, "镜头沿Y轴移向波包展示位"),
    ("A12", 1560, 1660, 887, 1021, "概率密度波包浮现"),
    ("A13", 1661, 1739, 1022, 1135, "完整波函数系统向势垒传播"),
    ("A14", 1740, 2039, 1136, 1446, "公式演示与Blender高亮"),
    ("A15", 2040, 2879, 1447, 2709, "透射与反射概率动态图表同步"),
    ("A19", 3420, 3540, 2710, 2745, "势垒高度降低到0.8V0"),
    ("A20", 3541, 3779, 2746, 2805, "势垒高度升高到1.3V0"),
    ("A21", 3780, 3959, 2806, 2848, "势垒高度恢复到V0"),
    ("A16", 2880, 3000, 2849, 2878, "势垒宽度减小到1/2W"),
    ("A17", 3001, 3239, 2879, 2928, "势垒宽度扩展到3/2W"),
    ("A18", 3240, 3419, 2929, 2961, "势垒宽度恢复到W"),
    ("A22", 3960, 4139, 2962, 3005, "图表与叠加层退出"),
    ("A23", 4140, 4379, 3006, 3084, "镜头拉近透射后的波包"),
    ("A24", 4380, 4499, 3085, 3239, "波函数坍缩回单个粒子"),
    ("A25", 4500, 4859, 3240, 3440, "拉远到反射/透射系综"),
    ("A26", 4860, 5399, 3441, 3578, "多粒子隧穿与反射试验"),
]


GLOBAL_CUES = {
    "BLENDER_START": 5545,
    "REAL_HIGHLIGHT_IN": 6200,
    "IMAG_HIGHLIGHT_IN": 6220,
    "PLANAR_HIGHLIGHT_OUT": 6255,
    "FORMULA_BC_IN": 6689,
    "LEFT_REGION_IN": 6800,
    "RIGHT_REGION_IN": 6850,
    "LEFT_REGION_OUT": 6860,
    "FORMULA_DF_IN": 6908,
    "RIGHT_REGION_OUT": 6920,
    "CHART_IN": 7000,
    "COEFFICIENTS_IN": 7686,
    "TRANSMISSION_FORMULA_IN": 7847,
    "APPROX_FORMULA_IN": 7945,
    "V0_HIGHLIGHT_IN": 8260,
    "V0_HIGHLIGHT_OUT": 8390,
    "W_HIGHLIGHT_IN": 8395,
    "W_HIGHLIGHT_OUT": 8500,
    "CHART_OUT": 8515,
    "BLENDER_END": 9122,
}


def local_frame(global_frame: int) -> int:
    return global_frame - GLOBAL_OFFSET


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


def segment_for_old_frame(frame: float):
    if frame <= SEGMENTS[0][1]:
        return SEGMENTS[0]
    for segment in SEGMENTS:
        if segment[1] <= frame <= segment[2]:
            return segment
    return SEGMENTS[-1]


def map_frame(frame: float) -> float:
    name, old_start, old_end, new_start, new_end, _ = segment_for_old_frame(frame)
    if name == "A03":
        return float(new_start)
    if old_end == old_start:
        return float(new_start)
    ratio = (frame - old_start) / (old_end - old_start)
    ratio = min(1.0, max(0.0, ratio))
    return new_start + ratio * (new_end - new_start)


def retime_action(action) -> tuple[int, int]:
    moved = 0
    removed = 0
    for curve in get_fcurves(action):
        points = list(curve.keyframe_points)
        # The cut A03 retains its first boundary value only.  Later A03 camera
        # pull-back/hold keys are removed rather than stacked at one frame.
        for point in reversed(points):
            old_frame = float(point.co.x)
            if 300.0 < old_frame <= 509.0:
                curve.keyframe_points.remove(point)
                removed += 1
                continue
            new_frame = map_frame(old_frame)
            delta = new_frame - old_frame
            point.co.x = new_frame
            point.handle_left.x += delta
            point.handle_right.x += delta
            if point.interpolation == "BEZIER":
                point.handle_left_type = "AUTO_CLAMPED"
                point.handle_right_type = "AUTO_CLAMPED"
            moved += 1
        curve.update()
    return moved, removed


def retime_nla() -> int:
    count = 0
    for datablocks in (bpy.data.objects, bpy.data.materials, bpy.data.scenes):
        for block in datablocks:
            animation = getattr(block, "animation_data", None)
            if animation is None:
                continue
            for track in animation.nla_tracks:
                for strip in track.strips:
                    strip.frame_start = map_frame(strip.frame_start)
                    strip.frame_end = map_frame(strip.frame_end)
                    count += 1
    return count


def principled(material_name: str):
    material = bpy.data.materials[material_name]
    return next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")


def remove_socket_keys(socket, frame_start: int, frame_end: int) -> None:
    node_tree = socket.id_data
    animation = node_tree.animation_data
    action = animation.action if animation else None
    path = socket.path_from_id("default_value")
    for curve in get_fcurves(action):
        if curve.data_path != path:
            continue
        for point in reversed(list(curve.keyframe_points)):
            if frame_start <= point.co.x <= frame_end:
                curve.keyframe_points.remove(point)
        curve.update()


def key_socket(socket, frame: int, value, interpolation: str = "BEZIER") -> None:
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


def add_material_highlight(material_name, start: int, end: int, base_color, highlight_color, base_strength: float):
    node = principled(material_name)
    color_socket = node.inputs["Emission Color"]
    strength_socket = node.inputs["Emission Strength"]
    remove_socket_keys(color_socket, start - 1, end + 1)
    remove_socket_keys(strength_socket, start - 1, end + 1)
    for frame, color, strength in (
        (start - 1, base_color, base_strength),
        (start, highlight_color, base_strength + 2.0),
        (end, highlight_color, base_strength + 2.0),
        (end + 1, base_color, base_strength),
    ):
        key_socket(color_socket, frame, (*color, 1.0), "BEZIER")
        key_socket(strength_socket, frame, strength, "BEZIER")


def create_region_highlight(name: str, x_min: float, x_max: float, start: int, end: int):
    collection = bpy.data.collections.get("60_SYNC_HIGHLIGHTS")
    if collection is None:
        collection = bpy.data.collections.new("60_SYNC_HIGHLIGHTS")
        bpy.context.scene.collection.children.link(collection)

    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    # Vertical XZ plane, just behind the wave from the main negative-Y camera.
    vertices = [
        (x_min, 0.16, 0.05), (x_max, 0.16, 0.05),
        (x_max, 0.16, 5.75), (x_min, 0.16, 5.75),
    ]
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["purpose"] = "narration-synchronized spatial highlight; not a scientific surface"

    material = bpy.data.materials.new(name.replace("GEO_", "MAT_"))
    material.use_nodes = True
    material.diffuse_color = (0.05, 0.55, 0.90, 0.0)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    node = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = (0.02, 0.22, 0.42, 1.0)
    node.inputs["Emission Color"].default_value = (0.05, 0.72, 1.0, 1.0)
    node.inputs["Emission Strength"].default_value = 2.0
    node.inputs["Roughness"].default_value = 0.5
    mesh.materials.append(material)

    alpha = node.inputs["Alpha"]
    for frame, value in ((1, 0.0), (start - 1, 0.0), (start, 0.11), (end, 0.11), (end + 1, 0.0), (3578, 0.0)):
        key_socket(alpha, frame, value, "BEZIER")
    return obj


def rebuild_markers() -> None:
    scene = bpy.context.scene
    scene.timeline_markers.clear()
    intro = bpy.data.objects.get("CAM_V4_Barrier_Intro")
    follow = bpy.data.objects.get("CAM_V4_Particle_Wave_Follow")
    marker = scene.timeline_markers.new("CAM / BARRIER INTRO", frame=1)
    marker.camera = intro
    marker = scene.timeline_markers.new("CAM / CONTINUOUS PARTICLE + WAVE", frame=346)
    marker.camera = follow
    scene.camera = intro

    for name, _, _, new_start, new_end, description in SEGMENTS:
        scene.timeline_markers.new(f"{name} / {description} / end {new_end}", frame=new_start)
    for name, global_value in GLOBAL_CUES.items():
        local_value = local_frame(global_value)
        if 1 <= local_value <= 3578:
            scene.timeline_markers.new(f"SYNC {name} / GLOBAL F{global_value:05d}", frame=local_value)


def write_reports(moved: int, removed: int, nla_count: int) -> None:
    ordered = []
    for name, old_start, old_end, new_start, new_end, description in SEGMENTS:
        ordered.append(
            {
                "action": name,
                "description": description,
                "old_frames": [old_start, old_end],
                "new_local_frames": [new_start, new_end],
                "new_global_frames": [new_start + GLOBAL_OFFSET, new_end + GLOBAL_OFFSET],
            }
        )
    payload = {
        "schema": "quantum-tunnelling-blender-v5-voice-alignment",
        "fps": 60,
        "resolution": [1300, 1080],
        "blender_local_range": [1, 3578],
        "global_range": [5545, 9122],
        "global_offset": GLOBAL_OFFSET,
        "height_before_width": True,
        "a03_removed": True,
        "final_render_executed": False,
        "retime_stats": {"moved_keyframes": moved, "removed_a03_keyframes": removed, "nla_strips": nla_count},
        "actions": ordered,
        "sync_cues": {
            name: {"global_frame": frame, "local_frame": local_frame(frame)}
            for name, frame in GLOBAL_CUES.items()
        },
        "interpretation": {
            "left_right_space_typo": "The duplicated cue-sheet labels were interpreted sequentially as left-space then right-space highlights.",
            "highlight_rule": "Emission saturation is tightened and emission strength is raised by 2.0, then restored.",
        },
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = [
        "# Blender V5 语音对齐动作表",
        "",
        "- 工程：`quantum_tunneling_scientific_v5_voice_aligned.blend`",
        "- 分辨率：1300×1080；帧率：60 fps",
        "- Blender 本地帧：F00001–F03578",
        "- 正片全局帧：F05545–F09122（全局帧 = Blender帧 + 5544）",
        "- A03 已切掉；A19–A21 高度变化排在 A16–A18 厚度变化之前。",
        "- 只完成工程与关键帧重定时，未启动渲染。",
        "",
        "|动作|新 Blender 帧|正片全局帧|内容|",
        "|---|---:|---:|---|",
    ]
    for item in ordered:
        rows.append(
            f"|{item['action']}|{item['new_local_frames'][0]}–{item['new_local_frames'][1]}|"
            f"{item['new_global_frames'][0]}–{item['new_global_frames'][1]}|{item['description']}|"
        )
    rows += [
        "",
        "## 高亮解释",
        "",
        "文档中重复写成两组“势垒左侧空间”的 b1/b2 标注，按出现顺序解释为左侧空间与右侧空间；两者均以低透明度青色区域光提示，并按标注帧恢复。",
    ]
    REPORT_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    if not bpy.data.filepath:
        raise RuntimeError("Open the retained V4 .blend before running this script")
    if Path(bpy.data.filepath).resolve() == OUTPUT_BLEND.resolve():
        raise RuntimeError("Refusing to retime the V5 output in place")

    moved = 0
    removed = 0
    for action in bpy.data.actions:
        action_moved, action_removed = retime_action(action)
        moved += action_moved
        removed += action_removed
    nla_count = retime_nla()

    # Real/imaginary component callouts.
    add_material_highlight(
        "MAT_Wave_Real_Red",
        local_frame(6200), local_frame(6255),
        (1.0, 0.12, 0.15), (1.0, 0.0, 0.03), 3.2,
    )
    add_material_highlight(
        "MAT_Wave_Imag_Blue",
        local_frame(6220), local_frame(6255),
        (0.15, 0.45, 1.0), (0.02, 0.34, 1.0), 3.2,
    )

    # Formula phase: emphasize the complex wave and probability envelope by
    # exactly +2 emission strength, then restore before the chart phase.
    add_material_highlight(
        "MAT_V4_Complex_Helix",
        local_frame(6689), local_frame(6990),
        (0.02, 0.28, 1.0), (0.0, 0.42, 1.0), 1.8,
    )
    add_material_highlight(
        "MAT_Wave_Amplitude_Envelope",
        local_frame(6689), local_frame(6990),
        (0.05, 0.55, 0.90), (0.0, 0.78, 1.0), 0.65,
    )

    create_region_highlight(
        "GEO_V5_LeftSpace_Highlight", -16.0, -0.45,
        local_frame(6800), local_frame(6860),
    )
    create_region_highlight(
        "GEO_V5_RightSpace_Highlight", 0.45, 16.0,
        local_frame(6850), local_frame(6920),
    )

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 3578
    scene.frame_preview_start = 1
    scene.frame_preview_end = 3578
    scene.render.fps = 60
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1300
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(ROOT / "renders" / "final_v5_voice_aligned" / "frame_")
    scene["project_title"] = "Quantum Tunneling - Scientific V5 Voice Aligned"
    scene["blender_global_frame_offset"] = GLOBAL_OFFSET
    scene["blender_global_start_frame"] = 5545
    scene["blender_global_end_frame"] = 9122
    scene["height_study_before_width_study"] = 1
    scene["a03_removed"] = 1
    scene["right_overlay_width_px"] = 620
    scene["final_render_executed"] = 0
    scene["review_status"] = "Voice-aligned keyframes complete; final Blender render intentionally pending"
    rebuild_markers()
    scene.frame_set(1)
    write_reports(moved, removed, nla_count)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    print(json.dumps({
        "output": str(OUTPUT_BLEND),
        "frame_range": [1, 3578],
        "resolution": [1300, 1080],
        "moved_keyframes": moved,
        "removed_a03_keyframes": removed,
        "rendered": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
