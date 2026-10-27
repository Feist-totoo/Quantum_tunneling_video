"""Frame-exact adapter shared by Manim scenes and editorial QA."""

from __future__ import annotations

import argparse
import csv
import json
import math
from bisect import bisect_left
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMELINE_PATH = ROOT / "sync" / "master_timeline_v3.json"
CSV_PATH = ROOT / "sync" / "probability_frames_v3.csv"


class V3Sync:
    def __init__(self, timeline_path=TIMELINE_PATH, csv_path=CSV_PATH):
        self.timeline = json.loads(Path(timeline_path).read_text(encoding="utf-8"))
        with Path(csv_path).open(encoding="utf-8-sig", newline="") as handle:
            self.rows = list(csv.DictReader(handle))
        self.frames = [int(row["blender_frame"]) for row in self.rows]

    @property
    def fps(self):
        return int(self.timeline["fps"])

    def manim_to_blender(self, manim_frame):
        return int(manim_frame) + 1200

    def blender_to_manim(self, blender_frame):
        return int(blender_frame) - 1200

    def row_at_blender_frame(self, frame, interpolate=True):
        frame = int(frame)
        index = bisect_left(self.frames, frame)
        if index == 0:
            return self._numeric(self.rows[0])
        if index >= len(self.rows):
            return self._numeric(self.rows[-1])
        if self.frames[index] == frame or not interpolate:
            return self._numeric(self.rows[index])
        left = self._numeric(self.rows[index - 1])
        right = self._numeric(self.rows[index])
        t = (frame - left["blender_frame"]) / (right["blender_frame"] - left["blender_frame"])
        result = dict(left)
        for key in ("p_before", "p_after", "p_inside", "log10_before", "log10_after",
                    "width_factor", "height_factor", "comparison_before", "comparison_after"):
            result[key] = left[key] + (right[key] - left[key]) * t
        result["blender_frame"] = frame
        result["manim_frame"] = self.blender_to_manim(frame)
        result["time_seconds"] = frame / self.fps
        return result

    def row_at_manim_frame(self, frame, interpolate=True):
        return self.row_at_blender_frame(self.manim_to_blender(frame), interpolate)

    @staticmethod
    def _numeric(row):
        result = dict(row)
        for key in ("blender_frame", "manim_frame"):
            result[key] = int(result[key])
        for key in ("time_seconds", "p_before", "p_after", "p_inside",
                    "log10_before", "log10_after", "width_factor", "height_factor",
                    "comparison_before", "comparison_after"):
            result[key] = float(result[key])
        return result

    def check(self):
        errors = []
        if self.fps != 60:
            errors.append("fps must be 60")
        for previous, current in zip(self.frames, self.frames[1:]):
            if current - previous != 3:
                errors.append(f"frame stride error: {previous}->{current}")
        for row in self.rows:
            numeric = self._numeric(row)
            if numeric["manim_frame"] != numeric["blender_frame"] - 1200:
                errors.append(f"offset error at {numeric['blender_frame']}")
            for key in ("p_before", "p_after", "p_inside", "comparison_before", "comparison_after"):
                value = numeric[key]
                if not math.isfinite(value) or not 0.0 <= value <= 1.000001:
                    errors.append(f"invalid {key} at {numeric['blender_frame']}: {value}")
        return {"passed": not errors, "rows": len(self.rows), "first": self.frames[0],
                "last": self.frames[-1], "errors": errors[:20]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--manim-frame", type=int)
    args = parser.parse_args()
    sync = V3Sync()
    if args.check:
        result = sync.check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["passed"] else 1)
    frame = 0 if args.manim_frame is None else args.manim_frame
    print(json.dumps(sync.row_at_manim_frame(frame), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

