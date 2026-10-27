from __future__ import annotations

import difflib
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path


ROOT = Path(r"C:\Users\liuzh\Desktop\1\voice")
SCRIPT = ROOT / "量子隧穿配音时间帧标注.txt"
JSON_DIR = ROOT / "_timing_work_utf8"
FFMPEG = Path(r"D:\MY_WORLD\Tools\ffmpeg-2026-08-09-git-6bbc22dc09-full_build\bin\ffmpeg.exe")
FPS = 60


def keep_char(ch: str) -> bool:
    return unicodedata.category(ch)[0] in {"L", "N"}


def normalized_chars(text: str) -> list[str]:
    return [ch.lower() for ch in text if keep_char(ch)]


def recognized_chars(json_path: Path) -> tuple[list[str], list[float]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    chars: list[str] = []
    ends: list[float] = []
    for segment in data["segments"]:
        for word in segment.get("words", []):
            token = normalized_chars(word["word"])
            if not token:
                continue
            start = float(word["start"])
            end = float(word["end"])
            for i, ch in enumerate(token, 1):
                chars.append(ch)
                ends.append(start + (end - start) * i / len(token))
    return chars, ends


def silence_starts(audio_path: Path) -> list[float]:
    proc = subprocess.run(
        [
            str(FFMPEG), "-hide_banner", "-i", str(audio_path),
            "-af", "silencedetect=noise=-38dB:d=0.12", "-f", "null", "NUL",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    values = [float(v) for v in re.findall(r"silence_start:\s*([0-9.]+)", proc.stderr)]
    return [v for v in values if v > 0.25]


def align_line_ends(lines: list[str], json_path: Path, audio_path: Path) -> list[float]:
    original: list[str] = []
    line_last_indices: list[int] = []
    for line in lines:
        original.extend(normalized_chars(line))
        line_last_indices.append(len(original) - 1)

    recognized, rec_ends = recognized_chars(json_path)
    matcher = difflib.SequenceMatcher(a=original, b=recognized, autojunk=False)
    mapped: list[float | None] = [None] * len(original)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            continue
        if tag == "equal":
            for offset in range(i2 - i1):
                mapped[i1 + offset] = rec_ends[j1 + offset]
            continue
        if j2 > j1:
            span = i2 - i1
            for offset in range(span):
                pos = j1 + min(j2 - j1 - 1, math.floor((offset + 1) * (j2 - j1) / max(span, 1)) - 1)
                mapped[i1 + offset] = rec_ends[max(j1, pos)]

    known = [i for i, value in enumerate(mapped) if value is not None]
    for i, value in enumerate(mapped):
        if value is not None:
            continue
        left = max((k for k in known if k < i), default=None)
        right = min((k for k in known if k > i), default=None)
        if left is None:
            mapped[i] = rec_ends[0] * (i + 1) / (right + 1 if right is not None else len(mapped))
        elif right is None:
            mapped[i] = mapped[left]
        else:
            fraction = (i - left) / (right - left)
            mapped[i] = float(mapped[left]) + (float(mapped[right]) - float(mapped[left])) * fraction

    candidates = silence_starts(audio_path)
    raw = [float(mapped[index]) for index in line_last_indices]
    snapped: list[float] = []
    previous = 0.0
    for value in raw:
        nearby = [candidate for candidate in candidates if candidate > previous + 0.04 and abs(candidate - value) <= 0.34]
        chosen = min(nearby, key=lambda candidate: abs(candidate - value)) if nearby else value
        chosen = max(chosen, previous + 0.04)
        snapped.append(chosen)
        previous = chosen
    return snapped


def main() -> None:
    all_lines = [line.strip() for line in SCRIPT.read_text(encoding="utf-8").splitlines() if line.strip()]
    voice1_lines = all_lines[:18]
    pause_marker = all_lines[18]
    voice2_lines = all_lines[19:]

    voice1_ends = align_line_ends(voice1_lines, JSON_DIR / "配音1.json", ROOT / "配音1.wav")
    voice2_ends = align_line_ends(voice2_lines, JSON_DIR / "配音2.json", ROOT / "配音2.wav")

    voice1_frame_count = math.ceil(44.474830 * FPS)
    voice2_start = voice1_frame_count + 100

    print("VOICE1")
    for line, seconds in zip(voice1_lines, voice1_ends):
        print(f"{line}\t{seconds:8.3f}s\tF{round(seconds * FPS):05d}")
    print(f"{pause_marker}\tgap F{voice1_frame_count:05d}-F{voice2_start - 1:05d}")
    print("VOICE2")
    for line, seconds in zip(voice2_lines, voice2_ends):
        print(f"{line}\t{seconds:8.3f}s local\tF{voice2_start + round(seconds * FPS):05d}")


if __name__ == "__main__":
    main()
