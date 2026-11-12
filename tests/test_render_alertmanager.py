"""Скрипт подстановки токена не должен светить секрет и портить чужой .env."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render-alertmanager.py"
TEMPLATE = ROOT / "alertmanager" / "alertmanager.yml.tmpl"


def fake_token() -> str:
    return "123456789:" + ("A" * 32)


def run_render(root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MONITORING_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )


class RenderAlertmanagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        destination = self.tmp / "alertmanager"
        destination.mkdir()
        shutil.copy(TEMPLATE, destination / "alertmanager.yml.tmpl")

    def write_env(self, chat_id: str, token: str | None = None) -> None:
        (self.tmp / ".env").write_text(
            "\n".join(
                [
                    f"TELEGRAM_BOT_TOKEN={fake_token() if token is None else token}",
                    f"TELEGRAM_CHAT_ID={chat_id}",
                    "GF_SECURITY_ADMIN_PASSWORD=ci-only-password",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_missing_env_fails(self) -> None:
        result = run_render(self.tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn(".env", result.stderr)

    def test_rejects_empty_chat_id(self) -> None:
        self.write_env("0")
        result = run_render(self.tmp)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.tmp / "alertmanager" / "alertmanager.yml").exists())

    def test_writes_config_without_printing_token(self) -> None:
        token = fake_token()
        self.write_env("-100123", token)
        result = run_render(self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        rendered = (self.tmp / "alertmanager" / "alertmanager.yml").read_text(encoding="utf-8")
        self.assertIn(token, rendered)
        self.assertIn("chat_id: -100123", rendered)
        self.assertNotIn("__TELEGRAM_", rendered)
        self.assertNotIn(token, result.stdout)
        self.assertNotIn(token, result.stderr)

    def test_refuses_directory_left_by_docker(self) -> None:
        self.write_env("-100123")
        output = self.tmp / "alertmanager" / "alertmanager.yml"
        output.mkdir()
        result = run_render(self.tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("каталог", result.stderr)
