# 🌐 SynapCore: Site & AI Bot

Единая инфраструктура для автоматизации бизнеса, включающая экспертный веб-сайт и интеллектуального FAQ-ассистента.

## 🌟 Ключевые особенности

### 💻 Веб-платформа (Flask)
- **AI ROI Calculator**: Интерактивный инструмент для оценки экономии человеко-часов при внедрении ИИ-агентов.
- **Process Diagnostic Tool**: Система скоринга готовности бизнеса к внедрению ИИ с визуализацией потенциала через Chart.js.
- **Clean Architecture**: Легкая и быстрая верстка на Tailwind CSS с серверной частью на Flask.

### 🤖 AI-Ассистент (Bot)
- **RAG & Knowledge Base**: Поиск по базе знаний через векторные хранилища (ChromaDB) для точных ответов.
- **Semantic Search**: Бот понимает смысл вопроса, даже если клиент использует синонимы или делает опечатки.

## 🛠 Технологический стек

- **Core**: Python 3.12, [uv](https://github.com/astral-sh/uv) (Package Manager)
- **Backend**: Flask, FastAPI
- **AI/LLM**: LangChain, OpenAI API, RelevanceAI
- **Database**: SQLAlchemy, ChromaDB
- **Frontend**: Tailwind CSS, Jinja2, Chart.js

## 📂 Структура проекта

```text
├── static/              # Ассеты: стили (Tailwind), скрипты, графика
├── templates/           # Шаблоны страниц на Jinja2
├── ai_bot/              # Модули Telegram-бота и AI-логика
├── app.py               # Точка входа для веб-сайта
├── bot.py               # Точка входа для запуска бота
├── extensions.py        # Конфигурация расширений Flask
├── forms.py             # Валидация и структура форм
├── models.py            # Модели базы данных (SQLAlchemy)
├── requirements.txt     # Зависимости проекта (оптимизированы через uv)
└── .env.example         # Пример конфигурации окружения

```

## 🚀 Установка и запуск на сервере

1. **Клонируйте репозиторий**:
   ```bash
   git clone [https://github.com/zuzinamd-creator/synapcore-full.git](https://github.com/zuzinamd-creator/synapcore-full.git)
cd synapcore-full
```

2. **Создайте окружение и установите зависимости**:
Мы используем uv для максимально быстрой установки:
   ```bash
Bash
uv venv
source venv/bin/activate  # Для Linux/macOS
uv pip install -r requirements.txt
```

3. **Настройте переменные окружения**:
   Создайте файл `.env` на основе `.env.example` и укажите ваши ключи:
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`

4. **Запуск компонентов**:
   - **Сайт**: `python app.py`
   - **Бот**: `python bot.py`

## 👩‍💻 Автор

**Telegram:** [@Margo_AI_Engineer](https://t.me/Margo_AI_Engineer)
