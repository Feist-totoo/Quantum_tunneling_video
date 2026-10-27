import bpy
import json
import math
from mathutils import Vector


scene = bpy.context.scene


def world_location(obj):
    return obj.matrix_world.translation.copy()


def camera_sample(frame):
    scene.frame_set(frame)
    cam = scene.camera
    q = cam.matrix_world.to_quaternion()
    position = world_location(cam)
    forward = (q @ Vector((0.0, 0.0, -1.0))).normalized()
    up = (q @ Vector((0.0, 1.0, 0.0))).normalized()

    particle = bpy.data.objects.get("GEO_Incident_Particle")
    barrier = bpy.data.objects.get("GEO_Barrier_Plain")
    item = {
        "frame": frame,
        "camera": cam.name,
        "camera_position": [round(v, 4) for v in position],
        "camera_forward": [round(v, 4) for v in forward],
        "camera_up": [round(v, 4) for v in up],
        "up_dot_world_z": round(up.dot(Vector((0.0, 0.0, 1.0))), 4),
    }
    if particle:
        p = world_location(particle)
        to_particle = (p - position)
        if to_particle.length:
            item["particle_position"] = [round(v, 4) for v in p]
            item["particle_center_error_deg"] = round(
                math.degrees(forward.angle(to_particle.normalized())), 4
            )
    if barrier:
        b = world_location(barrier)
        item["barrier_position"] = [round(v, 4) for v in b]
        if particle:
            item["camera_x_between_particle_and_barrier"] = bool(
                min(p.x, b.x) <= position.x <= max(p.x, b.x)
            )
    return item


keywords = ("Arrow", "arrow", "Width", "Height", "V0", "W_", "Indicator")
objects = []
for obj in bpy.data.objects:
    if any(word in obj.name for word in keywords):
        entry = {"name": obj.name, "type": obj.type}
        for frame in (2710, 2745, 2805, 2848, 2878, 2928, 2961):
            scene.frame_set(frame)
            entry[str(frame)] = {
                "hide_render": bool(obj.hide_render),
                "hide_viewport": bool(obj.hide_viewport),
                "scale": [round(v, 4) for v in obj.scale],
                "location": [round(v, 4) for v in obj.matrix_world.translation],
            }
        objects.append(entry)

data = {
    "engine": scene.render.engine,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "camera_samples": [camera_sample(f) for f in (346, 380, 405, 470, 505, 1022, 1135, 2710, 2805, 2928, 3006, 3239, 3578)],
    "cue_objects": objects,
}
print("V5_CAMERA_CUES=" + json.dumps(data, ensure_ascii=False))
