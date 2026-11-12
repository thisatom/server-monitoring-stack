# Секреты и сеть

## Что считается секретом

- `TELEGRAM_BOT_TOKEN` — токен от @BotFather
- `TELEGRAM_CHAT_ID` — id чата, куда писать
- `GF_SECURITY_ADMIN_PASSWORD` — пароль входа в Grafana

Они лежат в файле `.env` на VPS. Файл в `.gitignore`. В репозиторий кладём только `.env.example` с пустыми значениями.

Alertmanager сам переменные из `.env` не читает. На сервере скрипт `scripts/render-alertmanager.py` подставляет токен и chat_id в `alertmanager/alertmanager.yml.tmpl` и записывает `alertmanager/alertmanager.yml`. Готовый файл тоже в `.gitignore`: в нём уже настоящий токен.

Не присылай токен в чат. Если он уже засветился, в @BotFather отзови его командой `/revoke` и выпусти новый.

## Как завести бота

1. В Telegram открой @BotFather.
2. Команда `/newbot`, имя и username. В ответ придёт токен. Его сразу в `.env` на сервере, не в файл проекта.
3. Напиши своему боту любое сообщение, иначе он не сможет писать первым.
4. Узнай chat_id. На сервере, после того как токен уже в `.env` и не светится в истории shell:

```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

В ответе поле `chat.id` — это `TELEGRAM_CHAT_ID`. Для лички id положительный, для группы часто отрицательный.

## Куда можно ходить по сети

| Куда | Кто | Зачем |
|---|---|---|
| исходящий HTTPS к `api.telegram.org` | Alertmanager | доставить алерт |
| сеть Docker `monitoring` | Prometheus → node_exporter и Alertmanager | сбор метрик и отправка алертов |
| `127.0.0.1` на VPS, порты 3000, 9090, 9093 | только ты, через SSH-туннель | открыть UI |

Входящие порты стека в файрволе наружу не открываем.

## Хук

`.cursor/hooks/guard.py` срабатывает перед командой в терминале агента:

- команда с куском, похожим на токен бота, — запрет;
- `git add .env` или `git add alertmanager/alertmanager.yml` — запрет;
- широкий `git add`, если рядом лежит `.env` или собранный конфиг с токеном, — запрет;
- команда с `docker` — вопрос, потому что запускать её нужно на VPS, не на Windows.
