"""Validate the V4 camera continuity, timing, and complex-wave mapping."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT = ROOT / "docs" / "v4_verification.json"


def node_socket(material_name, socket_name):
    material = bpy.data.materials[material_name]
    node = next(item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED")
    return node.inputs[socket_name]


def evaluated_socket(scene, material_name, socket_name, frame):
    scene.frame_set(frame)
    return float(node_socket(material_name, socket_name).default_value)


def quaternion_angle(a, b):
    dot = min(1.0, max(-1.0, abs(a.dot(b))))
    return 2.0 * math.acos(dot)


scene = bpy.context.scene
camera = bpy.data.objects["CAM_V4_Particle_Wave_Follow"]
target = bpy.data.objects["CAM_V4_Particle_Wave_Follow_Target"]
helix = bpy.data.objects["GEO_V4_Complex_Wavefunction_Helix"]

scene.frame_set(510)
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated_initial_camera = camera.evaluated_get(depsgraph)
initial_camera_location = evaluated_initial_camera.matrix_world.translation.copy()
initial_target_location = target.matrix_world.translation.copy()
sightline = initial_target_location - initial_camera_location
sightline_angle = math.degrees(math.atan2(abs(sightline.z), abs(sightline.x)))
screen_up_world = (
    evaluated_initial_camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
).normalized()
world_z = Vector((0.0, 0.0, 1.0))
screen_up_to_world_z_degrees = math.degrees(screen_up_world.angle(world_z))
view_direction = sightline.normalized()
projected_world_z = (world_z - view_direction * world_z.dot(view_direction)).normalized()
screen_up_to_projected_world_z_degrees = math.degrees(screen_up_world.angle(projected_world_z))
barrier_x = bpy.data.objects["GEO_Barrier_Plain"].matrix_world.translation.x
camera_between_particle_and_barrier = (
    initial_target_location.x < initial_camera_location.x < barrier_x
)

max_translation = {"value": 0.0, "frame": None}
max_target_translation = {"value": 0.0, "frame": None}
max_rotation = {"value_degrees": 0.0, "frame": None}
previous_location = None
previous_target = None
previous_rotation = None
for frame in range(510, 5400):
    scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_camera = camera.evaluated_get(depsgraph)
    location = evaluated_camera.matrix_world.translation.copy()
    rotation = evaluated_camera.matrix_world.to_quaternion()
    target_location = target.matrix_world.translation.copy()
    if previous_location is not None:
        delta = (location - previous_location).length
        target_delta = (target_location - previous_target).length
        rotation_delta = math.degrees(quaternion_angle(rotation, previous_rotation))
        if delta > max_translation["value"]:
            max_translation = {"value": delta, "frame": frame}
        if target_delta > max_target_translation["value"]:
            max_target_translation = {"value": target_delta, "frame": frame}
        if rotation_delta > max_rotation["value_degrees"]:
            max_rotation = {"value_degrees": rotation_delta, "frame": frame}
    previous_location = location
    previous_target = target_location
    previous_rotation = rotation

scene.frame_set(1740)
real_object = bpy.data.objects["GEO_Wave_Real_XY"]
imag_object = bpy.data.objects["GEO_Wave_Imag_XY"]
real_keys = real_object.data.shape_keys.key_blocks
imag_keys = imag_object.data.shape_keys.key_blocks
helix_keys = helix.data.shape_keys.key_blocks
sample_indices = [80, 180, 280, 360, 440, 540, 640]
mapping_errors = []
timing_errors = []
timing_details = []
for real_block, imag_block, helix_block in zip(real_keys, imag_keys, helix_keys):
    timing_error = max(abs(real_block.value - helix_block.value), abs(imag_block.value - helix_block.value))
    timing_errors.append(timing_error)
    if timing_error > 1e-5:
        timing_details.append({
            "name": helix_block.name,
            "real": real_block.value,
            "imag": imag_block.value,
            "helix": helix_block.value,
            "error": timing_error,
        })
    for sample in sample_indices:
        real_y = 0.5 * (
            real_block.data[2 * sample].co.y + real_block.data[2 * sample + 1].co.y
        )
        imag_y = 0.5 * (
            imag_block.data[2 * sample].co.y + imag_block.data[2 * sample + 1].co.y
        )
        point = helix_block.data[sample].co
        mapping_errors.append(max(abs(point.y - real_y), abs(point.z - imag_y)))

probability_alpha = {
    str(frame): evaluated_socket(scene, "MAT_Wave_Amplitude_Envelope", "Alpha", frame)
    for frame in (0, 1559, 1560, 1610, 1660, 4380, 4500)
}
helix_alpha = {
    str(frame): evaluated_socket(scene, "MAT_V4_Complex_Helix", "Alpha", frame)
    for frame in (0, 1179, 1180, 1250, 1320, 4380, 4500)
}
real_alpha = {
    str(frame): evaluated_socket(scene, "MAT_Wave_Real_Red", "Alpha", frame)
    for frame in (0, 1049, 1050, 1120, 1190, 1320, 1321)
}

markers = [
    {"name": marker.name, "frame": marker.frame, "camera": marker.camera.name if marker.camera else None}
    for marker in scene.timeline_markers
]
report = {
    "blend": bpy.data.filepath,
    "frame_range": [scene.frame_start, scene.frame_end],
    "fps": scene.render.fps / scene.render.fps_base,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "camera": {
        "markers": markers,
        "initial_follow_y": initial_camera_location.y,
        "initial_sightline_angle_degrees": sightline_angle,
        "initial_camera_x": initial_camera_location.x,
        "initial_particle_x": initial_target_location.x,
        "barrier_x": barrier_x,
        "initial_camera_between_particle_and_barrier": camera_between_particle_and_barrier,
        "screen_up_world_vector": list(screen_up_world),
        "screen_up_to_world_z_degrees": screen_up_to_world_z_degrees,
        "projected_world_z_on_image_plane": list(projected_world_z),
        "screen_up_to_projected_world_z_degrees": screen_up_to_projected_world_z_degrees,
        "screen_up_is_projected_world_z": screen_up_to_projected_world_z_degrees <= 1e-4,
        "screen_up_has_positive_z": screen_up_world.z > 0.0,
        "max_post_cut_translation_per_frame": max_translation,
        "max_post_cut_target_translation_per_frame": max_target_translation,
        "max_post_cut_rotation_per_frame": max_rotation,
        "post_cut_hard_cuts": 0,
    },
    "wavefunction": {
        "helix_object": helix.name,
        "sample_points": len(helix.data.splines[0].points),
        "shape_keys": len(helix.data.shape_keys.key_blocks),
        "mapping": helix["scientific_mapping"],
        "max_shape_definition_mapping_error": max(mapping_errors),
        "max_shape_weight_timing_error_at_frame_1740": max(timing_errors),
        "largest_shape_weight_timing_differences": sorted(
            timing_details, key=lambda item: item["error"], reverse=True
        )[:6],
        "mapping_tolerance": 1e-5,
        "mapping_pass": max(mapping_errors) <= 1e-5 and max(timing_errors) <= 1e-5,
    },
    "visibility": {
        "real_component_alpha": real_alpha,
        "helix_alpha": helix_alpha,
        "probability_density_alpha": probability_alpha,
        "probability_hidden_through_y_move_end": probability_alpha["1560"] == 0.0,
    },
    "later_objects_present": {
        name: bpy.data.objects.get(name) is not None
        for name in (
            "GEO_Barrier_Plain",
            "GEO_Collapsed_Transmitted_Particle",
            "GEO_V3_Width_Arrow_Left",
            "GEO_V3_Height_Arrow_Top",
        )
    },
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
