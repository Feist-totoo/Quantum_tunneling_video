"""Auditable DeepSeek text worker for the quantum-tunneling video project."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONFIG_PATH = HERE / "config.json"
KEY_PATH = HERE / "DEEPSEEK_API_KEY.txt"
SYSTEM_PATH = HERE / "system_prompt.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_key() -> str:
    key = KEY_PATH.read_text(encoding="utf-8").strip()
    if not key or key == "PASTE_YOUR_DEEPSEEK_API_KEY_HERE":
        raise RuntimeError(f"请先在 {KEY_PATH} 填写 DeepSeek API Key")
    return key


def client_and_config():
    config = load_json(CONFIG_PATH)
    client = OpenAI(api_key=load_key(), base_url=config["base_url"])
    return client, config


def doctor() -> int:
    config = load_json(CONFIG_PATH)
    assert config["model"] == "deepseek-v4-flash"
    assert SYSTEM_PATH.exists() and KEY_PATH.exists()
    status = {
        "python": sys.version.split()[0],
        "config_valid": True,
        "model": config["model"],
        "key_configured": KEY_PATH.read_text(encoding="utf-8").strip()
        not in ("", "PASTE_YOUR_DEEPSEEK_API_KEY_HERE"),
        "workflow_boundary": "text_only",
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


def verify_model(client: OpenAI, model: str):
    available = {item.id for item in client.models.list().data}
    if model not in available:
        raise RuntimeError(f"账号当前不可用模型 {model}；可见模型：{sorted(available)}")


def load_task(path: Path, config: dict):
    task = load_json(path)
    task_type = task.get("task_type")
    if task_type not in config["allowed_tasks"]:
        raise ValueError(f"任务类型不在允许列表：{task_type}")
    documents = []
    for relative in task.get("inputs", []):
        source = (ROOT / relative).resolve()
        if ROOT not in source.parents and source != ROOT:
            raise ValueError(f"输入越出项目目录：{source}")
        if not source.is_file():
            raise FileNotFoundError(source)
        if source.suffix.lower() not in {".md", ".txt", ".json", ".csv", ".py"}:
            raise ValueError(f"工作流只接受文本输入：{source}")
        documents.append({"path": relative, "content": source.read_text(encoding="utf-8")})
    return task, documents


def call(task_path: Path, is_smoke=False):
    client, config = client_and_config()
    verify_model(client, config["model"])
    if is_smoke:
        task = {"task_type": "qa_checklist", "objective": "返回工作流连通性测试结果"}
        documents = []
    else:
        task, documents = load_task(task_path, config)
    payload = {"task": task, "documents": documents}
    messages = [
        {"role": "system", "content": SYSTEM_PATH.read_text(encoding="utf-8")},
        {"role": "user", "content": "请按指定结构输出 json：\n" + json.dumps(payload, ensure_ascii=False)},
    ]

    def request_once(thinking):
        return client.chat.completions.create(
            model=config["model"], messages=messages,
            response_format={"type": "json_object"},
            temperature=config["temperature"],
            max_tokens=2400 if is_smoke else config["max_tokens"],
            extra_body={"thinking": thinking, "user_id": config["user_id"]},
        )

    # The official JSON-mode documentation notes that an empty content field
    # can occasionally occur. Smoke tests use non-thinking mode, and any empty
    # result gets one identical retry without exposing the credential.
    thinking = {"type": "disabled"} if is_smoke else config["thinking"]
    response = request_once(thinking)
    content = response.choices[0].message.content or ""
    if not content.strip():
        response = request_once(thinking)
        content = response.choices[0].message.content or ""
    if not content.strip():
        raise RuntimeError("DeepSeek 官方接口连续两次返回空内容")
    parsed = json.loads(content)
    required = {"summary", "deliverables", "issues", "uncertainties", "recommended_codex_checks"}
    missing = sorted(required - set(parsed))
    if missing:
        raise ValueError(f"响应缺少字段：{missing}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = HERE / "runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "response.txt").write_text(content, encoding="utf-8")
    (run_dir / "result.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {
        "timestamp_utc": stamp,
        "model_requested": config["model"],
        "model_returned": response.model,
        "task_type": task["task_type"],
        "usage": response.usage.model_dump() if response.usage else None,
        "codex_review_status": "pending",
    }
    (run_dir / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "run_dir": str(run_dir), "audit": audit}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("smoke-test")
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--task", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        raise SystemExit(doctor())
    if args.command == "smoke-test":
        call(HERE / "tasks" / "example_script_analysis.json", is_smoke=True)
    else:
        call(args.task.resolve())


if __name__ == "__main__":
    main()
