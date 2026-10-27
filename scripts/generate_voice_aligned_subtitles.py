"""Generate the editable Resolve subtitle handoff from the approved 60 fps cue sheet.

The cue sheet's annotated end frames are authoritative.  Offline Whisper word
timestamps are used only to estimate where each spoken line begins.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
VOICE_DIR = ROOT / "voice"
CUE_SHEET = VOICE_DIR / "量子隧穿配音时间帧标注.txt"
WHISPER_DIR = VOICE_DIR / "_timing_work_utf8"
OUTPUT_DIR = ROOT / "resolve_edit" / "subtitles"
SRT_PATH = OUTPUT_DIR / "quantum_tunnelling_zh_voice_aligned_60fps.srt"
JSON_PATH = OUTPUT_DIR / "quantum_tunnelling_zh_voice_aligned_60fps.json"
FPS = 60
VOICE2_START_FRAME = 2769


def keep_char(char: str) -> bool:
    return unicodedata.category(char)[0] in {"L", "N"}


def normalized_chars(text: str) -> list[str]:
    return [char.lower() for char in text if keep_char(char)]


def parse_cues() -> list[dict]:
    pattern = re.compile(r"^(.*?)\s+【读完约：F(\d{5})】\s+【对应画面：(.*?)】")
    cues = []
    for line in CUE_SHEET.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            cues.append(
                {
                    "text": match.group(1).strip(),
                    "end_frame": int(match.group(2)),
                    "visual_note": match.group(3).strip(),
                }
            )
    if len(cues) != 71:
        raise RuntimeError(f"Expected 71 spoken cues, found {len(cues)}")
    return cues


def recognized_chars(path: Path) -> tuple[list[str], list[float], list[float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chars: list[str] = []
    starts: list[float] = []
    ends: list[float] = []
    for segment in data["segments"]:
        for word in segment.get("words", []):
            token = normalized_chars(word["word"])
            if not token:
                continue
            start = float(word["start"])
            end = float(word["end"])
            for index, char in enumerate(token):
                chars.append(char)
                starts.append(start + (end - start) * index / len(token))
                ends.append(start + (end - start) * (index + 1) / len(token))
    return chars, starts, ends


def map_character_times(lines: list[str], whisper_path: Path) -> tuple[list[float], list[float]]:
    original: list[str] = []
    first_indices: list[int] = []
    last_indices: list[int] = []
    for line in lines:
        first_indices.append(len(original))
        original.extend(normalized_chars(line))
        last_indices.append(len(original) - 1)

    recognized, rec_starts, rec_ends = recognized_chars(whisper_path)
    matcher = difflib.SequenceMatcher(a=original, b=recognized, autojunk=False)
    mapped_start: list[float | None] = [None] * len(original)
    mapped_end: list[float | None] = [None] * len(original)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            continue
        if tag == "equal":
            for offset in range(i2 - i1):
                mapped_start[i1 + offset] = rec_starts[j1 + offset]
                mapped_end[i1 + offset] = rec_ends[j1 + offset]
            continue
        if j2 > j1:
            original_span = max(1, i2 - i1)
            recognized_span = j2 - j1
            for offset in range(i2 - i1):
                position = j1 + min(recognized_span - 1, int(offset * recognized_span / original_span))
                mapped_start[i1 + offset] = rec_starts[position]
                mapped_end[i1 + offset] = rec_ends[position]

    for mapped, fallback in ((mapped_start, rec_starts), (mapped_end, rec_ends)):
        known = [index for index, value in enumerate(mapped) if value is not None]
        for index, value in enumerate(mapped):
            if value is not None:
                continue
            left = max((candidate for candidate in known if candidate < index), default=None)
            right = min((candidate for candidate in known if candidate > index), default=None)
            if left is None and right is None:
                mapped[index] = fallback[0]
            elif left is None:
                mapped[index] = float(mapped[right])
            elif right is None:
                mapped[index] = float(mapped[left])
            else:
                fraction = (index - left) / (right - left)
                mapped[index] = float(mapped[left]) + (float(mapped[right]) - float(mapped[left])) * fraction

    return (
        [float(mapped_start[index]) for index in first_indices],
        [float(mapped_end[index]) for index in last_indices],
    )


def srt_timestamp(frame: int) -> str:
    milliseconds = round(frame * 1000 / FPS)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def main() -> None:
    cues = parse_cues()
    voice1 = cues[:18]
    voice2 = cues[18:]
    v1_starts, _ = map_character_times([cue["text"] for cue in voice1], WHISPER_DIR / "配音1.json")
    v2_starts, _ = map_character_times([cue["text"] for cue in voice2], WHISPER_DIR / "配音2.json")

    estimated_starts = [round(value * FPS) for value in v1_starts]
    estimated_starts += [VOICE2_START_FRAME + round(value * FPS) for value in v2_starts]
    # Whisper tends to assign the initial silence to the first word.  The WAV
    # silence detector measured these actual speech entrances.
    estimated_starts[0] = 21
    estimated_starts[18] = VOICE2_START_FRAME + 22

    previous_end = -1
    for index, (cue, estimate) in enumerate(zip(cues, estimated_starts), 1):
        start = max(previous_end + 1, estimate)
        start = min(start, cue["end_frame"] - 1)
        cue["index"] = index
        cue["start_frame"] = start
        cue["end_frame_exclusive"] = cue["end_frame"] + 1
        cue["start_timecode"] = srt_timestamp(start)
        cue["end_timecode"] = srt_timestamp(cue["end_frame"] + 1)
        previous_end = cue["end_frame"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    srt_blocks = []
    for cue in cues:
        srt_blocks.append(
            f"{cue['index']}\n{cue['start_timecode']} --> {cue['end_timecode']}\n{cue['text']}"
        )
    SRT_PATH.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8-sig")
    JSON_PATH.write_text(
        json.dumps(
            {
                "schema": "quantum-tunnelling-voice-aligned-subtitles-v2",
                "fps": FPS,
                "timeline_frame_start": 0,
                "voice1_frames": [0, 2668],
                "inter_voice_gap_frames": [2669, 2768],
                "voice2_start_frame": VOICE2_START_FRAME,
                "cue_count": len(cues),
                "cues": cues,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(SRT_PATH)
    print(JSON_PATH)
    print(f"cues={len(cues)} first={cues[0]['start_frame']} last={cues[-1]['end_frame']}")


if __name__ == "__main__":
    main()
