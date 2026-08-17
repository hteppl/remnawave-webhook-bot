<img src="https://raw.githubusercontent.com/hteppl/remnawave-webhook-bot/master/.github/images/logo.webp" alt="remnawave-webhook-bot" width="800px">

## remnawave-webhook-bot

[English](https://github.com/hteppl/remnawave-webhook-bot/blob/master/README.md) | **Русский**

[![Release](https://img.shields.io/github/v/release/hteppl/remnawave-webhook-bot?logo=github&logoColor=white&label=release)](https://github.com/hteppl/remnawave-webhook-bot/releases/latest)
[![Docker Image](https://img.shields.io/docker/v/hteppl/remnawave-webhook-bot?logo=docker&logoColor=white&label=docker)](https://hub.docker.com/r/hteppl/remnawave-webhook-bot)
[![CI](https://github.com/hteppl/remnawave-webhook-bot/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/hteppl/remnawave-webhook-bot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg?logo=python&logoColor=white)](https://github.com/hteppl/remnawave-webhook-bot/blob/master/pyproject.toml)
[![License: GPL v3](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](https://github.com/hteppl/remnawave-webhook-bot/blob/master/LICENSE)

Система уведомлений о состояниях и изменениях данных в панелях Remnawave.

## 📋 Возможности

- Установка как рядом с панелью Remnawave, так и на отдельном сервере
- Поддержка топиков Telegram для разделения типов событий
- Настройка текстов, форматирования и перечня обрабатываемых событий
- Периодические отчеты о состоянии инфраструктуры
- Уведомления о входах в панель и о неудачных попытках авторизации
- Дополнительные обработчики данных, включая сбор метрик событий
- Проверка подлинности входящих запросов по заголовкам безопасности Remnawave

## 🚀 Установка

### Требования

- Сервер с установленной подсистемой Docker: с панелью Remnawave либо отдельный

### Шаг 1: Размещение файлов на сервере

На сервере с панелью рекомендуется использовать директорию `/opt/remnawave/webhook`.

В продакшн-сценариях применяется готовый образ, копирование исходного кода на сервер не требуется.
Достаточно двух файлов: `docker-compose.yml` и `.env`.

Варианты конфигурации compose:

| Файл в репозитории            | Назначение                            | Особенности                                                      |
| ----------------------------- | ------------------------------------- | ---------------------------------------------------------------- |
| `docker-compose.prod.yml`     | Сервер с панелью Remnawave            | Готовый образ, сеть `remnawave-network`, порт не публикуется     |
| `docker-compose.external.yml` | Отдельный (внешний) сервер без панели | Готовый образ, сеть `remnawave-webhook-bot`, порт не публикуется |
| `docker-compose.dev.yml`      | Разработка                            | Сборка из исходников, монтирование `./src` и `./locales`         |

Создайте на сервере файл `docker-compose.yml` и перенесите в него содержимое выбранного варианта. Все дальнейшие
команды выполняются стандартным `docker compose`:

```bash
cd /opt/remnawave/webhook && sudo nano docker-compose.yml
```

### Шаг 2: Настройка конфигурации

Создайте файл `.env` рядом с `docker-compose.yml` и перенесите в него содержимое `.env.example`:

```bash
cd /opt/remnawave/webhook && sudo nano .env
```

Обратите внимание:

- Чат следует преобразовать в супергруппу с топиками до добавления бота, иначе сервис
  https://t.me/username_to_id_bot вернет некорректный идентификатор чата.
- Значение `WEBHOOK_SECRET_HEADER` берется из окружения Remnawave: `sudo nano /opt/remnawave/.env`.

В нижней части конфигурации размещены параметры фильтрации обрабатываемых событий. Перечень событий приведен
в разделе «Поддерживаемые события», а также в документации https://docs.rw/docs/features/webhooks.

```dotenv
# Настройки бота Telegram
# Чтобы получить айди чата можно использовать: https://t.me/username_to_id_bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Настройка топиков Telegram для посылки уведомлений
# Чтобы получить айди топика - скопируйте ссылку на сообщение.
# Пример: https://t.me/c/123123123/[2]/21 - 2 это и есть айди топика.

# Пользователи: создан, изменен, продлен, истек, лимит трафика
TOPIC_USER=
# Ноды: создана, включена/выключена, потеря/восстановление связи, трафик
TOPIC_NODE=
# Сервис: запуск панели, входы в панель, API-токены
TOPIC_SERVICE=
# Ошибки: превышен лимит уведомлений и прочие сбои (если пусто - используется TOPIC_SERVICE)
TOPIC_ERRORS=
# Системные статусы бота: сводки падений нод, ежедневная статистика пользователей
TOPIC_STATUS=
# Отчеты торрент-блокировщика: обнаружен торрент-трафик (если пусто - используется TOPIC_NODE)
TOPIC_TORRENT_BLOCKER=
# Устройства HWID: добавлено/удалено устройство (если пусто - используется TOPIC_USER)
TOPIC_USER_HWID_DEVICES=
# Биллинг нод: напоминания об оплате и просрочке
TOPIC_CRM=

# Настройки вебхука
WEBHOOK_SECRET_HEADER=your_webhook_secret_here
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8089
WEBHOOK_PATH=/

# Выбор языка (ru, en)
LANGUAGE=ru
LOCALES_DIR=locales

# Таймзона для отображения времени (UTC, Europe/Moscow, Europe/Samara, Asia/Yekaterinburg итд)
# Зоны: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE=Europe/Moscow

# Формат отображения времени (по умолчанию: %d.%m.%Y %H:%M:%S)
# %d.%m.%Y %H:%M:%S = 01.11.2025 23:04:10
# %Y-%m-%d %H:%M:%S = 2025-11-01 23:04:10
TIME_FORMAT="%d.%m.%Y %H:%M:%S"

# Сервис подсчета и вывода последних упавших нод (вывод в топик TOPIC_STATUS)
ENABLE_CONNECTION_LOSS_STATS=false
# Время хранения метрик падений в часах (по умолчанию: 24)
CONNECTION_LOSS_STATS_HOURS=24
# Интервал отправки отчетов о потерях соединения в часах (по умолчанию: 3)
CONNECTION_LOSS_REPORT_INTERVAL_HOURS=3

# Сервис ежедневной статистики user.created и user.first_connected пользователей (вывод в топик TOPIC_STATUS)
ENABLE_USER_DAILY_STATS=false
# Время отправки отчета в формате HH:MM (по умолчанию: 00:00)
USER_DAILY_STATS_TIME=00:00
```

## 🚀 Обновление

Обновление выполняется загрузкой актуального образа:

```bash
cd /opt/remnawave/webhook && sudo docker compose pull && sudo docker compose up -d
```

При обновлении рекомендуется сверить `.env` с актуальным `.env.example` и при необходимости
дополнить конфигурацию новыми переменными: `cd /opt/remnawave/webhook && sudo nano .env`.

## ▶️ Запуск

Все команды приведены для установки в директорию `/opt/remnawave/webhook`.

Запуск:

```bash
cd /opt/remnawave/webhook && sudo docker compose up -d
```

Перезапуск:

```shell
cd /opt/remnawave/webhook && sudo docker compose down && sudo docker compose up -d
```

Просмотр логов:

```bash
sudo docker logs remnawave-webhook-bot
```

Сборка из исходников применяется только при разработке, с конфигурацией `docker-compose.dev.yml`:

```bash
sudo docker compose up -d --build
```

## 🔐 Подключение к Remnawave

### Вариант A: обработчик на сервере с панелью

Реверс прокси и TLS не требуются. Панель и обработчик находятся в одной сети Docker
(`remnawave-network`), поэтому события передаются напрямую по внутреннему адресу, минуя внешнюю сеть.

Укажите переменные окружения панели: `sudo nano /opt/remnawave/.env`

```dotenv
### WEBHOOK ###
WEBHOOK_ENABLED=true
WEBHOOK_URL=http://remnawave-webhook-bot:8089/
WEBHOOK_SECRET_HEADER=a12m7ca8h...
```

Перезапустите Remnawave:

```bash
cd /opt/remnawave && sudo docker compose down && sudo docker compose up -d
```

Проверка работоспособности с сервера с панелью:

```bash
sudo docker exec remnawave-webhook-bot python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8089/health').read())"
```

### Вариант B: обработчик на отдельном сервере

Панель обращается к обработчику через внешнюю сеть, поэтому обязательны публичный домен, TLS
и реверс прокси. Готовые примеры конфигураций находятся в директории [examples](https://github.com/hteppl/remnawave-webhook-bot/tree/master/examples):

| Реверс прокси | Файл примера                                                 |
| ------------- | ------------------------------------------------------------ |
| Caddy         | [examples/Caddyfile](https://github.com/hteppl/remnawave-webhook-bot/blob/master/examples/Caddyfile)                     |
| nginx         | [examples/nginx.conf](https://github.com/hteppl/remnawave-webhook-bot/blob/master/examples/nginx.conf)                   |
| Traefik       | [examples/traefik-dynamic.yml](https://github.com/hteppl/remnawave-webhook-bot/blob/master/examples/traefik-dynamic.yml) |

Порт наружу не публикуется, поэтому реверс прокси должен быть запущен в Docker и подключен к сети
`remnawave-webhook-bot`: обращение выполняется по внутреннему адресу `http://remnawave-webhook-bot:8089`.
После изменения конфигурации реверс прокси соответствующий сервис необходимо перезапустить.

Проверка доступности:

```bash
curl https://webhook.your_address.com/health   # ожидается ответ OK
```

Переменные окружения панели:

```dotenv
### WEBHOOK ###
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://webhook.your_address.com/
WEBHOOK_SECRET_HEADER=a12m7ca8h...
```

Значение `WEBHOOK_SECRET_HEADER` должно совпадать в конфигурациях панели и обработчика: этим ключом
подписываются и проверяются входящие запросы.

## 🌐 Установка на внешний сервер

Сценарий: панель Remnawave размещена на одном сервере, обработчик вебхуков - на другом. Панель отправляет
события на публичный HTTPS-адрес обработчика.

**Требуется:** сервер с Docker, домен (например `webhook.your_address.com`) с A-записью на этот сервер
и реверс прокси с TLS.

1. Создайте рабочую директорию, например `/opt/webhook`, и разместите в ней `docker-compose.yml`
   с содержимым `docker-compose.external.yml` из репозитория:

   ```bash
   sudo mkdir -p /opt/webhook && cd /opt/webhook && sudo nano docker-compose.yml
   ```

2. Создайте `.env` с содержимым `.env.example` и заполните его:

   ```bash
   cd /opt/webhook && sudo nano .env
   ```

   Обязательные параметры: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` и `WEBHOOK_SECRET_HEADER`, совпадающий
   со значением в конфигурации панели. Параметры `WEBHOOK_HOST=0.0.0.0` и `WEBHOOK_PORT=8089` изменению
   не подлежат: они определяют адрес внутри контейнера.

3. Запустите сервис:

   ```bash
   cd /opt/webhook && sudo docker compose up -d
   ```

   Порт наружу не публикуется: контейнер доступен только внутри сети `remnawave-webhook-bot`.

4. Настройте реверс прокси по примерам из директории [examples](https://github.com/hteppl/remnawave-webhook-bot/tree/master/examples) и проверьте доступность:

   ```bash
   curl https://webhook.your_address.com/health   # ожидается ответ OK
   ```

5. На сервере с панелью укажите адрес обработчика и перезапустите Remnawave:

   ```dotenv
   ### WEBHOOK ###
   WEBHOOK_ENABLED=true
   WEBHOOK_URL=https://webhook.your_address.com/
   WEBHOOK_SECRET_HEADER=a12m7ca8h...
   ```

   ```bash
   cd /opt/remnawave && sudo docker compose down && sudo docker compose up -d
   ```

6. Проверьте логи: после перезапуска панели поступает событие `service.panel_started`.

   ```bash
   sudo docker logs -f remnawave-webhook-bot
   ```

### Диагностика

| Симптом                   | Причина и решение                                                                                                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `403` в логах обработчика | Значение `WEBHOOK_SECRET_HEADER` не совпадает со значением в конфигурации панели                                                                                                                      |
| `404` в логах обработчика | Путь в `WEBHOOK_URL` не соответствует `WEBHOOK_PATH` (по умолчанию `/`)                                                                                                                               |
| События не поступают      | При установке рядом с панелью - контейнеры в разных сетях Docker; при установке на отдельном сервере - панель не получает доступ к домену: проверьте DNS, TLS-сертификат и правила межсетевого экрана |

## 📊 Поддерживаемые события

### События пользователей (`user.*`)

- `user.created` - Создание пользователя
- `user.modified` - Изменение пользователя
- `user.deleted` - Удаление пользователя
- `user.disabled` - Отключение пользователя
- `user.enabled` - Включение пользователя
- `user.limited` - Ограничение пользователя
- `user.expired` - Истечение срока пользователя
- `user.revoked` - Отзыв доступа пользователя
- `user.traffic_reset` - Сброс трафика
- `user.first_connected` - Первое подключение
- `user.bandwidth_usage_threshold_reached` - Достижение лимита трафика
- `user.not_connected` - Пользователь давно не подключался (требует `NOT_CONNECTED_USERS_NOTIFICATIONS_ENABLED=true` в
  панели)
- `user.expiration` - Уведомления об истечении срока (требует `EXPIRATION_NOTIFICATIONS_ENABLED=true` в панели)

Устаревшие события, удаленные в панели v2.8.0 и замененные на `user.expiration`. Обрабатываются для совместимости
с предыдущими версиями панели:

- `user.expires_in_72_hours`, `user.expires_in_48_hours`, `user.expires_in_24_hours`, `user.expired_24_hours_ago`

### События устройств HWID (`user_hwid_devices.*`)

- `user_hwid_devices.added` - Добавлено устройство
- `user_hwid_devices.deleted` - Удалено устройство

### События узлов (`node.*`)

- `node.created` - Создание узла
- `node.modified` - Изменение узла
- `node.disabled` - Отключение узла
- `node.enabled` - Включение узла
- `node.deleted` - Удаление узла
- `node.connection_lost` - Потеря соединения
- `node.connection_restored` - Восстановление соединения
- `node.traffic_notify` - Уведомление о трафике

### Биллинг-события (`crm.infra_billing_*`)

- `crm.infra_billing_node_payment_in_7_days` - Оплата через 7 дней
- `crm.infra_billing_node_payment_in_48hrs` - Оплата через 48 часов
- `crm.infra_billing_node_payment_in_24hrs` - Оплата через 24 часа
- `crm.infra_billing_node_payment_due_today` - Оплата сегодня
- `crm.infra_billing_node_payment_overdue_24hrs` - Просрочка 24 часа
- `crm.infra_billing_node_payment_overdue_48hrs` - Просрочка 48 часов
- `crm.infra_billing_node_payment_overdue_7_days` - Просрочка 7 дней

Биллинг-события агрегируются: при поступлении нескольких уведомлений в течение 3 секунд отправляется одно
сводное сообщение.

### Сервисные события (`service.*`)

- `service.panel_started` - Запуск панели
- `service.login_attempt_success` - Успешный вход
- `service.login_attempt_failed` - Неудачная попытка входа
- `service.subpage_config_changed` - Изменена конфигурация подписочной страницы
- `service.api_token_created` - Создан API токен
- `service.api_token_deleted` - Удален API токен

### События торрент-блокировщика (`torrent_blocker.*`)

Требуется панель Remnawave версии 2.7.0 и выше.

- `torrent_blocker.report` - Отчет о торрент-активности (узел, пользователь, статус блокировки, IP, протокол/сеть,
  источник и назначение)

### События ошибок (`errors.*`)

- `errors.bandwidth_usage_threshold_reached_max_notifications` - Достигнут лимит уведомлений о пороге трафика

## 📄 Лицензия

Проект распространяется по лицензии GNU General Public License v3.0. Подробности - в файле [LICENSE](https://github.com/hteppl/remnawave-webhook-bot/blob/master/LICENSE).
