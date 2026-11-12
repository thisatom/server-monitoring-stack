# CLAUDE.md

Канон для любого агента в этом репозитории — [AGENTS.md](AGENTS.md). Здесь то же самое короче, чтобы файл находился и Claude Code.

- Учебный мониторинг VPS: Prometheus, node_exporter, Grafana, Alertmanager, Telegram.
- Пиши по-русски, один файл за шаг, по порядку из [docs/PLAN.md](docs/PLAN.md).
- Решения не пересматривай молча: [docs/DECISIONS.md](docs/DECISIONS.md).
- Секреты только в `.env` на сервере. Хук `.cursor/hooks/guard.py` режет команды с токеном и `git add .env`.
- UI слушает `127.0.0.1`. С ноутбука заходи SSH-туннелем. Docker запускай на Debian 12, не на Windows-машине автора.
- Навык агента: `.cursor/skills/monitoring-stack/SKILL.md`.
