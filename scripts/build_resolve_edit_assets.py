from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "resolve_edit" / "edit_plan_179_5s.json"
SUBTITLE_DIR = ROOT / "resolve_edit" / "subtitles"
SUBTITLE_SEGMENTS_PATH = SUBTITLE_DIR / "subtitle_segments_179_5s.json"
REPORT_DIR = ROOT / "resolve_edit" / "recording"
PUNCTUATION = "，。！？；：、,.!?;:"


def timecode(frame: int, fps: int, *, srt: bool = False) -> str:
    milliseconds = round(frame * 1000 / fps)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{milliseconds:03d}"


def spoken_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u9fffA-Za-z0-9]", text))


def visible_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def has_internal_punctuation(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    return any(character in PUNCTUATION for character in compact[:-1])


def validate_segments(cue: dict[str, object], segments: list[str]) -> None:
    source = str(cue["text"])
    if "".join(segments) != source:
        raise SystemExit(f"字幕断句没有完整还原台词：{cue['id']}")
    boundaries: set[int] = set()
    cursor = 0
    for segment in segments:
        cursor += len(segment)
        boundaries.add(cursor)
        limit = 9 if has_internal_punctuation(segment) else 16
        if visible_count(segment) > limit:
            raise SystemExit(
                f"字幕过长：{cue['id']}｜{segment}｜{visible_count(segment)}>{limit}"
            )
    previous_punctuation = -1
    for position, character in enumerate(source):
        if character not in PUNCTUATION:
            continue
        phrase = source[previous_punctuation + 1 : position]
        if spoken_count(phrase) > 4 and position + 1 not in boundaries:
            raise SystemExit(
                f"超过4字的标点断点未独立：{cue['id']}｜{phrase}{character}"
            )
        previous_punctuation = position


def punctuation_hold(text: str) -> float:
    if not text:
        return 0.0
    return {
        "。": 1.4,
        "！": 1.4,
        "？": 1.5,
        "；": 1.0,
        "：": 0.9,
        "，": 0.7,
        "、": 0.35,
        ".": 1.4,
        "!": 1.4,
        "?": 1.5,
        ";": 1.0,
        ":": 0.9,
        ",": 0.7,
    }.get(text[-1], 0.0)


def allocate_segment_frames(
    start: int, end: int, segments: list[str]
) -> list[tuple[int, int, str]]:
    weights = [max(1, spoken_count(text)) + punctuation_hold(text) for text in segments]
    total_weight = sum(weights)
    result: list[tuple[int, int, str]] = []
    cursor = start
    accumulated = 0.0
    for index, (text, weight) in enumerate(zip(segments, weights)):
        accumulated += weight
        segment_end = end if index == len(segments) - 1 else round(
            start + (end - start) * accumulated / total_weight
        )
        segment_end = max(cursor + 1, segment_end)
        result.append((cursor, segment_end, text))
        cursor = segment_end
    return result


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    subtitle_segments = json.loads(SUBTITLE_SEGMENTS_PATH.read_text(encoding="utf-8"))
    fps = int(plan["project"]["fps"])
    total_frames = int(plan["project"]["total_frames"])
    if total_frames > round(179.5 * fps):
        raise SystemExit("总时长超过179.5秒")

    SUBTITLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    srt_lines: list[str] = []
    subtitle_rows: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    subtitle_index = 1
    for cue in plan["narration"]:
        start = int(cue["start"])
        end = int(cue["end"])
        if not 0 <= start < end <= total_frames:
            raise SystemExit(f"非法字幕范围：{cue['id']}")
        duration = (end - start) / fps
        count = spoken_count(cue["text"])
        cps = count / duration
        segments = subtitle_segments.get(cue["id"])
        if not isinstance(segments, list) or not all(isinstance(item, str) for item in segments):
            raise SystemExit(f"缺少字幕断句：{cue['id']}")
        validate_segments(cue, segments)
        for segment_number, (segment_start, segment_end, text) in enumerate(
            allocate_segment_frames(start, end, segments), start=1
        ):
            srt_lines.extend(
                [
                    str(subtitle_index),
                    f"{timecode(segment_start, fps, srt=True)} --> {timecode(segment_end, fps, srt=True)}",
                    text,
                    "",
                ]
            )
            subtitle_rows.append(
                {
                    "字幕编号": f"S{subtitle_index:03d}",
                    "配音段": cue["id"],
                    "段内序号": segment_number,
                    "开始": timecode(segment_start, fps),
                    "结束": timecode(segment_end, fps),
                    "字符数": visible_count(text),
                    "内部标点": "是" if has_internal_punctuation(text) else "否",
                    "字幕": text,
                }
            )
            subtitle_index += 1
        rows.append(
            {
                "编号": cue["id"],
                "开始": timecode(start, fps),
                "结束": timecode(end, fps),
                "时长秒": f"{duration:.2f}",
                "口播字符": count,
                "字符每秒": f"{cps:.2f}",
                "台词": cue["text"],
                "人工配音提示": cue["direction"],
            }
        )

    srt_path = SUBTITLE_DIR / "quantum_tunnelling_zh_179_5s.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8-sig")

    subtitle_csv_path = REPORT_DIR / "subtitle_cues_179_5s.csv"
    with subtitle_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(subtitle_rows[0]))
        writer.writeheader()
        writer.writerows(subtitle_rows)

    csv_path = REPORT_DIR / "human_voice_cues_179_5s.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    total_chars = sum(int(row["口播字符"]) for row in rows)
    voiced_seconds = sum(float(row["时长秒"]) for row in rows)
    report_lines = [
        "# 人工配音与字幕执行单（179.5秒版）",
        "",
        f"- 时间基准：{fps} fps，{total_frames} 帧，{total_frames / fps:.1f} 秒。",
        "- 不生成AI配音；先按字幕时间窗录制干声，再在 Resolve 的 A1 轨逐句替换。",
        f"- 总口播字符：{total_chars}；有台词时间窗：{voiced_seconds:.1f} 秒。",
        f"- 屏幕字幕：{len(subtitle_rows)} 条；超过4字的标点断点独立成条。",
        "- 含内部标点的字幕最多9个字符；不含内部标点的字幕最多16个字符。",
        "- 建议基准：科学术语 2.8—3.5 字符/秒，普通叙述 3.5—4.3 字符/秒；表中已为转场和停连预留空间。",
        "- 字幕样式：思源黑体/同类无衬线体，白色，重点术语沿用项目语义色；最多两行，位于底部安全区。",
        "",
        "| 编号 | 时间窗 | 字符/秒 | 台词 | 配音提示 |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['编号']} | {row['开始']}—{row['结束']} | {row['字符每秒']} | {row['台词']} | {row['人工配音提示']} |"
        )
    report_lines.extend(
        [
            "",
            "## 录音交付规范",
            "",
            "- 48 kHz、24 bit、单声道 WAV；不要降噪到出现水声。",
            "- 每条单独导出，文件名使用 `VO01.wav` 至 `VO23.wav`。",
            "- 开头保留约0.15秒环境底噪，结尾保留约0.25秒，便于后期交叉淡化。",
            "- 数学读法：V读英文字母V，V₀读“V零”，W读“double-u”，NAND逐字母读，倏逝读“shū shì”。",
        ]
    )
    (REPORT_DIR / "人工配音与字幕执行单_179_5s.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    comparison_lines = [
        "# 原版脚本与修改后字幕对照（179.5秒版）",
        "",
        "- 原版：23段人工配音台词。",
        f"- 修改后：{len(subtitle_rows)}条屏幕字幕；台词文字和顺序不变，仅重新断句与分配显示时间。",
        "- 断句规则：超过4字的标点断点独立成条；含内部标点最多9个字符；不含内部标点最多16个字符。",
        "",
        "| 配音段与时间窗 | 原版脚本 | 修改后字幕 |",
        "|---|---|---|",
    ]
    for cue in plan["narration"]:
        cue_rows = [row for row in subtitle_rows if row["配音段"] == cue["id"]]
        revised = "<br>".join(
            f"{row['字幕编号']} `{row['开始']}—{row['结束']}`　{row['字幕']}"
            for row in cue_rows
        )
        original = str(cue["text"]).replace("|", "\\|")
        revised = revised.replace("|", "\\|")
        comparison_lines.append(
            f"| **{cue['id']}**<br>`{timecode(int(cue['start']), fps)}—{timecode(int(cue['end']), fps)}` "
            f"| {original} | {revised} |"
        )
    comparison_path = REPORT_DIR / "原版脚本与修改后字幕对照_179_5s.md"
    comparison_path.write_text("\n".join(comparison_lines) + "\n", encoding="utf-8")

    marker_rows: dict[int, dict[str, object]] = {}
    for marker in plan["chapter_markers"]:
        marker_rows[int(marker["frame"])] = {
            "frame": int(marker["frame"]),
            "color": marker["color"],
            "name": marker["name"],
            "note": "章节起点",
            "duration": 1,
            "custom_data": f"chapter:{marker['frame']}",
        }
    for cue in plan["narration"]:
        frame = int(cue["start"])
        duration = int(cue["end"]) - frame
        cue_note = f"{cue['id']}｜{cue['text']}｜{cue['direction']}"
        if frame in marker_rows:
            marker_rows[frame]["note"] = f"{marker_rows[frame]['note']}\n{cue_note}"
            marker_rows[frame]["duration"] = duration
            marker_rows[frame]["custom_data"] = f"chapter+voice:{cue['id']}"
        else:
            marker_rows[frame] = {
                "frame": frame,
                "color": "Yellow",
                "name": cue["id"],
                "note": cue_note,
                "duration": duration,
                "custom_data": f"voice:{cue['id']}",
            }
    marker_batch = [
        {"tool": "timeline_markers", "arguments": {"action": "add", "params": marker}}
        for _, marker in sorted(marker_rows.items())
    ]
    marker_batch_path = ROOT / "resolve_edit" / "resolve_markers_batch.json"
    marker_batch_path.write_text(
        json.dumps(marker_batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "srt": str(srt_path),
        "csv": str(csv_path),
        "subtitle_csv": str(subtitle_csv_path),
        "report": str(REPORT_DIR / "人工配音与字幕执行单_179_5s.md"),
        "comparison": str(comparison_path),
        "total_frames": total_frames,
        "duration_seconds": total_frames / fps,
        "total_spoken_chars": total_chars,
        "subtitle_cue_count": len(subtitle_rows),
        "resolve_marker_batch": str(marker_batch_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
