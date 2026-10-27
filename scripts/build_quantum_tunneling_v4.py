"""Build Blender V4 directly from the retained V3 full-render scene.

V4 changes the opening camera grammar and replaces the later two planar
component ribbons with one scientifically mapped complex-wavefunction helix.
The existing barrier study, collapse, and many-trial animation are preserved.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Quaternion


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUTPUT_BLEND = ROOT / "quantum_tunneling_scientific_v4.blend"
REPORT_PATH = ROOT / "docs" / "build_report_v4.json"
TIMELINE_PATH = ROOT / "sync" / "master_timeline_v4.json"
FRAME_DIR = ROOT / "renders" / "final_v4" / "frames"

CUT_FRAME = 510
PLANAR_IN_START = 1050
PLANAR_IN_END = 1120
HELIX_FIT_START = 1180
HELIX_FIT_END = 1320
Y_MOVE_END = 1560
PROBABILITY_IN_START = 1560
PROBABILITY_IN_END = 1660
COLLAPSE_START = 4380
COLLAPSE_END = 4500


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


def set_interpolation(id_block, interpolation="BEZIER", clamped=True):
    animation = getattr(id_block, "animation_data", None)
    action = animation.action if animation else None
    for curve in get_fcurves(action):
        for point in curve.keyframe_points:
            point.interpolation = interpolation
            if interpolation == "BEZIER":
                handle = "AUTO_CLAMPED" if clamped else "AUTO"
                point.handle_left_type = handle
                point.handle_right_type = handle


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def create_camera(name, lens, location, target_location, collection, lock_world_z_up=False):
    camera_data = bpy.data.cameras.new(name + "_Data")
    camera_data.lens = lens
    camera_data.sensor_width = 36.0
    camera_data.clip_start = 0.05
    camera_data.clip_end = 1000.0
    camera = bpy.data.objects.new(name, camera_data)
    camera.location = location
    collection.objects.link(camera)

    target = bpy.data.objects.new(name + "_Target", None)
    target.empty_display_type = "SPHERE"
    target.empty_display_size = 0.25
    target.location = target_location
    collection.objects.link(target)

    if lock_world_z_up:
        constraint = camera.constraints.new(type="TRACK_TO")
        constraint.name = "V4_Center_Subject_World_Z_Up"
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"
        constraint.use_target_z = True
    else:
        constraint = camera.constraints.new(type="DAMPED_TRACK")
        constraint.name = "V4_Center_Subject"
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
    return camera, target


def camera_key(camera, target, frame, location, target_location, lens):
    camera.location = location
    camera.keyframe_insert(data_path="location", frame=frame)
    target.location = target_location
    target.keyframe_insert(data_path="location", frame=frame)
    camera.data.lens = lens
    camera.data.keyframe_insert(data_path="lens", frame=frame)


def build_cameras():
    collection = ensure_collection("50_CAMERAS")

    intro, intro_target = create_camera(
        "CAM_V4_Barrier_Intro", 55.0, (8.5, -16.0, 6.5), (0.3, 0.0, 2.0), collection
    )
    intro_keys = [
        (0, (8.5, -16.0, 6.5), (0.3, 0.0, 2.0), 55.0),
        (300, (6.5, -13.0, 5.4), (0.3, 0.0, 2.2), 62.0),
        (450, (7.5, -15.0, 6.0), (0.3, 0.0, 2.0), 55.0),
        (CUT_FRAME - 1, (7.5, -15.0, 6.0), (0.3, 0.0, 2.0), 55.0),
    ]
    for key in intro_keys:
        camera_key(intro, intro_target, *key)

    follow, follow_target = create_camera(
        "CAM_V4_Particle_Wave_Follow", 62.0, (-17.5, 0.0, 3.96), (-31.0, 0.0, 0.34), collection,
        lock_world_z_up=True,
    )
    # The camera starts between the particle and barrier, looking back toward
    # -X at a 15-degree downward angle. Track-To keeps camera-local +Y (screen
    # up) aligned to world +Z. A tiny Y offset is introduced only while
    # approaching the vertical top-down pose, avoiding the tracking singularity.
    follow_keys = [
        (510, (-17.50, 0.00, 3.96), (-31.00, 0.00, 0.34), 62.0),
        (600, (-17.50, 0.00, 3.96), (-31.00, 0.00, 0.34), 62.0),
        (720, (-13.50, 0.00, 3.96), (-27.00, 0.00, 0.34), 60.0),
        (780, (-14.33, -0.18, 7.40), (-25.13, 0.00, 0.34), 58.0),
        (900, (-17.20, -0.42, 15.40), (-22.00, 0.00, 0.34), 56.0),
        (960, (-19.30, -0.55, 18.00), (-19.49, 0.00, 0.34), 55.0),
        (1080, (-16.00, -0.55, 18.00), (-16.00, 0.00, 0.34), 55.0),
        (1199, (-16.00, -0.55, 18.00), (-16.00, 0.00, 0.34), 55.0),
        (1320, (-16.00, -0.70, 18.00), (-16.00, 0.00, 0.34), 55.0),
        (1440, (-16.50, -9.50, 14.00), (-14.00, 0.00, 0.50), 55.0),
        # Maintain an oblique X/Y view after the Y-axis translation.  The
        # complex curve now visibly wraps around X instead of collapsing into
        # a side-on sine projection.
        (1560, (-22.00, -22.00, 8.20), (-10.00, 0.00, 0.80), 55.0),
        (1800, (-12.00, -26.00, 8.80), (-4.00, 0.00, 1.40), 55.0),
        (1980, (-8.00, -29.00, 9.50), (0.30, 0.00, 2.80), 55.0),
        (2400, (-8.00, -29.00, 9.50), (0.30, 0.00, 2.80), 55.0),
        (2700, (-7.50, -29.50, 9.60), (0.30, 0.00, 2.80), 55.0),
        (3060, (-6.00, -29.00, 10.00), (0.30, 0.00, 2.80), 55.0),
        (3420, (-8.00, -29.00, 9.20), (0.30, 0.00, 2.80), 55.0),
        (3780, (-6.00, -29.00, 9.60), (0.30, 0.00, 2.80), 55.0),
        (4080, (-8.00, -29.00, 9.50), (0.30, 0.00, 2.80), 55.0),
        (4200, (-4.00, -25.00, 8.00), (1.20, 0.00, 2.40), 55.0),
        (4260, (1.00, -20.00, 6.50), (2.50, 0.00, 1.80), 55.0),
        (4380, (6.20, -12.00, 3.60), (5.60, 0.00, 0.28), 55.0),
        (4500, (6.40, -10.50, 3.20), (5.60, 0.00, 0.28), 55.0),
        (4620, (9.00, -30.00, 11.00), (5.60, 0.00, 0.50), 55.0),
        (4800, (3.00, -50.00, 18.00), (0.00, 0.00, 0.40), 55.0),
        (4980, (-3.00, -40.00, 14.00), (-3.00, 0.00, 0.65), 55.0),
        (5160, (-1.20, -27.00, 9.50), (-0.80, 0.00, 0.55), 55.0),
        (5399, (0.30, -19.00, 7.00), (0.30, 0.00, 0.50), 55.0),
    ]
    for key in follow_keys:
        camera_key(follow, follow_target, *key)

    # The target's local Z is the camera's roll reference. It starts as world
    # +Z, then rotates toward +Y before the camera reaches the top-down
    # singularity, and returns to +Z as the camera moves into the side view.
    follow_target.rotation_mode = "QUATERNION"
    identity = Quaternion((1.0, 0.0, 0.0, 0.0))
    topdown_safe_up = Quaternion((1.0, 0.0, 0.0), math.radians(-90.0))
    up_reference_keys = [
        (510, identity),
        (600, identity),
        (960, topdown_safe_up),
        (1200, topdown_safe_up),
        (1440, identity),
        (5399, identity),
    ]
    for frame, rotation in up_reference_keys:
        follow_target.rotation_quaternion = rotation
        follow_target.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    for block in (intro, intro_target, intro.data, follow, follow_target, follow.data):
        set_interpolation(block, "BEZIER", clamped=True)

    scene = bpy.context.scene
    scene.timeline_markers.clear()
    intro_marker = scene.timeline_markers.new("V4 / BARRIER INTRO", frame=0)
    intro_marker.camera = intro
    follow_marker = scene.timeline_markers.new("V4 / CONTINUOUS PARTICLE + WAVE CAMERA", frame=CUT_FRAME)
    follow_marker.camera = follow
    scene.camera = intro
    return intro, follow, intro_keys, follow_keys


def centerline_from_keyblock(keyblock):
    points = []
    data = keyblock.data
    if len(data) % 2:
        raise RuntimeError(f"Expected paired ribbon vertices, got {len(data)}")
    for index in range(0, len(data), 2):
        a = data[index].co
        b = data[index + 1].co
        points.append(((a.x + b.x) * 0.5, (a.y + b.y) * 0.5))
    return points


def create_emissive_material(name, base_color, emission_color, strength=3.0, alpha=1.0):
    old = bpy.data.materials.get(name)
    if old is not None:
        bpy.data.materials.remove(old, do_unlink=True)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*base_color[:3], alpha)
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    node = next(item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = (*base_color[:3], 1.0)
    node.inputs["Roughness"].default_value = 0.28
    node.inputs["Metallic"].default_value = 0.05
    node.inputs["Emission Color"].default_value = (*emission_color[:3], 1.0)
    node.inputs["Emission Strength"].default_value = strength
    node.inputs["Alpha"].default_value = alpha
    return material, node


def key_socket(socket, values, interpolation="BEZIER"):
    for frame, value in values:
        socket.default_value = value
        socket.keyframe_insert(data_path="default_value", frame=frame)
    node_tree = socket.id_data
    set_interpolation(node_tree, interpolation, clamped=True)


def build_complex_helix():
    real = bpy.data.objects.get("GEO_Wave_Real_XY")
    imag = bpy.data.objects.get("GEO_Wave_Imag_XY")
    if real is None or imag is None:
        raise RuntimeError("V3 real/imag wave ribbons are missing")
    real_keys = real.data.shape_keys
    imag_keys = imag.data.shape_keys
    if real_keys is None or imag_keys is None:
        raise RuntimeError("V3 wave shape keys are missing")
    if [item.name for item in real_keys.key_blocks] != [item.name for item in imag_keys.key_blocks]:
        raise RuntimeError("Real and imaginary snapshots do not share topology")

    basis_real = centerline_from_keyblock(real_keys.key_blocks[0])
    basis_imag = centerline_from_keyblock(imag_keys.key_blocks[0])
    curve_data = bpy.data.curves.new("CURVE_V4_Complex_Wavefunction_Helix", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 2
    curve_data.bevel_depth = 0.055
    curve_data.bevel_resolution = 4
    curve_data.resolution_u = 2
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(basis_real) - 1)
    for point, (real_point, imag_point) in zip(spline.points, zip(basis_real, basis_imag)):
        x_value = (real_point[0] + imag_point[0]) * 0.5
        point.co = (x_value, real_point[1], imag_point[1], 1.0)

    helix = bpy.data.objects.new("GEO_V4_Complex_Wavefunction_Helix", curve_data)
    ensure_collection("20_WAVEFUNCTION").objects.link(helix)
    helix.location = (0.0, 0.0, 0.34)
    helix["scientific_mapping"] = "r(x,t)=(x, Re(psi(x,t)), Im(psi(x,t)))"
    helix["radius_quantity"] = "|psi(x,t)|"
    helix["phase_quantity"] = "arg(psi(x,t))"
    helix["replaces"] = "GEO_Wave_Real_XY + GEO_Wave_Imag_XY after frame 1320"

    material, node = create_emissive_material(
        "MAT_V4_Complex_Helix", (0.005, 0.06, 0.32), (0.02, 0.28, 1.0), strength=1.8, alpha=0.0
    )
    curve_data.materials.append(material)

    basis = helix.shape_key_add(name="Basis", from_mix=False)
    for point, real_point, imag_point in zip(basis.data, basis_real, basis_imag):
        x_value = (real_point[0] + imag_point[0]) * 0.5
        point.co = (x_value, real_point[1], imag_point[1])

    for real_block, imag_block in zip(list(real_keys.key_blocks)[1:], list(imag_keys.key_blocks)[1:]):
        block = helix.shape_key_add(name=real_block.name, from_mix=False)
        real_points = centerline_from_keyblock(real_block)
        imag_points = centerline_from_keyblock(imag_block)
        for point, real_point, imag_point in zip(block.data, real_points, imag_points):
            x_value = (real_point[0] + imag_point[0]) * 0.5
            point.co = (x_value, real_point[1], imag_point[1])

    # Link each helix snapshot weight to the source snapshot with an internal
    # single-property driver. This preserves the already approved propagation
    # timing exactly (including its interpolation) without duplicating or
    # re-sampling nearly 1,400 frames of animation.
    for block in list(helix.data.shape_keys.key_blocks)[1:]:
        driver_curve = block.driver_add("value")
        driver = driver_curve.driver
        driver.type = "SCRIPTED"
        variable = driver.variables.new()
        variable.name = "source_weight"
        variable.type = "SINGLE_PROP"
        variable.targets[0].id_type = "KEY"
        variable.targets[0].id = real_keys
        variable.targets[0].data_path = f'key_blocks["{block.name}"].value'
        driver.expression = "source_weight"

    # A flattened complex curve first replaces the two planar projections; its
    # imaginary dimension then opens smoothly to form the 3D helix.
    helix.scale = (1.0, 1.0, 0.001)
    helix.keyframe_insert(data_path="scale", frame=0)
    helix.keyframe_insert(data_path="scale", frame=HELIX_FIT_START)
    helix.keyframe_insert(data_path="scale", frame=1210)
    helix.scale = (1.0, 1.0, 1.0)
    helix.keyframe_insert(data_path="scale", frame=HELIX_FIT_END)
    helix.keyframe_insert(data_path="scale", frame=COLLAPSE_START)
    helix.scale = (1.0, 1.0, 0.001)
    helix.keyframe_insert(data_path="scale", frame=COLLAPSE_END)
    set_interpolation(helix, "BEZIER", clamped=True)

    key_socket(node.inputs["Alpha"], [
        (0, 0.0), (HELIX_FIT_START, 0.0), (1250, 1.0),
        (COLLAPSE_START, 1.0), (COLLAPSE_END, 0.0), (5399, 0.0),
    ])
    key_socket(node.inputs["Emission Color"], [
        (0, (0.02, 0.28, 1.0, 1.0)),
        (1810, (0.02, 0.28, 1.0, 1.0)),
        (1880, (0.30, 0.82, 1.0, 1.0)),
        (1970, (0.02, 0.28, 1.0, 1.0)),
        (5399, (0.02, 0.28, 1.0, 1.0)),
    ])
    key_socket(node.inputs["Emission Strength"], [
        (0, 0.0), (HELIX_FIT_START, 0.0), (1250, 1.8),
        (1810, 1.8), (1880, 4.0), (1945, 2.6), (1970, 1.8),
        (COLLAPSE_START, 1.8), (COLLAPSE_END, 0.0), (5399, 0.0),
    ])
    return helix


def reset_planar_material(material_name, emission_color):
    material = bpy.data.materials[material_name]
    node = next(item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED")
    material.node_tree.animation_data_clear()
    key_socket(node.inputs["Alpha"], [
        (0, 0.0), (PLANAR_IN_START, 0.0), (PLANAR_IN_END, 0.92),
        (1190, 0.92), (HELIX_FIT_END, 0.0), (5399, 0.0),
    ])
    key_socket(node.inputs["Emission Color"], [
        (0, (*emission_color, 1.0)), (5399, (*emission_color, 1.0)),
    ])
    key_socket(node.inputs["Emission Strength"], [
        (0, 0.0), (PLANAR_IN_START, 0.0), (PLANAR_IN_END, 3.2),
        (1190, 3.2), (HELIX_FIT_END, 0.0), (5399, 0.0),
    ])


def reset_probability_material():
    material = bpy.data.materials["MAT_Wave_Amplitude_Envelope"]
    node = next(item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED")
    material.node_tree.animation_data_clear()
    key_socket(node.inputs["Alpha"], [
        (0, 0.0), (PROBABILITY_IN_START, 0.0), (PROBABILITY_IN_END, 0.42),
        (COLLAPSE_START, 0.42), (COLLAPSE_END, 0.0), (5399, 0.0),
    ])
    key_socket(node.inputs["Emission Color"], [
        (0, (0.05, 0.55, 0.90, 1.0)),
        (1810, (0.05, 0.55, 0.90, 1.0)),
        (1880, (0.20, 0.95, 1.00, 1.0)),
        (1970, (0.05, 0.55, 0.90, 1.0)),
        (5399, (0.05, 0.55, 0.90, 1.0)),
    ])
    key_socket(node.inputs["Emission Strength"], [
        (0, 0.0), (PROBABILITY_IN_START, 0.0), (PROBABILITY_IN_END, 0.65),
        (1810, 0.65), (1880, 4.2), (1945, 1.1), (1970, 0.65),
        (COLLAPSE_START, 0.65), (COLLAPSE_END, 0.0), (5399, 0.0),
    ])


def export_timeline():
    timeline = {
        "schema": "quantum-tunneling-master-timeline-v4",
        "fps": 60,
        "resolution": [1920, 1080],
        "frame_range": [0, 5399],
        "camera": {
            "intro": "CAM_V4_Barrier_Intro",
            "continuous_after_cut": "CAM_V4_Particle_Wave_Follow",
            "only_cut_frame": CUT_FRAME,
            "initial_follow_sightline_degrees_to_negative_x": 15.0,
            "initial_follow_plane": "XZ",
            "initial_follow_position_relation": "between incident particle and barrier",
            "screen_up_axis": "+Z",
        },
        "segments": [
            {"name": "barrier_intro", "frames": [0, 509]},
            {"name": "particle_follow_15deg_to_topdown", "frames": [510, 1079]},
            {"name": "particle_to_planar_real_imag", "frames": [1080, 1199]},
            {"name": "planar_to_3d_complex_helix", "frames": [1200, 1319]},
            {"name": "camera_translate_y_probability_reveal", "frames": [1320, 1739]},
            {"name": "formula_with_blender_highlight", "frames": [1740, 2039]},
            {"name": "probability_chart_live", "frames": [2040, 2879]},
            {"name": "width_study", "frames": [2880, 3419]},
            {"name": "height_study", "frames": [3420, 3959]},
            {"name": "comparison_hold", "frames": [3960, 4079]},
            {"name": "overlay_out", "frames": [4080, 4139]},
            {"name": "collapse_ensemble", "frames": [4140, 4859]},
            {"name": "many_trials", "frames": [4860, 5399]},
        ],
        "complex_wavefunction_mapping": {
            "curve": "r(x,t)=(x, Re(psi), Im(psi))",
            "radius": "|psi|",
            "phase": "arg(psi)",
            "probability_density": "rho=|psi|^2",
            "probability_reveal_frames": [PROBABILITY_IN_START, PROBABILITY_IN_END],
        },
        "external_overlay_sync": {
            "formula_start": 1740,
            "probability_chart_start": 2040,
            "absolute_frame_numbers_unchanged_after_1740": True,
        },
    }
    TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE_PATH.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline


def main():
    if bpy.data.filepath and Path(bpy.data.filepath).resolve() == OUTPUT_BLEND.resolve():
        raise RuntimeError("Open the V3 full-render blend when rebuilding V4")

    intro, follow, intro_keys, follow_keys = build_cameras()
    helix = build_complex_helix()
    reset_planar_material("MAT_Wave_Real_Red", (1.0, 0.12, 0.15))
    reset_planar_material("MAT_Wave_Imag_Blue", (0.15, 0.45, 1.0))
    reset_probability_material()

    # Retire the old all-purpose camera without deleting editable V3 data.
    old_camera = bpy.data.objects.get("CAM_V3_Continuous")
    if old_camera:
        old_camera.hide_viewport = True

    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = 5399
    scene.render.fps = 60
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(FRAME_DIR / "frame_")
    scene["project_title"] = "Quantum Tunneling - Scientific V4"
    scene["camera_design"] = "barrier intro camera; one cut at frame 510; one continuous camera afterward"
    scene["complex_wavefunction_design"] = "3D helix r=(x,Re(psi),Im(psi)); radius=|psi|"
    scene["probability_reveal_frame"] = PROBABILITY_IN_END
    scene["review_status"] = "V4 keyframe review required before full render"
    scene["final_render_executed"] = 0

    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    timeline = export_timeline()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

    start_location = follow_keys[0][1]
    start_target = follow_keys[0][2]
    sightline = math.degrees(math.atan2(
        abs(start_target[2] - start_location[2]),
        abs(start_target[0] - start_location[0]),
    ))
    report = {
        "blend": str(OUTPUT_BLEND),
        "source": str(ROOT / "quantum_tunneling_scientific_v3_fullrender.blend"),
        "cameras": {
            "intro": intro.name,
            "follow": follow.name,
            "cut_frame": CUT_FRAME,
            "follow_initial_plane": "XZ",
            "follow_initial_sightline_degrees": sightline,
            "follow_initial_position_relation": "particle.x < camera.x < barrier.x",
            "follow_screen_up_axis": "+Z",
            "post_cut_hard_cuts": 0,
            "intro_key_count": len(intro_keys),
            "follow_key_count": len(follow_keys),
        },
        "wavefunction": {
            "object": helix.name,
            "mapping": helix["scientific_mapping"],
            "shape_key_count": len(helix.data.shape_keys.key_blocks),
            "sample_points": len(helix.data.splines[0].points),
            "planar_component_frames": [PLANAR_IN_START, HELIX_FIT_END],
            "helix_fit_frames": [HELIX_FIT_START, HELIX_FIT_END],
        },
        "probability": {
            "object": "GEO_Probability_Density_XZ",
            "hidden_until_camera_y_move": True,
            "fade_frames": [PROBABILITY_IN_START, PROBABILITY_IN_END],
        },
        "timeline": str(TIMELINE_PATH),
        "later_animation_preserved": "barrier study, collapse, ensemble, and many-trial object animation retained",
        "final_render_executed": False,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
