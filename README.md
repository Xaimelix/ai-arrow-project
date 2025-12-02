# AI Arrow Project

Интерактивный веб‑интерфейс, который ведёт диалог во вселенной Dungeons & Dragons, генерирует иллюстрации и озвучку с помощью сервисов Yandex Cloud. Приложение построено на Flask, хранит историю переписки в SQLite и поддерживает авторизацию пользователей.

## Возможности
- Чат с персонажем: ответы строятся в YandexGPT с учётом всей истории переписки.
- Генерация арта: последние пользовательские реплики можно превратить в изображение через YandexART.
- Озвучивание: последние ответы синтезируются голосом «anton» через SpeechKit.
- История: текст, изображения и аудио сохраняются и выдаются одной лентой.
- Пользовательские аккаунты: регистрация, вход, выход и защита всех маршрутов через Flask‑Login.

## Технологический стек
- Python 3.11+
- Flask, Flask-WTF, Flask-Login
- SQLAlchemy + SQLite (`db/history.db`)
- Pillow для постобработки изображений
- requests, speechkit SDK и REST API YandexGPT / YandexART / SpeechKit

## Предварительные требования
1. Учётная запись Yandex Cloud и включённые API Foundation Models и SpeechKit.
2. Созданные ключи API и идентификатор каталога (folder_id).
3. Python и pip, желательно в отдельном virtualenv.

## Установка и запуск
```bash
# Клонируйте репозиторий и перейдите в каталог приложения
 git clone <repo_url>
 cd ai-arrow-project

# Создайте окружение и установите зависимости
 python -m venv .venv
 source .venv/bin/activate
 pip install flask flask-login flask-wtf sqlalchemy pillow requests speechkit

# Подготовьте статические каталоги
 mkdir -p static/images static/audio

# Запустите веб-приложение
 python main.py
```
Приложение откроется на http://127.0.0.1:5000.

## Настройка ключей (`tokens.csv`)
Файл лежит в корне проекта (`ai-arrow-project/tokens.csv`). Формат CSV должен содержать заголовок `catalog,identifier,apikey` и минимум две строки:
```
catalog,identifier,apikey
<catalog_for_gpt_and_art>,<folder_id>,<api_key_for_gpt_and_art>
<catalog_for_speechkit>,<folder_id>,<api_key_for_speechkit>
```
- Первая строка используется для YandexGPT и YandexART.
- Вторая — для SpeechKit (синтез речи).

## Структура проекта
```
ai-arrow-project/
├── main.py                # Flask-приложение и маршруты
├── yandexGPTtest.py       # Обёртка над Yandex APIs
├── data/                  # SQLAlchemy модели и сессии
├── forms/                 # Flask-WTF формы входа и регистрации
├── templates/             # HTML-шаблоны (чат, регистрация, логин)
├── db/history.db          # SQLite база (создаётся автоматически)
└── static/                # Изображения и аудио, создаётся вручную
```

## Основные маршруты
- `GET /` — главная страница чата (требуется вход).
- `POST /get-message` — отправка текста и получение ответа YandexGPT.
- `POST /get-art` и `POST /get-art-ready` — асинхронная генерация изображения.
- `POST /speech-synthesis` — синтез аудио последнего ответа.
- `GET /get-history` — история диалога и вложений.
- `GET|POST /login`, `GET|POST /register`, `GET /logout` — аутентификация.

## Дополнительные сведения
- История сообщений хранится в таблице `chatHistory` и связывается с пользователем.
- После генерации изображения оно приводится к размеру 400×400 px библиотекой Pillow и сохраняется в `static/images`.
- Аудиофайлы сохраняются в `static/audio` в формате `.ogg`.
- Подсказка для YandexGPT настроена в `yandexGPTtest.py` и описывает контекст DnD. Меняйте её под свои сценарии.

Готово! Теперь можно экспериментировать с промптами, оформлением интерфейса или расширять функциональность (например, добавив сброс истории, роли мастера игры и т.д.).
