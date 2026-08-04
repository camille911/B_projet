"""Fail CI when the B candidate bypasses the documented reuse boundary."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
CHAIN_TEST = ROOT / "tests" / "test_reuse_call_chain.py"
PROJECT = ROOT / "pyproject.toml"
FORBIDDEN_SOURCE_MARKERS = (
    "import hmac",
    "from hmac",
    "import hashlib",
    "from hashlib",
    "hmac.new",
    "hashlib.sha256",
)


def tracked_paths() -> list[str]:
    output = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in output.splitlines() if line]


def main() -> int:
    failures: list[str] = []
    if not CHAIN_TEST.is_file():
        failures.append("tests/test_reuse_call_chain.py is required")

    project = PROJECT.read_text(encoding="utf-8")
    if "company-shared-api==0.1.0" not in project:
        failures.append("pyproject.toml must pin company-shared-api==0.1.0")

    for path in SOURCE.rglob("*.py"):
        content = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_SOURCE_MARKERS:
            if marker in content:
                failures.append(f"{path.relative_to(ROOT)} contains forbidden marker: {marker}")

    generated = [path for path in tracked_paths() if "__pycache__" in path or path.endswith((".pyc", ".pyo"))]
    if generated:
        failures.append("generated Python files are tracked: " + ", ".join(generated))

    if failures:
        print("Remote white-box boundary check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Remote white-box boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
