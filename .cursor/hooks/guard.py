#!/usr/bin/env python3
"""Останавливает команды, которые светят токен или коммитят .env.

Читает JSON из stdin (поле command) и пишет JSON в stdout.
Разрешения: allow, ask, deny. При любой своей ошибке выходит с кодом 2,
чтобы failClosed в hooks.json не пропустил команду молча.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOKEN = re.compile(r"\d{6,}:[A-Za-z0-9_-]{20,}")
GIT_ADD = re.compile(r"(?:^|[\s;&|])git\s+add\b")
ENV_FILE = re.compile(r"(?:^|[\s\"'])\.env(?!\.example)\b")
RENDERED = re.compile(r"alertmanager[/\\]alertmanager\.yml(?!\.tmpl)\b")
GIT_ADD_BROAD = re.compile(r"git\s+add\s+(?:-A|--all|\.)(?:\s|$)")
DOCKER = re.compile(r"\bdocker(?:\.exe)?\b|\bdocker-compose\b", re.IGNORECASE)


def emit(permission: str, message: str = "") -> None:
    payload: dict[str, str] = {"permission": permission}
    if message:
        payload["user_message"] = message
        payload["agent_message"] = message
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        emit("deny", "Хук не разобрал команду. Повтори её отдельно, без секретов.")
        return

    command = str(data.get("command") or "")

    if TOKEN.search(command):
        emit(
            "deny",
            "В команде похоже на токен Telegram. Убери секрет и читай его из .env на VPS.",
        )
        return

    if GIT_ADD.search(command) and ENV_FILE.search(command):
        emit("deny", "Файл .env в git не добавляем. В репозитории только .env.example.")
        return

    if GIT_ADD.search(command) and RENDERED.search(command):
        emit(
            "deny",
            "alertmanager/alertmanager.yml собран из .env и содержит токен. В git только шаблон.",
        )
        return

    secret_files = Path(".env").exists() or Path("alertmanager/alertmanager.yml").is_file()
    if GIT_ADD_BROAD.search(command) and secret_files:
        emit(
            "deny",
            "Широкий git add запрещён: рядом лежит .env или собранный alertmanager.yml с токеном.",
        )
        return

    if DOCKER.search(command):
        emit(
            "ask",
            "Docker на этом компьютере не работает. Эту команду нужно запускать на VPS Debian 12.",
        )
        return

    emit("allow")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.stderr.write("guard.py: unexpected error\n")
        sys.exit(2)
