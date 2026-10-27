import json
import bpy


scene = bpy.context.scene
barrier = bpy.data.objects.get("GEO_Barrier_Plain")


def snapshot(frame):
    scene.frame_set(frame)
    return {
        "frame": frame,
        "barrier_dimensions": [round(v, 4) for v in barrier.dimensions] if barrier else None,
        "camera": scene.camera.name if scene.camera else None,
    }


markers = [
    {
        "frame": marker.frame,
        "name": marker.name,
        "camera": marker.camera.name if marker.camera else None,
    }
    for marker in scene.timeline_markers
]
max_keyframe = 0.0
min_keyframe = None
keyframe_count = 0
for action in bpy.data.actions:
    for slot in action.slots:
        channelbag = action.layers[0].strips[0].channelbag(slot)
        if channelbag is None:
            continue
        for fcurve in channelbag.fcurves:
            for key in fcurve.keyframe_points:
                frame = float(key.co[0])
                max_keyframe = max(max_keyframe, frame)
                min_keyframe = frame if min_keyframe is None else min(min_keyframe, frame)
                keyframe_count += 1

result = {
    "frame_range": [scene.frame_start, scene.frame_end],
    "fps": scene.render.fps,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "render_percentage": scene.render.resolution_percentage,
    "global_offset": scene.get("blender_global_frame_offset"),
    "final_render_executed": scene.get("final_render_executed"),
    "timeline_markers": markers,
    "keyframes": {
        "count": keyframe_count,
        "min": min_keyframe,
        "max": max_keyframe,
        "within_scene_range": min_keyframe is not None and min_keyframe >= scene.frame_start and max_keyframe <= scene.frame_end,
    },
    "barrier_samples": [snapshot(frame) for frame in (2745, 2805, 2848, 2878, 2928, 2961)],
}
print("V5_VALIDATION=" + json.dumps(result, ensure_ascii=False, sort_keys=True))
