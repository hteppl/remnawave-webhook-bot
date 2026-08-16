# Заголовок и разделители
message-header-event = 📋 Событие
message-header-action = Действие
message-header-time = 🕐 Время
message-header-data-label = Данные
message-separator-field = {"  "}•{" "}

# Поля данных
field-username = Имя пользователя
field-email = Email
field-status = Статус
field-used-traffic = Трафик
field-data-limit = Лимит трафика
field-expire = Истекает
field-created-at = Создан
field-usage-percentage = Процент использования
field-name = Название
field-node-name = Название узла
field-address = Адрес
field-location = Локация
field-provider = Провайдер
field-inbound = Инбаунд
field-inbound-tags = Инбаунды
field-port = Порт
field-xray-version = Версия Xray
field-node-version = Версия ноды
field-traffic-used = Трафик
field-ip = IP
field-geo-country = Страна
field-geo-city = Город/Регион
field-geo-isp = Провайдер
field-device = Устройство
field-user-agent = User Agent
field-description = Описание
field-last-status-message = 📝 Последний статус
field-downtime = ⏱ Время простоя
field-password = Пароль
field-squads = Сквады
field-hwid = HWID
field-hwid-limit = Лимит устройств
field-platform = Платформа
field-os-version = Версия ОС
field-device-model = Модель устройства
field-blocked = Заблокировано
field-block-duration = Длительность блокировки
field-unblock-at = Разблокировка
field-protocol = Протокол
field-network = Сеть
field-source = Источник
field-destination = Назначение
field-inbound-tag = Инбаунд
field-outbound-tag = Аутбаунд
field-action = Действие
field-uuid = UUID
field-scopes = Права

# Общие значения
value-yes = Да
value-no = Нет

# Форматирование длительности
duration-seconds = {$seconds} сек.
duration-minutes = {$minutes} мин.
duration-hours = {$hours} ч.
duration-days = {$days} дн.

# Форматирование дат
date-in-days = через {$days} дн.
date-days-ago = {$days} дн. назад
date-in-hours = через {$hours} ч.
date-today = сегодня
date-unlimited = Без лимита

# События пользователей
event-user-header = 👤 Информация о пользователе
event-user-created-message = Создан новый пользователь
event-user-modified-message = Пользователь изменен
event-user-deleted-message = Пользователь удален
event-user-revoked-message = Доступ пользователя отозван
event-user-disabled-message = Пользователь отключен
event-user-enabled-message = Пользователь включен
event-user-limited-message = Пользователь ограничен
event-user-expired-message = Срок действия пользователя истек
event-user-traffic-reset-message = Трафик пользователя сброшен

event-user-expiration-icon = ⏰
event-user-expiration-message = Уведомление об истечении срока
event-user-expiration-in-message = Пользователь истекает через { $hours } ч.
event-user-expiration-ago-message = Срок пользователя истек { $hours } ч. назад

event-user-not-connected-icon = 💤
event-user-not-connected-message = Пользователь не подключается
event-user-not-connected-hours-message = Пользователь не подключается уже { $hours } ч.

event-user-first-connected-icon = ✅
event-user-first-connected-message = Первое подключение пользователя

event-user-bandwidth-usage-threshold-reached-icon = ⚠️
event-user-bandwidth-usage-threshold-reached-message = Достигнут порог использования трафика: { $usage_percentage }%

# События устройств пользователей (HWID)
event-user-hwid-devices-header = 📱 Информация об устройстве

event-user-hwid-devices-added-icon = ➕
event-user-hwid-devices-added-message = Добавлено устройство HWID

event-user-hwid-devices-deleted-icon = ➖
event-user-hwid-devices-deleted-message = Удалено устройство HWID

# События узлов
event-node-header = 🖥 Информация об узле
event-node-created-message = Создан новый узел
event-node-modified-message = Узел изменен
event-node-disabled-message = Узел отключен
event-node-enabled-message = Узел включен
event-node-deleted-message = Узел удален
event-node-traffic-notify-message = Уведомление о трафике узла

event-node-connection-lost-icon = ❌
event-node-connection-lost-message = Соединение с узлом потеряно!

event-node-connection-restored-icon = ✅
event-node-connection-restored-message = Соединение с узлом восстановлено

# Статистика потерь соединения
connection-stats-title = 📊 Потери соединения (за {$hours}ч)
provider-stats-title = 🏢 По провайдерам
country-stats-title = 🌍 По странам
total-stats-label = 📈 Всего

# Ежедневная статистика пользователей
daily-stats-title = 📊 Статистика за день
daily-stats-users-created = 👤 Создано пользователей
daily-stats-users-first-connected = ✅ Первых подключений

# События биллинга
event-crm-header = 💰 Информация о биллинге

# Метки полей биллинга
billing-field-node = Узел
billing-field-provider = Провайдер
billing-field-billing-date = Дата оплаты
billing-field-login-to-provider = Панель {$provider}
billing-field-total-nodes = Всего узлов
billing-field-nodes = узлов

# Агрегирование биллинга
billing-aggregated-title = 💰 Несколько уведомлений о биллинге

# Индивидуальные события биллинга
event-crm-infra-billing-node-payment-in-7-days-icon = 📅
event-crm-infra-billing-node-payment-in-7-days-message = Оплата узла через 7 дней

event-crm-infra-billing-node-payment-in-48hrs-icon = 🔵
event-crm-infra-billing-node-payment-in-48hrs-message = Оплата узла через 48 часов

event-crm-infra-billing-node-payment-in-24hrs-icon = 🟡
event-crm-infra-billing-node-payment-in-24hrs-message = Оплата узла через 24 часа

event-crm-infra-billing-node-payment-due-today-icon = 🟡
event-crm-infra-billing-node-payment-due-today-message = Оплата узла сегодня

event-crm-infra-billing-node-payment-overdue-24hrs-icon = 🟠
event-crm-infra-billing-node-payment-overdue-24hrs-message = Просрочка оплаты узла на 24 часа

event-crm-infra-billing-node-payment-overdue-48hrs-icon = 🔴
event-crm-infra-billing-node-payment-overdue-48hrs-message = Просрочка оплаты узла на 48 часов

event-crm-infra-billing-node-payment-overdue-7-days-icon = 🔴
event-crm-infra-billing-node-payment-overdue-7-days-message = Просрочка оплаты узла на 7 дней

# События сервиса
event-service-header = ⚙️ Событие сервиса

event-service-panel-started-icon = ✅
event-service-panel-started-message = Панель запущена

event-service-login-attempt-failed-icon = ⚠️
event-service-login-attempt-failed-message = Неудачная попытка входа

event-service-login-attempt-success-icon = ✅
event-service-login-attempt-success-message = Успешный вход

event-service-subpage-config-changed-icon = 📝
event-service-subpage-config-changed-message = Изменена конфигурация страницы подписок

event-service-api-token-created-icon = 🔑
event-service-api-token-created-message = Создан API токен

event-service-api-token-deleted-icon = 🔑
event-service-api-token-deleted-message = Удален API токен

# События торрент-блокировщика
event-torrent-blocker-header = 🚫 Отчет торрент-блокировщика

event-torrent-blocker-report-icon = 🚫
event-torrent-blocker-report-message = Обнаружена торрент-активность

# События ошибок
event-errors-header = ‼️ Информация об ошибке

event-errors-bandwidth-usage-threshold-reached-max-notifications-icon = ‼️
event-errors-bandwidth-usage-threshold-reached-max-notifications-message = Достигнут лимит уведомлений о пороге трафика

# Сообщения при запуске топиков
topic-startup-message = ✅ Топик {$topic_name} настроен!

# УСТАРЕВШИЕ (DEPRECATED)
event-user-expires-in-72-hours-icon = ⏰
event-user-expires-in-72-hours-message = Пользователь истекает через 72 часа

event-user-expires-in-48-hours-icon = ⏰
event-user-expires-in-48-hours-message = Пользователь истекает через 48 часов

event-user-expires-in-24-hours-icon = ⚠️
event-user-expires-in-24-hours-message = Пользователь истекает через 24 часа

event-user-expired-24-hours-ago-icon = ❌
event-user-expired-24-hours-ago-message = Срок пользователя истек 24 часа назад
