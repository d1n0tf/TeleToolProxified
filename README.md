# Tele Tool Fork

![Header](https://i.ibb.co/W408CSt1/image.png)

Этот репозиторий является **fork** оригинального `TeleTool` и расширяет его proxy-инфраструктурой для работы с Telegram-сессиями.

## Что умеет проект

`Tele Tool` помогает работать с Telegram `.session` и `tdata`:

- анализ `.session` и выгрузка информации в JSON
- создание `.session` через QR
- создание `.session` через код подтверждения
- конвертация `session -> tdata`
- конвертация `tdata -> session`
- массовая очистка каналов, групп, ботов и диалогов

## Что добавлено в этом fork

- глобальный `Proxy Manager` в главном меню
- несколько режимов распределения аккаунтов по прокси
- основной smart-режим `chunked_round_robin`
- сохранение последнего плана распределения в `results/proxy_plans/*.json`
- общий proxy layer для массовых операций, а не отдельные хаки по модулям

## Proxy Manager

В главном меню появился отдельный пункт `Proxy Manager`. Через него можно:

- включать и отключать прокси глобально
- менять режим работы
- открывать `proxies.txt`
- открывать последние JSON-планы распределения
- быстро проверять статус и количество валидных прокси

### Режимы

- `chunked_round_robin` — рекомендуемый режим. Аккаунты делятся по прокси равномерными пачками, но обрабатываются по кругу.
- `round_robin` — каждый следующий аккаунт получает следующий прокси по кругу.
- `sticky_hash` — одна и та же сессия старается закрепляться за одним и тем же прокси между запусками.
- `single` — все аккаунты используют первый прокси из списка.

### Как работает основной режим

Пример:

- 100 аккаунтов
- 10 прокси

Результат:

- каждый прокси получает примерно по 10 аккаунтов
- обработка идет не `10 подряд на одном прокси`, а по кругу
- нагрузка распределяется мягче

Подробности, примеры и форматы строк прокси описаны в [PROXY_GUIDE.md](PROXY_GUIDE.md).

## Поддерживаемые форматы прокси

```text
socks5://127.0.0.1:9050
socks5://user:password@127.0.0.1:9050
http://127.0.0.1:8080
127.0.0.1:9050
127.0.0.1:9050:user:password
socks5:127.0.0.1:9050:user:password
```

Если тип не указан, по умолчанию используется `socks5`.

## Технологии

- Python
- Telethon
- OpenTele
- PySocks
- PyStyle
- Colorama
- AsyncIO

## Требования

- Python 3.8+
- Windows
- доступ к Telegram API
- `api_id` и `api_hash` с `my.telegram.org`

## Быстрый старт

### 1. Клонирование

Если вы хотите работать именно с этим fork, клонируйте URL своего fork-репозитория.

```bash
git clone https://github.com/klintxxxgod/TeleTool
cd TeleTool
```

### 2. Установка зависимостей

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настройка `config.ini`

Минимально настройте API-данные хотя бы для нужного раздела, например:

```ini
[QR]
device_id = 0
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
```

Для прокси в этом fork используется отдельная секция:

```ini
[PROXY]
enabled = false
mode = chunked_round_robin
proxy_file = proxies.txt
```

### 4. Настройка прокси

1. Откройте `Proxy Manager`
2. Включите прокси
3. Заполните `proxies.txt`
4. Выберите нужный режим

### 5. Запуск

```bash
python main.py
```

или через:

```bash
run.bat
```

## Структура проекта

```text
TeleToolProxified/
├── main.py
├── config.ini
├── proxies.txt
├── PROXY_GUIDE.md
├── requirements.txt
├── menu/
│   ├── banner.py
│   ├── cleaner_and_info.py
│   ├── proxy_manager.py
│   ├── session_account_info.py
│   ├── session_analyzer.py
│   ├── session_creator_code.py
│   ├── session_creator_qr.py
│   ├── session_to_tdata.py
│   └── tdata_to_session.py
├── utils/
│   ├── clener_dialogs.py
│   ├── convert_session_tdata.py
│   ├── convert_tadata_session.py
│   ├── create_session_code.py
│   ├── create_session_qrcode.py
│   ├── get_account_info.py
│   ├── proxy_manager.py
│   └── runtime_config.py
└── results/
```

## Важные замечания

- Используйте только свои `api_id` и `api_hash`
- Не делитесь `.session` и `tdata`
- Перед массовыми действиями проверьте, что `proxies.txt` заполнен корректно
- Последний план распределения сохраняется в `results/proxy_plans/*.json`
- При ошибках смотрите логи в `results/*/*.log`

## Контакты разработчиков

Контакты оригинального автора и автора этого fork:

### Автор форка

- Telegram: [@d1n0tf](https://t.me/d1n0tf)
- LOLZ: `d1n0`
- GitHub: [d1n0tf](https://github.com/d1n0tf)

### Оригинальный автор

- Telegram: [@klintxxxgod](https://t.me/klintxxxgod)
- LOLZ: `KLINTXXXGOD`
- BHF: `KLINTXXXGOD`
- GitHub: [klintxxxgod](https://github.com/klintxxxgod)
