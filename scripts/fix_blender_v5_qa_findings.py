"""Fix the visual QA findings in the already retimed Blender V5 project.

This script edits V5 in place, without rendering.  V4 remains the retained
source.  It locks the scientific barrier endpoints and prevents the height and
width annotation arrows from leaking into one another's time ranges.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
V5 = ROOT / "quantum_tunneling_scientific_v5_voice_aligned.blend"
REPORT_JSON = ROOT / "sync" / "blender_v5_voice_alignment.json"
REPORT_MD = ROOT / "sync" / "BlenderV5_语音对齐动作表.md"


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


def remove_keys(obj, data_path: str, first: int, last: int) -> None:
    animation = obj.animation_data
    action = animation.action if animation else None
    for curve in get_fcurves(action):
        if curve.data_path != data_path:
            continue
        for point in reversed(list(curve.keyframe_points)):
            if first <= point.co.x <= last:
                curve.keyframe_points.remove(point)
        curve.update()


def set_bezier_auto_clamped(obj, data_path: str) -> None:
    animation = obj.animation_data
    action = animation.action if animation else None
    for curve in get_fcurves(action):
        if curve.data_path != data_path:
            continue
        for point in curve.keyframe_points:
            point.interpolation = "BEZIER"
            point.handle_left_type = "AUTO_CLAMPED"
            point.handle_right_type = "AUTO_CLAMPED"
        curve.update()


def key_scale(obj, frame: int, xyz) -> None:
    obj.scale = xyz
    obj.keyframe_insert(data_path="scale", frame=frame, group="QA timing")


def rebuild_barrier_parameter_motion() -> None:
    barrier = bpy.data.objects["GEO_Barrier_Plain"]
    remove_keys(barrier, "scale", 2709, 2962)

    # Height study: 1.0 -> 0.8 -> 1.3 -> 1.0.
    # Width study follows: 1.0 -> 0.5 -> 1.5 -> 1.0.
    keys = (
        (2709, (1.0, 1.0, 1.0)),
        (2710, (1.0, 1.0, 1.0)),
        (2745, (1.0, 1.0, 0.8)),
        (2746, (1.0, 1.0, 0.8)),
        (2805, (1.0, 1.0, 1.3)),
        (2806, (1.0, 1.0, 1.3)),
        (2848, (1.0, 1.0, 1.0)),
        (2849, (1.0, 1.0, 1.0)),
        (2878, (0.5, 1.0, 1.0)),
        (2879, (0.5, 1.0, 1.0)),
        (2928, (1.5, 1.0, 1.0)),
        (2929, (1.5, 1.0, 1.0)),
        (2961, (1.0, 1.0, 1.0)),
        (2962, (1.0, 1.0, 1.0)),
    )
    for frame, value in keys:
        key_scale(barrier, frame, value)
    set_bezier_auto_clamped(barrier, "scale")
    barrier["parameter_animation_order"] = "height 0.8-1.3-1.0, then width 0.5-1.5-1.0"


def rebuild_arrow_gates() -> None:
    height_roots = (
        bpy.data.objects["GEO_V3_Height_Arrow_Bottom"],
        bpy.data.objects["GEO_V3_Height_Arrow_Top"],
    )
    width_roots = (
        bpy.data.objects["GEO_V3_Width_Arrow_Left"],
        bpy.data.objects["GEO_V3_Width_Arrow_Right"],
    )

    for obj in height_roots:
        remove_keys(obj, "scale", 1, 3578)
        for frame, value in (
            (1, 0.001), (2709, 0.001), (2716, 1.0),
            (2846, 1.0), (2848, 0.001), (3578, 0.001),
        ):
            key_scale(obj, frame, (value, value, value))
        set_bezier_auto_clamped(obj, "scale")
        obj["visibility_gate"] = "height study only: F02710-F02848"

    for obj in width_roots:
        remove_keys(obj, "scale", 1, 3578)
        for frame, value in (
            (1, 0.001), (2848, 0.001), (2851, 1.0),
            (2956, 1.0), (2961, 0.001), (3578, 0.001),
        ):
            key_scale(obj, frame, (value, value, value))
        set_bezier_auto_clamped(obj, "scale")
        obj["visibility_gate"] = "width study only: F02849-F02961"


def enforce_particle_centering() -> None:
    """Keep the opening follow shot aimed exactly at the moving particle."""
    target = bpy.data.objects["CAM_V4_Particle_Wave_Follow_Target"]
    particle = bpy.data.objects["GEO_Incident_Particle"]
    old = target.constraints.get("QA_Copy_Incident_Particle")
    if old is not None:
        target.constraints.remove(old)
    constraint = target.constraints.new("COPY_LOCATION")
    constraint.name = "QA_Copy_Incident_Particle"
    constraint.target = particle
    constraint.target_space = "WORLD"
    constraint.owner_space = "WORLD"
    for frame, influence in (
        (1, 0.0), (345, 0.0), (346, 1.0),
        (624, 1.0), (625, 0.0), (3578, 0.0),
    ):
        constraint.influence = influence
        constraint.keyframe_insert(data_path="influence", frame=frame)
    action = target.animation_data.action if target.animation_data else None
    path = constraint.path_from_id("influence")
    for curve in get_fcurves(action):
        if curve.data_path == path:
            for point in curve.keyframe_points:
                point.interpolation = "CONSTANT"
            curve.update()
    target["opening_subject_lock"] = "incident particle centered F00346-F00624"


def verify() -> dict:
    scene = bpy.context.scene
    barrier = bpy.data.objects["GEO_Barrier_Plain"]
    expected = {
        2745: (0.6, 7.0, 4.48),
        2805: (0.6, 7.0, 7.28),
        2848: (0.6, 7.0, 5.6),
        2878: (0.3, 7.0, 5.6),
        2928: (0.9, 7.0, 5.6),
        2961: (0.6, 7.0, 5.6),
    }
    samples = []
    for frame, wanted in expected.items():
        scene.frame_set(frame)
        actual = tuple(round(v, 4) for v in barrier.dimensions)
        if any(abs(a - b) > 0.0002 for a, b in zip(actual, wanted)):
            raise RuntimeError(f"Barrier endpoint mismatch at {frame}: {actual} != {wanted}")
        samples.append({"frame": frame, "dimensions": list(actual)})

    scene.frame_set(2805)
    width_during_height = [round(bpy.data.objects[n].scale.x, 4) for n in (
        "GEO_V3_Width_Arrow_Left", "GEO_V3_Width_Arrow_Right"
    )]
    scene.frame_set(2928)
    height_during_width = [round(bpy.data.objects[n].scale.x, 4) for n in (
        "GEO_V3_Height_Arrow_Bottom", "GEO_V3_Height_Arrow_Top"
    )]
    if max(width_during_height) > 0.002 or max(height_during_width) > 0.002:
        raise RuntimeError("Arrow visibility gates overlap")

    camera = bpy.data.objects["CAM_V4_Particle_Wave_Follow"]
    particle = bpy.data.objects["GEO_Incident_Particle"]
    barrier_position = bpy.data.objects["GEO_Barrier_Plain"].matrix_world.translation
    camera_samples = []
    for frame in (346, 380, 405, 470, 505, 624):
        scene.frame_set(frame)
        q = camera.matrix_world.to_quaternion()
        forward = (q @ Vector((0.0, 0.0, -1.0))).normalized()
        up = (q @ Vector((0.0, 1.0, 0.0))).normalized()
        camera_position = camera.matrix_world.translation
        particle_position = particle.matrix_world.translation
        to_particle = (particle_position - camera_position).normalized()
        error = math.degrees(forward.angle(to_particle))
        if error > 0.1:
            raise RuntimeError(f"Particle is not centered at {frame}: {error:.4f} degrees")
        sample = {"frame": frame, "center_error_degrees": round(error, 4)}
        if frame == 346:
            sample["camera_x_between_particle_and_barrier"] = bool(
                min(particle_position.x, barrier_position.x)
                <= camera_position.x
                <= max(particle_position.x, barrier_position.x)
            )
            sample["camera_up_dot_world_z"] = round(up.dot(Vector((0.0, 0.0, 1.0))), 4)
            if not sample["camera_x_between_particle_and_barrier"]:
                raise RuntimeError("Opening camera is not between particle and barrier")
            if sample["camera_up_dot_world_z"] < 0.9:
                raise RuntimeError("Opening camera top is not aligned with world +Z")
        camera_samples.append(sample)
    return {
        "barrier_samples": samples,
        "width_arrow_scale_during_height": width_during_height,
        "height_arrow_scale_during_width": height_during_width,
        "opening_camera_samples": camera_samples,
    }


def update_reports(result: dict) -> None:
    if REPORT_JSON.exists():
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    else:
        payload = {}
    payload["qa_correction"] = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "final_render_executed": False,
        "fixed": [
            "locked barrier height endpoints to 0.8V0, 1.3V0, V0",
            "locked barrier width endpoints to 0.5W, 1.5W, W",
            "separated height-arrow and width-arrow visibility windows",
            "locked the opening follow camera target to the moving particle",
        ],
        **result,
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    note = (
        "\n## 画面 QA 修正\n\n"
        "- 势垒高度端点已精确锁定为 `0.8V0 → 1.3V0 → V0`。\n"
        "- 势垒厚度端点已精确锁定为 `0.5W → 1.5W → W`。\n"
        "- 高度箭头仅在高度阶段显示，厚度箭头仅在厚度阶段显示，不再提前串场。\n"
        "- 粒子跟随镜头在 F00346–F00624 持续锁定粒子中心；起始镜头位于粒子与势垒之间，镜头上方对齐世界 +Z。\n"
        "- 仅保存工程，未执行最终动画渲染。\n"
    )
    text = REPORT_MD.read_text(encoding="utf-8") if REPORT_MD.exists() else "# Blender V5 语音对齐动作表\n"
    if "## 画面 QA 修正" in text:
        text = text.split("## 画面 QA 修正", 1)[0].rstrip() + "\n"
    REPORT_MD.write_text(text + note, encoding="utf-8")


def main() -> None:
    if Path(bpy.data.filepath).resolve() != V5.resolve():
        raise RuntimeError(f"Open V5 before running this script: {V5}")
    scene = bpy.context.scene
    if (scene.render.resolution_x, scene.render.resolution_y, scene.render.fps) != (1300, 1080, 60):
        raise RuntimeError("Unexpected V5 output settings")

    rebuild_barrier_parameter_motion()
    rebuild_arrow_gates()
    enforce_particle_centering()
    result = verify()
    scene["qa_visual_pass"] = "barrier endpoints and arrow handoff corrected"
    scene["final_render_executed"] = 0
    update_reports(result)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(V5), check_existing=False)
    print("V5_QA_FIXED=" + json.dumps(result, ensure_ascii=False))


main()
