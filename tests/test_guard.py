"""Хук должен останавливать команды с токеном и git add секретов."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / ".cursor" / "hooks" / "guard.py"


def fake_token() -> str:
    return "123456789:" + ("A" * 32)


def run_guard(command: str, cwd: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps({"command": command}),
        text=True,
        capture_output=True,
        cwd=cwd,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return json.loads(result.stdout)


class GuardTest(unittest.TestCase):
    def test_allows_plain_git_status(self) -> None:
        self.assertEqual(run_guard("git status")["permission"], "allow")

    def test_denies_token_in_command(self) -> None:
        decision = run_guard(f"echo {fake_token()}")
        self.assertEqual(decision["permission"], "deny")

    def test_denies_git_add_env_but_allows_example(self) -> None:
        self.assertEqual(run_guard("git add .env")["permission"], "deny")
        self.assertEqual(run_guard("git add .env.example")["permission"], "allow")

    def test_denies_rendered_alertmanager_config(self) -> None:
        decision = run_guard("git add alertmanager/alertmanager.yml")
        self.assertEqual(decision["permission"], "deny")
        self.assertEqual(
            run_guard("git add alertmanager/alertmanager.yml.tmpl")["permission"],
            "allow",
        )

    def test_asks_before_docker(self) -> None:
        self.assertEqual(run_guard("docker compose up -d")["permission"], "ask")

    def test_denies_broad_add_when_env_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("TELEGRAM_BOT_TOKEN=\n", encoding="utf-8")
            self.assertEqual(run_guard("git add -A", root)["permission"], "deny")
            self.assertEqual(run_guard("git status", root)["permission"], "allow")
