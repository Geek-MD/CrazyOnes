"""Tests for the Docker entrypoint configuration."""

import json
import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_entrypoint_reads_version_from_pyproject(tmp_path: Path) -> None:
    """The generated Docker config uses the package's canonical version."""
    env = os.environ.copy()
    env.update(
        {
            "CRAZYONES_APP_HOME": str(tmp_path),
            "CRAZYONES_LOG_FILE": str(tmp_path / "crazyones.log"),
            "TELEGRAM_BOT_TOKEN": "123456789:real-token-for-entrypoint-test",
        }
    )
    env.pop("CRAZYONES_VERSION", None)

    subprocess.run(
        ["bash", str(PROJECT_ROOT / "docker-entrypoint.sh"), "true"],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    config = json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))
    metadata = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(
        r'(?ms)^\[project\]\s*$.*?^version\s*=\s*"([^"]+)"',
        metadata,
    )
    assert version_match is not None
    assert config["version"] == version_match.group(1)
