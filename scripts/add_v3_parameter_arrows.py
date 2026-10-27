"""Reapply the approved V3 barrier-parameter arrows without rendering."""

import bpy
import math
from pathlib import Path


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
BLEND = ROOT / "quantum_tunneling_scientific_v3.blend"


def action_curves(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbags"):
                for bag in strip.channelbags:
                    curves.extend(bag.fcurves)
    return curves


def tune(obj, interpolation="BEZIER"):
    if not (obj.animation_data and obj.animation_data.action):
        return
    for curve in action_curves(obj.animation_data.action):
        for point in curve.keyframe_points:
            point.interpolation = interpolation
            if interpolation == "BEZIER":
                point.handle_left_type = "AUTO_CLAMPED"
                point.handle_right_type = "AUTO_CLAMPED"


def main():
    collection = bpy.data.collections["40_ANNOTATION"]
    materials = {
        "W": bpy.data.materials["MAT_HUD_Width"],
        "V0": bpy.data.materials["MAT_HUD_Height"],
    }
    for obj in list(bpy.data.objects):
        if obj.name.startswith("GEO_V3_") and "Arrow" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

    def relink(obj):
        for owner in list(obj.users_collection):
            owner.objects.unlink(obj)
        collection.objects.link(obj)

    def arrow(name, material, length=1.75):
        root = bpy.data.objects.new(name, None)
        collection.objects.link(root)
        head_length = 0.50
        shaft_length = length - head_length * 0.72
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.075,
                                            depth=shaft_length)
        shaft = bpy.context.object
        shaft.name = name + "_Shaft"
        relink(shaft)
        shaft.parent = root
        shaft.rotation_euler.y = math.pi / 2
        shaft.location.x = -(head_length + shaft_length) / 2
        shaft.data.materials.append(material)
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.23, radius2=0.0,
                                       depth=head_length)
        head = bpy.context.object
        head.name = name + "_Head"
        relink(head)
        head.parent = root
        head.rotation_euler.y = math.pi / 2
        head.location.x = -head_length / 2
        head.data.materials.append(material)
        for child in (shaft, head):
            bevel = child.modifiers.new("Arrow_Soft_Edges", "BEVEL")
            bevel.width = 0.018
            bevel.segments = 2
        root["role"] = "barrier_parameter_change_indicator"
        root["style"] = "bold emissive paired arrow"
        return root

    def visibility(root, start, end):
        keys = [(0, .001), (start - 1, .001), (start + 24, 1.0),
                (start + 96, 1.08), (start + 168, 1.0),
                (end - 24, 1.0), (end, .001), (5399, .001)]
        for frame, factor in keys:
            root.scale = (factor,) * 3
            root.keyframe_insert("scale", frame=frame)
        tune(root)

    def width_factor(frame):
        if frame <= 2880: return 1.0
        if frame <= 3000: return 1.0 - .5 * (frame - 2880) / 120
        if frame <= 3060: return .5
        if frame <= 3240: return .5 + (frame - 3060) / 180
        if frame <= 3360: return 1.5
        return 1.5 - .5 * (frame - 3360) / 60

    def height_factor(frame):
        if frame <= 3420: return 1.0
        if frame <= 3540: return 1.0 - .2 * (frame - 3420) / 120
        if frame <= 3600: return .8
        if frame <= 3780: return .8 + .5 * (frame - 3600) / 180
        if frame <= 3900: return 1.3
        return 1.3 - .3 * (frame - 3900) / 60

    front_y = -3.82
    left = arrow("GEO_V3_Width_Arrow_Left", materials["W"])
    right = arrow("GEO_V3_Width_Arrow_Right", materials["W"])
    left.location = (-.16, front_y, 3.25)
    right.location = (.76, front_y, 3.25)
    right.rotation_euler.z = math.pi
    for frame in range(2880, 3421, 3):
        right.location.x = .60 * width_factor(frame) + .16
        right.keyframe_insert("location", frame=frame)
    tune(right, "LINEAR")
    visibility(left, 2880, 3420)
    visibility(right, 2880, 3420)

    bottom = arrow("GEO_V3_Height_Arrow_Bottom", materials["V0"])
    top = arrow("GEO_V3_Height_Arrow_Top", materials["V0"])
    bottom.location = (1.55, front_y, .12)
    bottom.rotation_euler.y = -math.pi / 2
    top.location = (1.55, front_y, 5.72)
    top.rotation_euler.y = math.pi / 2
    for frame in range(3420, 3961, 3):
        top.location.z = 5.6 * height_factor(frame) + .12
        top.keyframe_insert("location", frame=frame)
    tune(top, "LINEAR")
    visibility(bottom, 3420, 3960)
    visibility(top, 3420, 3960)

    bpy.context.scene["parameter_arrows_added_directly_to_v3"] = True
    bpy.context.scene["final_render_executed"] = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), check_existing=False)


if __name__ == "__main__":
    main()
