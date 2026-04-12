# Веб-сайт на Flask

Полнофункциональный веб-сайт с формой обратной связи, кейсами, админ-панелью и интерактивными инструментами оценки эффективности внедрения ИИ-решений.

## 🌟 Ключевые особенности

- **AI ROI Calculator**: Интерактивный инструмент для оценки экономии человеко-часов при автоматизации типовых запросов.
- **Process Diagnostic Tool**: Система скоринга готовности бизнеса к внедрению ИИ с визуализацией потенциала через Chart.js.
- **Clean Architecture**: Легкая и быстрая верстка на Tailwind CSS с серверной частью на Flask.


## 🛠 Технологический стек

- **Backend**: Python, Flask
- **Frontend**: Tailwind CSS, Jinja2, Chart.js
- **Data Management**: Flask-SQLAlchemy, Flask-WTF
- **Environment**: Dotenv (.env)

## 📂 Структура проекта

```text
├── static/              # Ассеты: стили, скрипты, графика
├── templates/           # Шаблоны страниц на Jinja2
├── app.py               # Точка входа и инициализация приложения
├── extensions.py        # Конфигурация расширений Flask
├── forms.py             # Валидация и структура форм
├── models.py            # Модели базы данных (SQLAlchemy)
├── requirements.txt     # Зависимости проекта
└── .env.example         # Пример конфигурации окружения
```

## 🚀 Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone [https://github.com/zuzinamd-creator/medtech-ai-site.git](https://github.com/zuzinamd-creator/medtech-ai-site.git)
```

2. **Установите зависимости**:

```bash
pip install -r requirements.txt

```

3. **Настройте переменные окружения**:
Создайте файл `.env` на основе `.env.example` и укажите ваш `SECRET_KEY`.

4. **Запустите сервер**:

```bash
python app.py
```

## 👩‍💻 Автор

**Telegram:** [@Margo_AI_Engineer](https://t.me/Margo_AI_Engineer)
