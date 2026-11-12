#!/usr/bin/env python3
"""Собирает alertmanager.yml из шаблона и .env. Токен на экран не печатает."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("MONITORING_ROOT", Path(__file__).resolve().parents[1]))
ENV_PATH = ROOT / ".env"
TEMPLATE = ROOT / "alertmanager" / "alertmanager.yml.tmpl"
OUTPUT = ROOT / "alertmanager" / "alertmanager.yml"

TOKEN_PLACEHOLDER = "__TELEGRAM_BOT_TOKEN__"
CHAT_PLACEHOLDER = "__TELEGRAM_CHAT_ID__"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def main() -> None:
    if not ENV_PATH.is_file():
        fail("Нет файла .env. Скопируй .env.example и впиши токен, chat_id и пароль Grafana.")
    if not TEMPLATE.is_file():
        fail(f"Нет шаблона {TEMPLATE}")
    if OUTPUT.exists() and not OUTPUT.is_file():
        fail(
            "alertmanager/alertmanager.yml — каталог, а не файл. "
            "Так бывает, если Docker уже запускали без конфига. Удали каталог и запусти скрипт снова."
        )

    env = load_env(ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or token == "changeme":
        fail("В .env пустой TELEGRAM_BOT_TOKEN.")
    if any(char in token for char in "\r\n\"'"):
        fail("TELEGRAM_BOT_TOKEN не должен содержать кавычки или перевод строки.")
    if not chat_id or chat_id == "0" or chat_id in {"+", "-"}:
        fail("В .env пустой TELEGRAM_CHAT_ID.")
    digits = chat_id[1:] if chat_id.startswith("-") else chat_id
    if not digits.isdigit():
        fail("TELEGRAM_CHAT_ID должен быть целым числом, для группы — отрицательным.")

    rendered = TEMPLATE.read_text(encoding="utf-8")
    rendered = rendered.replace(TOKEN_PLACEHOLDER, token)
    rendered = rendered.replace(CHAT_PLACEHOLDER, chat_id)
    if TOKEN_PLACEHOLDER in rendered or CHAT_PLACEHOLDER in rendered:
        fail("В шаблоне остались плейсхолдеры. Файл не записан.")

    OUTPUT.write_text(rendered, encoding="utf-8")
    try:
        OUTPUT.chmod(0o600)
    except OSError:
        pass
    print("Записал alertmanager/alertmanager.yml. В git его не добавляй: внутри токен.")


if __name__ == "__main__":
    main()
