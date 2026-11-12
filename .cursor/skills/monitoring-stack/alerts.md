# Формулы алертов

Имена и `for` зафиксированы. Менять только вместе с `docs/DECISIONS.md`.

CPU, доля не-idle за 5 минут, в процентах:

```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
```

Память. `MemAvailable` уже вычитает кэш, который ядро может отдать:

```promql
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
```

Диск. Корень и обычные ФС. `tmpfs` и `overlay` пропускаем: они не диск VPS.

```promql
(
  1 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}
      / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"}
) * 100 > 85
```

Нагрузка. `load1` сравниваем с числом ядер того же инстанса:

```promql
node_load1 > count by (instance) (node_cpu_seconds_total{mode="idle"})
```

Сервер недоступен — цель не отвечает на scrape:

```promql
up == 0
```

У каждого алерта лейблы `severity` (`critical` для InstanceDown и HighDisk, `warning` для остальных) и `summary` на русском.
