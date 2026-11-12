#!/bin/sh
# Проверки, которым нужен Docker. Их запускает GitHub Actions, не ноутбук.
# Фиктивный токен собирается в памяти и в репозиторий не пишется.

set -eu
cd "$(dirname "$0")/.."

token="123456789:$(python3 -c 'print("A"*32)')"
password="ci-only-password"

umask 077
cat > .env << EOF
TELEGRAM_BOT_TOKEN=${token}
TELEGRAM_CHAT_ID=-100123
GF_SECURITY_ADMIN_PASSWORD=${password}
EOF

cleanup() {
  rm -f .env alertmanager/alertmanager.yml
}
trap cleanup EXIT

python3 scripts/render-alertmanager.py
sh -n scripts/stress-demo.sh

docker run --rm --entrypoint promtool \
  -v "$PWD/prometheus:/prometheus:ro" \
  prom/prometheus:v3.16.0 \
  check config /prometheus/prometheus.yml

docker run --rm --entrypoint amtool \
  -v "$PWD/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro" \
  prom/alertmanager:v0.35.0 \
  check-config /etc/alertmanager/alertmanager.yml

docker compose config >/dev/null
