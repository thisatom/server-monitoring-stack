---
name: monitoring-stack
description: >-
  Собирает учебный мониторинг VPS (Prometheus, node_exporter, Grafana,
  Alertmanager, Telegram) в этом репозитории. Use when editing docker-compose,
  prometheus.yml, alert rules, Alertmanager, Grafana provisioning, the stress
  demo, or docs about alerts, SSH tunnel, and Telegram.
---

# Стек мониторинга

Читай `docs/DECISIONS.md` до правок. Объясняй каждый шаг простым русским.

## Порядок файлов

Не пиши следующий, пока предыдущий не лежит в репозитории:

1. `docker-compose.yml`
2. `prometheus/prometheus.yml`
3. `prometheus/alert.rules.yml`
4. `alertmanager/alertmanager.yml.tmpl` (переменные из `.env`)
5. `grafana/provisioning/` и JSON дашборда
6. `scripts/stress-demo.sh`
7. Разделы README: запуск, проверка, скриншот

## Жёсткие правила

- Порты UI только на `127.0.0.1`. `node_exporter` без проброса на хост.
- Образы с фиксированным тегом, не `latest`.
- Токен и chat_id только как `${TELEGRAM_BOT_TOKEN}` и `${TELEGRAM_CHAT_ID}`.
- Алерты и пороги — таблица в `.cursor/rules/alerts.mdc`. Не выдумывай шестой алерт.
- Проверку `docker compose` делай на VPS. Локальный Docker не предлагай.
- Скриншот дашборда клади в `docs/images/` и вставляй в README только после реального прогона. Не рисуй фейковый.

## Доступ

С ноутбука:

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 -L 9093:127.0.0.1:9093 user@vps
```

Потом в браузере: Grafana `http://127.0.0.1:3000`, Prometheus `http://127.0.0.1:9090`, Alertmanager `http://127.0.0.1:9093`.

## Проверка на VPS

```bash
docker compose config
docker compose up -d
docker compose ps
curl -s http://127.0.0.1:9090/api/v1/targets
curl -s http://127.0.0.1:9093/api/v2/status
```

Цель зелёная, правила загружены (`/api/v1/rules`), тестовый алерт доходит в Telegram после `scripts/stress-demo.sh`.

## Дополнительно

Пороги и формулы: [alerts.md](alerts.md).
