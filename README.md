# 🖤 Tele Tool! Proxified!

![Header](https://i.ibb.co/W408CSt1/image.png)

> Этот репозиторий является **форком** оригинального TeleTool с расширенной поддержкой прокси:
> `Proxy Manager`, режимы ротации прокси, сбалансированное распределение учетных записей между прокси и сохраненные планы JSON в `results/proxy_plans/`.

---

## ♥️ О проекте

**Tele Tool** — Инструмент для работы с Telegram сессиями. Программа предоставляет полный набор функций для управления и конвертации Telegram аккаунтов, делая процесс максимально простым и эффективным.

---

## ♻️ Что добавлено в этом форке

- глобальный `Proxy Manager` в главном меню
- несколько режимов распределения аккаунтов по прокси
- основной smart-режим `chunked_round_robin`
- сохранение последнего плана распределения в `results/proxy_plans/*.json`
- общий proxy-layer для массовых операций
- валидация `proxies.txt`, проверка зависимостей и более понятные proxy-ошибки

---

## 🌐 Proxy Manager

В главном меню появился отдельный пункт `Proxy Manager`. Через него можно:

- включать и отключать прокси глобально
- менять режим работы
- открывать `proxies.txt`
- открывать последние JSON-планы распределения
- быстро проверять статус, число валидных прокси и ошибки в proxy-строках

### Режимы работы

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
- нагрузка распределяется мягче и естественнее

Подробности, примеры и форматы строк прокси описаны в [PROXY_GUIDE.md](PROXY_GUIDE.md).

### Поддерживаемые форматы прокси

```text
socks5://127.0.0.1:9050
socks5://user:password@127.0.0.1:9050
http://127.0.0.1:8080
127.0.0.1:9050
127.0.0.1:9050:user:password
socks5:127.0.0.1:9050:user:password
```

Если тип не указан, по умолчанию используется `socks5`.

---



## 🖤 Основные возможности:
<details>
  <summary><strong>📂 КАТЕГОРИЯ: 💫 Операции с сессиями</strong></summary>
  <br>
  
  <details>
    <summary><strong>└─ 💨 Анализ сессии</strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Открытие директории для загрузки данных (Папка для .session файлов)</li>
      <li> 4. Открытие директории для получения результатов (Папка с результатами анализа)</li>
      <li> 5. Анализ аккаунта (Получение полной информации о сессии в JSON формате)</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/60d949v0/image.png" alt="Session Analysis 1" width="62%">
        <img src="https://i.ibb.co/PswQJz9D/image.png" alt="Session Analysis 2" width="36%">
    </div>
  </details>
  
  <details>
    <summary><strong>└─ 💨 Создать session через QR</strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Получить QR код (Папка для .session файлов)</li>
      <li> 4. Открытие директории для получения результатов (Папка с результатами анализа)</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/MkbmtQ38/image.png" alt="Session Analysis 1" width="62%">
    </div>
  </details>

  <details>
    <summary><strong>└─ 💨 Создать session через код</strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Получить QR код (Папка для .session файлов)</li>
      <li> 4. Открытие директории для получения результатов (Папка с результатами анализа)</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/qMRkPDKt/image.png" alt="Session Analysis 1" width="62%">
    </div>
  </details>
</details>

<details>
  <summary><strong>📂 КАТЕГОРИЯ: 🔄 Конвертация</strong></summary>
  <br>
  
  <details>
    <summary><strong>└─ 💨 Session ➜ Tdata</strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Открытие директории для загрузки .session файлов</li>
      <li> 4. Открытие директории с результатами конвертации</li>
      <li> 5. Конвертация .session файлов в формат Telegram Desktop (tdata)</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/8L9Hhd3R/image.png" alt="Session Analysis 1" width="62%">
    </div>
  </details>

  <details>
    <summary><strong>└─ 💨 Tdata ➜ Session</strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Открытие директории для загрузки tdata папок</li>
      <li> 4. Открытие директории с результатами конвертации</li>
      <li> 5. Конвертация Telegram Desktop (tdata) файлов в формат .session</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/XxP2yBhm/image.png" alt="Session Analysis 1" width="62%">
    </div>
  </details>

  <details>
    <summary><strong>└─ 💨 Session ➜ Info</strong></summary>
    <br>
    <ul>
      <li> 1. Открытие директории для загрузки .session файла</li>
      <li> 2. Открытие директории с результатами конвертации</li>
      <li> 3. Анализ файла .session и получение информации в формате JSON</li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/jPP3Y8nR/image.png" alt="Session Analysis 1" width="62%">
        <img src="https://i.ibb.co/m5sKcPK6/image.png" alt="Session Analysis 2" width="64%">
    </div>
  </details>
</details>

<details>
  <summary><strong>📂 КАТЕГОРИЯ: 🧹 Управление и очистка</strong></summary>
  <br>
  
  <details>
    <summary><strong>└─ 💨 Очистка каналов | групп | ботов | чатов </strong></summary>
    <br>
    <ul>
      <li> 1. Настройка device (Предлагает на выбор конфигурации девайсов для входа в сессию от их лица)</li>
      <li> 2. Настройка API id and hash (Настройка данных для подключения к Telegram API)</li>
      <li> 3. Открытие директории для загрузки .session файла</li>
      <li> 4. Вывести кол-во диалогов (каналы, группы, боты, чаты) </li>
      <li> 5. Выйти со всех диалогов (каналы, группы, боты, чаты) </li>
    </ul>
    <div style="display: flex; justify-content: space-between;">
        <img src="https://i.ibb.co/nqXwMGXH/image.png" alt="Session Analysis 1" width="62%">
    </div>
  </details>
</details>

---

## ⚙️ Используемые технологии

### 🛠️ Основные библиотеки</strong></summary>
![Python](https://img.shields.io/badge/Python-%23000000.svg?style=for-the-badge&logo=python&logoColor=white) ![Telethon](https://img.shields.io/badge/Telethon-%23000000.svg?style=for-the-badge&logo=telegram&logoColor=white) ![OpenTele](https://img.shields.io/badge/OpenTele-%23000000.svg?style=for-the-badge&logo=telegram&logoColor=white) ![PySocks](https://img.shields.io/badge/PySocks-%23000000.svg?style=for-the-badge&logo=python&logoColor=white) ![PyStyle](https://img.shields.io/badge/PyStyle-%23000000.svg?style=for-the-badge&logo=python&logoColor=white) ![Colorama](https://img.shields.io/badge/Colorama-%23000000.svg?style=for-the-badge&logo=python&logoColor=white) ![ConfigParser](https://img.shields.io/badge/ConfigParser-%23000000.svg?style=for-the-badge&logo=python&logoColor=white) ![AsyncIO](https://img.shields.io/badge/AsyncIO-%23000000.svg?style=for-the-badge&logo=python&logoColor=white)

---

## 📋 Требования

### 💻 Системные требования:
- Python 3.8 или выше (желательно 3.11.6)
- Windows операционная система
- Минимум 100MB свободного места
- Стабильное подключение к интернету
- RAM: минимум 2GB

### 🔑 Telegram API:
- API ID (получить на my.telegram.org)
- API Hash (получить на my.telegram.org)
- Активный Telegram аккаунт
- Доступ к Telegram API

---

## 🌳 Структура проекта

```bash
TeleToolProxified/
├── 📁 menu/               # Модули меню
│   ├── banner.py         # Отрисовка баннера и разделителей
│   ├── session_analyzer.py       # Меню анализа сессий
│   ├── session_creator_qr.py      # Создание сессий через QR
│   ├── session_creator_code.py   # Авторизация по коду
│   ├── cleaner_and_info.py       # Управление очисткой аккаунта
│   └── proxy_manager.py         # Управление прокси
│
├── 📁 utils/             # Вспомогательные модули
│   ├── get_account_info.py      # Парсинг информации об аккаунте
│   ├── create_session_qrcode.py # Генерация QR-кодов
│   ├── convert_session_tdata.py # Конвертация session → tdata 
│   ├── convert_tadata_session.py # Конвертация tdata → session
│   ├── clener_dialogs.py        # Логика очистки диалогов
│   ├── runtime_config.py        # Логика параметров работы
│   └── proxy_manager.py         # Логика прокси и ротации
│
├── 📁 src/               # Ресурсы проекта
│   └── set_apps.json     # База устройств для эмуляции
│
├── 📁 results/            # Результаты работы
│   ├── account_info_save/ # Дампы информации аккаунтов
│   ├── session_analyzer/  # Результаты анализа сессий
│   ├── create_session_*/  # Созданные session-файлы
│   └── proxy_plans/       # Последние планы распределения по прокси
│
├── 📄 main.py            # Главный исполняемый файл
├── 📄 config.ini         # Конфигурация API и устройств
├── 📄 proxies.txt        # Список прокси
├── 📄 PROXY_GUIDE.md     # Подробное описание proxy-режимов
├── 📄 requirements.txt   # Зависимости проекта
└── 📄 run.bat            # Скрипт запуска для Windows
```

### Пояснения к структуре:
1. **Ядро системы** (`main.py`) - Центральный модуль, управляющий всей логикой приложения
2. **Меню-модули** - Группа файлов реализующих интерактивный интерфейс
3. **Утилиты** - Набор "движков" для выполнения основных операций
4. **Конфигурация** - Файлы настроек и пресетов устройств
5. **Результаты** - Автоматически генерируемые в процессе работы данные

---

## 🚀 Руководство по запуску

### 1. Клонирование репозитория
```bash
git clone https://github.com/d1n0tf/TeleToolProxified
cd TeleToolProxified
```

### 2. Настройка окружения
```bash
# Создание виртуального окружения (Windows)
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка конфигурации
1. Получите API ID и Hash на [my.telegram.org](https://my.telegram.org/apps)
2. Отредактируйте `config.ini`:
```ini
[QR]
device_id = 0
api_id = YOUR_API_ID       # Замените на свои значения
api_hash = YOUR_API_HASH   # 32-символьная строка

[PROXY]
enabled = false
mode = chunked_round_robin
proxy_file = proxies.txt
```

### 4. Настройка прокси
1. Откройте `Proxy Manager`
2. Заполните `proxies.txt`
3. Выберите нужный режим
4. Включите прокси

### 5. Запуск приложения
```bash
# Стандартный запуск
python main.py

# Или через bat-файл (Windows)
run.bat
```

### 🛠 Первый запуск:
1. При открытии любого меню где требуется Telegram API приступайте к пункту 2 и 3
2. Настройте device (рекомендуется выбор 0 - Xiaomi)
3. Введите валидные API данные
4. Следуйте инструкциям на экране

![Пример работы](https://i.ibb.co/W408CSt1/image.png)

### ⚠️ Важно!
- Используйте только свои API ключи
- Не делитесь файлами `.session` и `tdata`
- Перед массовыми действиями проверьте, что `proxies.txt` заполнен корректно
- Последний план распределения сохраняется в `results/proxy_plans/*.json`
- При ошибках проверьте логи в `results/*/*.log`


## 🖤 Контакты

[![Telegram](https://img.shields.io/badge/-Telegram-black?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/d1n0tf)  [![Lolz](https://img.shields.io/badge/-Lolz%20Team-black?style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAFdJREFUOI3FkjEOgkAQRc/CoFAEmf4SzkIkg1UkfsAdKNFBOkEEVnMkr1SBBSgUtqtUKV9jeBGwrvE3d+7s3TeAH5GgdYBGSCYJ1ASowm5YAz5voFrOh6oP/poM14wHdAe2Bi4OjsMUyccxPB3bs6Dn8AMhRWLZLeQKkwAAAABJRU5ErkJggg==&logoColor=white)](https://lolz.live/members/10620650/) [![Gmail](https://img.shields.io/badge/-Gmail-black?style=for-the-badge&logo=gmail&logoColor=white)](mailto:d1n0tf@starletters.space)
