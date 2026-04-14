# SynapCore: Site + Support Bot

Проект состоит из двух сервисов:
- сайт на Flask (`:5000`);
- FAQ/RAG-бот на FastAPI (`:8000`).

Фронтенд сайта отправляет сообщения в `POST /predict` на Flask, а Flask проксирует запрос к FastAPI (`/chat`).

## Возможности

### Сайт (Flask)
- лендинг с формой обратной связи;
- калькулятор ROI и диагностический квиз;
- админ-раздел для заявок и результатов диагностики;
- страница политики конфиденциальности по адресу `/privacy` (HTML-страница с текстом из `privacy-policy.md`).

### Бот поддержки (FastAPI)
- RAG-поиск по базе знаний;
- генерация ответа через OpenAI;
- fallback-сценарий: если бот не уверен в ответе, запрос эскалируется в Telegram.

### Логирование и уведомления
- ошибки пишутся в `logs/app_errors.log` (с ротацией файлов);
- ошибки формы обратной связи и чата поддержки отправляются в тот же Telegram-чат, что и обычные заявки.

## Технологии

- Python, Flask, FastAPI
- SQLAlchemy, Flask-WTF
- OpenAI API, FAISS, NumPy
- Tailwind CSS, Jinja2, Chart.js

## Структура проекта

```text
├── app.py                      # Flask-приложение (сайт + прокси /predict)
├── backend_bot/
│   ├── backend/app.py          # FastAPI-приложение бота
│   └── data/                   # База знаний и индексы
├── templates/                  # HTML-шаблоны Jinja2
├── static/                     # JS/CSS/медиа
├── logs/app_errors.log         # Файл логов ошибок (создается приложением)
├── privacy-policy.md           # Исходный текст политики конфиденциальности
├── requirements.txt
└── .env.example
```

## Переменные окружения

Создайте `.env` в корне проекта и укажите минимум:
- `SECRET_KEY`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Локальный запуск

1. Создайте и активируйте виртуальное окружение.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите FastAPI-бота:

```bash
python -m uvicorn backend_bot.backend.app:app --host 127.0.0.1 --port 8000
```

4. В другом терминале запустите Flask-сайт:

```bash
python app.py
```

5. Откройте:
- сайт: `http://127.0.0.1:5000`
- health бота: `http://127.0.0.1:8000/health`
- docs бота: `http://127.0.0.1:8000/docs`

## Примечания

- Для валидации email используется пакет `email-validator`.
- Чат на сайте использует CSRF-токен (`X-CSRFToken`) для запроса в `POST /predict`.

## Автор

Telegram: [@Margo_AI_Engineer](https://t.me/Margo_AI_Engineer)
