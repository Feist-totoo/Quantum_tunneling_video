"""Report the largest adjacent-frame pixel changes in selected time ranges."""

from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path

import numpy as np
from PIL import Image


def parse_range(value: str) -> tuple[float, float, str]:
    start, end, label = value.split(":", 2)
    return float(start), float(end), label


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--fps", type=float, default=60)
    parser.add_argument("--range", action="append", type=parse_range, required=True)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--size", default="160x90")
    args = parser.parse_args()

    width, height = (int(part) for part in args.size.lower().split("x", 1))
    report: dict[str, object] = {"schema": "adjacent_frame_diff.v1", "fps": args.fps, "ranges": []}
    for start_s, end_s, label in args.range:
        start = round(start_s * args.fps)
        end = round(end_s * args.fps)
        previous = np.asarray(
            Image.open(args.frames / f"fusion_{start:05d}.jpg").resize((width, height)),
            dtype=np.int16,
        )
        largest: list[tuple[float, int]] = []
        for frame in range(start + 1, end):
            current = np.asarray(
                Image.open(args.frames / f"fusion_{frame:05d}.jpg").resize((width, height)),
                dtype=np.int16,
            )
            difference = float(np.abs(current - previous).mean())
            heapq.heappush(largest, (difference, frame))
            if len(largest) > args.top:
                heapq.heappop(largest)
            previous = current
        report["ranges"].append(
            {
                "label": label,
                "start_seconds": start_s,
                "end_seconds": end_s,
                "largest_adjacent_diffs": [
                    {"to_frame": frame, "time_seconds": frame / args.fps, "mean_rgb_diff": round(diff, 4)}
                    for diff, frame in sorted(largest, reverse=True)
                ],
            }
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
