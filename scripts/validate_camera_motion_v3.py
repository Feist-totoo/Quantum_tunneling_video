"""Sample every V3 frame and verify that the single camera has no discontinuity."""

import bpy
import json
import math
import os


ROOT = r"C:\Users\liuzh\Desktop\1"
scene = bpy.context.scene
camera = bpy.data.objects.get("CAM_V3_Continuous")
if camera is None or scene.camera != camera:
    raise RuntimeError("V3 continuous camera is not active")

samples = []
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = camera.evaluated_get(depsgraph)
    samples.append({
        "frame": frame,
        "location": evaluated.matrix_world.translation.copy(),
        "rotation": evaluated.matrix_world.to_quaternion(),
        "lens": float(evaluated.data.lens),
    })

steps = []
for before, after in zip(samples, samples[1:]):
    dot = min(1.0, max(-1.0, abs(before["rotation"].dot(after["rotation"]))))
    steps.append({
        "frame": after["frame"],
        "location_step": (after["location"] - before["location"]).length,
        "rotation_step_degrees": math.degrees(2.0 * math.acos(dot)),
        "lens_step": abs(after["lens"] - before["lens"]),
    })

def peak(field):
    return max(steps, key=lambda item: item[field])

former_edit_points = [600, 1200, 4140, 4860]
boundary_samples = {}
for frame in former_edit_points:
    boundary_samples[str(frame)] = [
        item for item in steps if frame - 2 <= item["frame"] <= frame + 2
    ]

report = {
    "schema": "v3_camera_motion_validation.v1",
    "camera": camera.name,
    "sampled_frames": len(samples),
    "camera_markers": len([marker for marker in scene.timeline_markers if marker.camera]),
    "peak_location_step": peak("location_step"),
    "peak_rotation_step_degrees": peak("rotation_step_degrees"),
    "peak_lens_step": peak("lens_step"),
    "former_edit_point_neighborhoods": boundary_samples,
}
report["checks"] = {
    "single_active_camera": scene.camera == camera,
    "single_camera_marker": report["camera_markers"] == 1,
    "no_translation_jump": report["peak_location_step"]["location_step"] < 1.0,
    "no_rotation_jump": report["peak_rotation_step_degrees"]["rotation_step_degrees"] < 2.0,
    "no_lens_jump": report["peak_lens_step"]["lens_step"] < 1.0,
}
report["passed"] = all(report["checks"].values())

path = os.path.join(ROOT, "docs", "camera_motion_validation_v3.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False, indent=2))
if not report["passed"]:
    raise RuntimeError("V3 camera motion validation failed")
