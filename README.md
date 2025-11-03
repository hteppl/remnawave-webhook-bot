# Remnawave Webhook Bot

✏️ Телеграм бот для уведомлений о состояниях и изменениях данных в панелях Remnawave.

## 📋 Возможности

- Легкая установка рядом с панелью Remnawave
- Поддержка топиков для разделения типов событий
- Полная кастомизация текстов, форматирования и типов обрабатываемых событий
- Дополнительные обработчики данных, включая получение данных о входах в панель
- Проверка получаемых данных с помощью заголовков безопасности Remnawave
- Интеграция с системой бекапов <a href="https://github.com/distillium/remnawave-backup-restore">
  remnawave-backup-restore</a>

## 🚀 Установка

### Требования

- Сервер с панелью Remnawave, с установленной подсистемой Docker

### Шаг 1: Загрузка файлов проекта на сервер

**Примечание:** для корректной интеграции с системой бекапов remnawave-backup-restore, рекомендуется загрузить файлы
проекта по пути `/opt/remnawave/webhook` (не обязательно)

Минимальный набор файлов проекта для начала процесса установки:

```text
src, locales, docker-compose.yml, Dockerfile, requirements.txt, pyproject.toml, .env.example
```

### Шаг 2: Настройка конфигурации

Создайте файл `.env` в корневой директории проекта:

```bash
sudo cp .env.example .env
```

**Примечание:** для корректного отображения айди чата ботом https://t.me/username_to_id_bot, следует превратить чат в
супергруппу с топиками еще до приглашения бота!

- `WEBHOOK_SECRET_HEADER` - переменная из окружения Remnawave: `sudo nano /opt/remnawave/.env`

В нижней части конфига доступна настройка фильтрации обрабатываемых уведомлений, используйте список из туториала, чтобы
определиться с требуемыми событиями.

```dotenv
# Настройки бота Telegram
# Чтобы получить айди чата можно использовать: https://t.me/username_to_id_bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Настройка топиков Telegram для посылки уведомлений
# Чтобы получить айди топика - скопируйте ссылку на сообщение.
# Пример: https://t.me/c/123123123/[2]/21 - 2 это и есть айди топика.
TOPIC_USER=
TOPIC_NODE=
TOPIC_CRM=
TOPIC_SERVICE=
# Топик для получения системных статусов, например CONNECTION_LOSS_STATS
TOPIC_STATUS=

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
```

## 🚀 Обновление

*Команды при установке в директорию `/opt/remnawave/webhook`*

Удалите старые файлы: `cd /opt/remnawave/webhook && sudo rm -R src && sudo rm -R locales && sudo rm Dockerfile`

Переменные окружения можно изменить/добавить в ручном режиме:

- Сравниваем актуальный .env.example
- Редактируем текущие переменные: `cd /opt/remnawave/webhook && sudo nano .env`

Перейдите к этапу установки, описанному выше.

## ▶️ Сборка и запуск

**Запуск осуществляется через подсистему Docker:**

*Команды при установке в директорию `/opt/remnawave/webhook`*

```bash
cd /opt/remnawave/webhook && sudo docker compose up -d --build
```

**Перезапуск:**

```shell
cd /opt/remnawave/webhook && sudo docker compose down && sudo docker compose up -d
```

**Просмотр логов:**

```bash
sudo docker logs remnawave-webhook-bot
```

## 🔐 Настройка реверс прокси и Remnawave

Вебхук обязательно должен находиться за реверс прокси, например `nginx`, `caddy` итп.

### Шаг 1: Настройка реверс прокси

Часть настройки конфигурации `сaddy`, работающего в одной подсети с Remnawave:

```caddyfile
https://panel.your_address.com {
    handle {
        reverse_proxy http://remnawave:3000
    }
    
    handle_path /webhook* {
        reverse_proxy http://remnawave-webhook-bot:8089
    }
}
```

После различных манипуляций с caddy или nginx, сервисы требуется перезапустить для применения настроек!

### Шаг 2: Проверка работоспособности:

```bash
curl https://panel.your_address.com/webhook/health
# Должен вернуть: OK
```

### Шаг 3: Добавление адреса обработчика в Remnawave:

Настройте переменные окружения Remnawave: `sudo nano /opt/remnawave/.env`

```dotenv
### WEBHOOK ###
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://panel.your_address.com/webhook
WEBHOOK_SECRET_HEADER=a12m7ca8h...
```

Перезагрузите Remnawave:

```bash
cd /opt/remnawave && sudo docker compose down && sudo docker compose up -d
```

## 📊 Поддерживаемые события

### События пользователей (`user.*`)

- `user.created` - Создание пользователя
- `user.modified` - Изменение пользователя
- `user.deleted` - Удаление пользователя
- `user.disabled` - Отключение пользователя
- `user.enabled` - Включение пользователя
- `user.limited` - Ограничение пользователя
- `user.expired` - Истечение срока пользователя
- `user.traffic_reset` - Сброс трафика
- `user.expires_in_*` - Уведомления об истечении срока
- `user.first_connected` - Первое подключение
- `user.bandwidth_usage_threshold_reached` - Достижение лимита трафика

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

- `crm.infra_billing_node_payment_in_48hrs` - Оплата через 48 часов
- `crm.infra_billing_node_payment_in_24hrs` - Оплата через 24 часа
- `crm.infra_billing_node_payment_due_today` - Оплата сегодня
- `crm.infra_billing_node_payment_overdue_24hrs` - Просрочка 24 часа
- `crm.infra_billing_node_payment_overdue_48hrs` - Просрочка 48 часов

**Особенность**: Биллинг-события автоматически агрегируются при получении нескольких уведомлений в течение 3 секунд,
отправляя одно сводное сообщение вместо множества отдельных.

### Сервисные события (`service.*`)

- `service.panel_started` - Запуск панели
- `service.login_attempt_success` - Успешный вход
- `service.login_attempt_failed` - Неудачная попытка входа

## 📄 Лицензия

[LICENSE](LICENSE)