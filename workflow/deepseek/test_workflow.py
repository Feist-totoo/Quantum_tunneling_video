import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_doctor_without_secret():
    result = subprocess.run(
        [sys.executable, str(HERE / "deepseek_worker.py"), "doctor"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    payload = json.loads(result.stdout)
    assert payload["config_valid"] is True
    assert payload["model"] == "deepseek-v4-flash"
    assert payload["workflow_boundary"] == "text_only"


if __name__ == "__main__":
    test_doctor_without_secret()
    print("workflow self-test: PASS")
