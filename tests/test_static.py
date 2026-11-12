"""Проверяет файлы репозитория без Docker и без секретов."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\d{6,}:[A-Za-z0-9_-]{20,}")
ALERTS = {
    "InstanceDown": "1m",
    "HighCpu": "5m",
    "HighMemory": "5m",
    "HighDisk": "10m",
    "HighLoad": "5m",
}


class StaticConfigTest(unittest.TestCase):
    def test_repository_has_no_bot_token(self) -> None:
        leaked: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if TOKEN.search(text):
                leaked.append(str(path.relative_to(ROOT)))
        self.assertEqual(leaked, [])

    def test_compose_binds_ui_to_localhost_and_pins_images(self) -> None:
        text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("127.0.0.1:3000:3000", text)
        self.assertIn("127.0.0.1:9090:9090", text)
        self.assertIn("127.0.0.1:9093:9093", text)
        self.assertNotIn("9100", text)
        self.assertNotRegex(text, r"image:\s+\S+:latest\b")
        self.assertNotIn("env_file:", text)

    def test_prometheus_scrapes_node_and_loads_rules(self) -> None:
        text = (ROOT / "prometheus" / "prometheus.yml").read_text(encoding="utf-8")
        self.assertIn("alert.rules.yml", text)
        self.assertIn("node-exporter:9100", text)
        self.assertIn("alertmanager:9093", text)

    def test_alert_names_and_waits(self) -> None:
        text = (ROOT / "prometheus" / "alert.rules.yml").read_text(encoding="utf-8")
        for name, wait in ALERTS.items():
            self.assertIn(f"alert: {name}", text)
            self.assertRegex(text, rf"alert: {name}\b[\s\S]*?\bfor: {wait}\b")

    def test_template_has_placeholders_only(self) -> None:
        text = (ROOT / "alertmanager" / "alertmanager.yml.tmpl").read_text(encoding="utf-8")
        self.assertIn("__TELEGRAM_BOT_TOKEN__", text)
        self.assertIn("__TELEGRAM_CHAT_ID__", text)
        self.assertIn("telegram_configs:", text)

    def test_gitignore_covers_secrets(self) -> None:
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", text)
        self.assertIn("alertmanager/alertmanager.yml", text)

    def test_grafana_dashboard_uses_prometheus(self) -> None:
        datasource = (ROOT / "grafana" / "provisioning" / "datasources" / "prometheus.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("http://prometheus:9090", datasource)
        dashboard = json.loads(
            (ROOT / "grafana" / "provisioning" / "dashboards" / "json" / "vps.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(dashboard["uid"], "vps-node")
        self.assertGreaterEqual(len(dashboard["panels"]), 5)
        self.assertTrue(
            all(panel["datasource"]["uid"] == "prometheus" for panel in dashboard["panels"])
        )
