# План

Собрать на VPS (Debian 12) мониторинг самого этого сервера и показывать его в портфолио: метрики, дашборд, алерт в Telegram.

Docker на компьютере автора не используем. Файлы пишем здесь, команды запуска выполняются на сервере.

## Что уже решено

- Доставка интерфейсов: SSH-туннель, порты только на `127.0.0.1`. Nginx не ставим. Причина в `docs/DECISIONS.md`.
- Канал алертов: встроенный `telegram_configs` Alertmanager. Токен и chat_id из `.env`.
- Пять алертов: сервер недоступен, CPU, RAM, диск, нагрузка. Пороги тоже в `docs/DECISIONS.md`.
- Дашборд Grafana поднимается сам из файлов provisioning, без кликов в UI.
- Нагрузку для демо даёт `stress-ng` на VPS, отдельным скриптом.

## Структура, когда стек будет собран

```
server-monitoring-stack/
├── .cursor/                 # правила, хук, навык (уже есть)
├── .env.example
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── docs/
│   ├── PLAN.md
│   ├── DECISIONS.md
│   ├── SECURITY.md
│   └── images/              # скриншот дашборда после проверки на VPS
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   └── alert.rules.yml
├── alertmanager/
│   └── alertmanager.yml.tmpl
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       └── dashboards/
├── scripts/
│   └── stress-demo.sh
```

Конфиги стека уже в репозитории. Не хватает прогона на VPS: адреса сервера в проекте нет, скриншот дашборда снять не с чего.

## Порядок, один файл за шаг

1. `docker-compose.yml` — четыре сервиса, сеть, тома, порты на localhost.
2. `prometheus/prometheus.yml` — кого скрейпить и куда слать алерты.
3. `prometheus/alert.rules.yml` — пять правил.
4. Шаблон Alertmanager и способ подставить `.env` при старте.
5. Provisioning Grafana и дашборд node_exporter.
6. `scripts/stress-demo.sh` — как искусственно нагрузить сервер.
7. README: как запустить, как проверить, скриншот с VPS.

## Как потом открывать UI

На ноутбуке, пока сессия SSH жива:

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 -L 9093:127.0.0.1:9093 user@vps
```

- Grafana: http://127.0.0.1:3000
- Prometheus: http://127.0.0.1:9090
- Alertmanager: http://127.0.0.1:9093

## Чеклист фундамента

- [x] Решение по доступу записано
- [x] Пороги алертов записаны
- [x] `.env.example` и `.gitignore`
- [x] Правила Cursor, хук, навык, AGENTS.md, CLAUDE.md
- [x] `docker-compose.yml`
- [x] Конфиг Prometheus и правила
- [x] Alertmanager → Telegram (шаблон и скрипт подстановки)
- [x] Grafana provisioning
- [x] Скрипт stress-ng
- [ ] Прогон на VPS и скриншот в README
