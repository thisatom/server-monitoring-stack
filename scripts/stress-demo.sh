#!/bin/sh
# Искусственная нагрузка CPU, чтобы сработал алерт HighCpu.
# Запускать на VPS, не на ноутбуке. Сервер на это время будет тормозить.

set -eu

if ! command -v stress-ng >/dev/null 2>&1; then
  echo "Нет программы stress-ng."
  echo "Установи её на Debian 12 и запусти скрипт снова:"
  echo "  sudo apt-get update && sudo apt-get install -y stress-ng"
  exit 1
fi

# 12 минут: формула смотрит среднее за 5 минут, затем Prometheus ждёт ещё 5 минут.
DURATION="${1:-12m}"

echo "Гружу все ядра ${DURATION}."
echo "Жди сообщение HighCpu в Telegram. Раньше времени алерт не придёт."
echo "Остановить нагрузку: Ctrl+C. После этого придёт «ПОЧИНИЛОСЬ»."

exec stress-ng --cpu 0 --timeout "${DURATION}" --metrics-brief
