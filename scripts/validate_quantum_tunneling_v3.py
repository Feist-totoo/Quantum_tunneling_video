"""Validate saved V3 after reopening."""

import bpy
import json
import os


ROOT = r"C:\Users\liuzh\Desktop\1"
scene = bpy.context.scene


def spans(obj):
    coords = [v.co for v in obj.data.vertices]
    return {
        "x": max(v.x for v in coords) - min(v.x for v in coords),
        "y": max(v.y for v in coords) - min(v.y for v in coords),
        "z": max(v.z for v in coords) - min(v.z for v in coords),
    }


real = bpy.data.objects.get("GEO_Wave_Real_XY")
imag = bpy.data.objects.get("GEO_Wave_Imag_XY")
density = bpy.data.objects.get("GEO_Probability_Density_XZ")
camera = bpy.data.objects.get("CAM_V3_Continuous")
collapsed = bpy.data.objects.get("GEO_Collapsed_Transmitted_Particle")
hud_objects = [obj.name for obj in bpy.data.objects if
               obj.name.startswith("HUD_Probability") or
               obj.name.startswith("HUD_Chart") or
               obj.name.startswith("HUD_Formula") or
               obj.name.startswith("HUD_Bar_") or
               obj.name.startswith("HUD_Axis_") or
               obj.name.startswith("HUD_Readout_")]
texts = {name: bpy.data.objects.get(name) is not None for name in
         ("TXT_Barrier_W", "TXT_Barrier_V0", "TXT_Mapping")}
report = {
    "file": bpy.data.filepath,
    "frame_range": [scene.frame_start, scene.frame_end],
    "fps": scene.render.fps,
    "real_spans": spans(real) if real else None,
    "imag_spans": spans(imag) if imag else None,
    "density_spans": spans(density) if density else None,
    "density_shape_keys": len(density.data.shape_keys.key_blocks)
    if density and density.data.shape_keys else 0,
    "removed_hud_remaining": hud_objects,
    "required_markers": texts,
    "sync_files": {
        "timeline": os.path.exists(os.path.join(ROOT, "sync", "master_timeline_v3.json")),
        "probability_csv": os.path.exists(os.path.join(ROOT, "sync", "probability_frames_v3.csv")),
    },
    "final_render_executed": scene.get("final_render_executed"),
    "camera": {
        "active": scene.camera.name if scene.camera else None,
        "timeline_camera_markers": len([m for m in scene.timeline_markers if m.camera]),
        "location_keys": len(camera.animation_data.action.layers[0].strips[0].channelbags[0].fcurves[0].keyframe_points)
        if camera and camera.animation_data and camera.animation_data.action else 0,
    },
    "collapsed_particle_x": collapsed.location.x if collapsed else None,
}
checks = {
    "correct_file": os.path.basename(bpy.data.filepath) == "quantum_tunneling_scientific_v3.blend",
    "ninety_seconds": report["frame_range"] == [0, 5399] and report["fps"] == 60,
    "real_imag_xy": bool(real and imag and spans(real)["z"] < 1e-5 and spans(imag)["z"] < 1e-5),
    "density_xz": bool(density and spans(density)["y"] < 0.1 and spans(density)["z"] > 0.1),
    "density_is_rho": density.get("vertical_quantity") == "probability_density" if density else False,
    "density_baked": report["density_shape_keys"] >= 150,
    "chart_formula_removed": hud_objects == [],
    "markers_kept": all(texts.values()),
    "sync_exported": all(report["sync_files"].values()),
    "single_continuous_camera": bool(camera and scene.camera == camera and
                                     report["camera"]["timeline_camera_markers"] == 1 and
                                     report["camera"]["location_keys"] >= 25),
    "collapse_at_barrier_height_value": bool(collapsed and
                                              abs(collapsed.location.x - 5.6) < 1e-5),
    "final_render_not_run": report["final_render_executed"] in (0, False),
}
report["checks"] = checks
report["passed"] = all(checks.values())
path = os.path.join(ROOT, "docs", "review_validation_v3.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False, indent=2))
if not report["passed"]:
    raise RuntimeError("V3 validation failed")
