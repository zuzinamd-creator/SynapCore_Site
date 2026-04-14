# -*- coding: utf-8 -*-
"""
Точка входа Flask-приложения MedTech AI.
Маршруты: лендинг, форма связи, API cookies и аудита, админ-панель.
Уведомления в Telegram — через TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID (.env).
"""
import json
import logging
import os
import re
from datetime import datetime
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect, validate_csrf
from wtforms import ValidationError

from extensions import db, login_manager
from forms import AdminLoginForm, ContactForm
from models import AuditResult, CookieConsent, Feedback, User

# Загрузка переменных из .env в корне проекта (токены не хранятся в коде).
load_dotenv()

logger = logging.getLogger(__name__)

UNKNOWN_ANSWER_PATTERNS = (
    r"\bне\s+увер",
    r"\bне\s+знаю",
    r"\bнет\s+информац",
    r"\bне\s+могу\s+ответ",
    r"\bобратит(?:е|ь)сь\s+в\s+поддержк",
)

# Ссылка на контакт в Telegram (для текста уведомлений).
TELEGRAM_CONTACT_URL = "https://t.me/Margo_AI_Engineer"


def configure_file_logging() -> None:
    """Настраивает запись логов в отдельный файл проекта."""
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "app_errors.log")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Не дублируем обработчик при повторном создании app (debug reload).
    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler) and getattr(
            handler, "baseFilename", ""
        ) == log_path:
            return

    file_handler = RotatingFileHandler(
        log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(file_handler)


def send_telegram_notification(text: str) -> None:
    """
    Отправка сообщения в Telegram через Bot API.
    Если TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не заданы — тихо пропускаем.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        logger.warning(
            "Telegram notification skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"
        )
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=12,
        )
        if not r.ok:
            logger.warning("Telegram API: %s %s", r.status_code, r.text[:200])
        else:
            logger.info("Telegram notification sent successfully")
    except requests.RequestException as exc:
        logger.warning("Telegram send failed: %s", exc)


def notify_error(context: str, details: str) -> None:
    """Логирует ошибку и отправляет уведомление в тот же Telegram-чат."""
    logger.error("%s | %s", context, details)
    send_telegram_notification(
        "🚨 Ошибка в веб-приложении\n\n"
        f"Контекст: {context}\n"
        f"Детали: {details}\n"
        f"Контакт: {TELEGRAM_CONTACT_URL}"
    )


def is_unknown_answer(answer: str) -> bool:
    """Определяет, что ассистент не уверен в ответе и нужен оператор."""
    text = (answer or "").strip().lower()
    if not text:
        return True
    return any(re.search(pattern, text) for pattern in UNKNOWN_ANSWER_PATTERNS)


def ensure_admin_user() -> None:
    """Создаёт учётку администратора при первом запуске (если её ещё нет)."""
    admin_email = "admin@med-ai.pro"
    if User.query.filter_by(email=admin_email).first():
        return
    user = User(email=admin_email, is_admin=True)
    user.set_password("Margo_AI_2026")
    db.session.add(user)
    db.session.commit()


def compute_automation_score(q1: int, q2: int, q3: int) -> int:
    """
    Оценка потенциала автоматизации (%) по ответам квиза (0–3 на вопрос).
    Диапазон итога ограничен разумными пределами для визуализации.
    """
    try:
        a = max(0, min(3, int(q1)))
        b = max(0, min(3, int(q2)))
        c = max(0, min(3, int(q3)))
    except (TypeError, ValueError):
        return 55
    raw = 45 + (a + b + c) * 8
    return int(max(48, min(96, raw)))


def create_app() -> Flask:
    """Фабрика приложения: конфигурация, расширения, маршруты."""
    configure_file_logging()
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "medtech.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        """Загрузка пользователя по id для сессии Flask-Login."""
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()
        ensure_admin_user()

    @app.context_processor
    def inject_globals():
        """Год в футере и другие глобальные переменные шаблонов."""
        return {"now_year": datetime.utcnow().year}

    @app.route("/")
    def index():
        """Главная страница лендинга."""
        form = ContactForm()
        return render_template("index.html", form=form)

    @app.route("/contact", methods=["POST"])
    def contact():
        """Приём формы обратной связи с CSRF и валидацией WTForms."""
        form = ContactForm()
        if form.validate_on_submit():
            try:
                entry = Feedback(
                    name=form.name.data.strip(),
                    email=form.email.data.strip().lower(),
                    company=form.company.data.strip(),
                    message=form.message.data.strip(),
                    ip_address=request.remote_addr,
                )
                db.session.add(entry)
                db.session.commit()
                send_telegram_notification(
                    "📝 Новая заявка с сайта\n\n"
                    f"Имя: {entry.name}\n"
                    f"Email: {entry.email}\n"
                    f"Компания: {entry.company}\n"
                    f"Сообщение:\n{entry.message}\n\n"
                    f"IP: {entry.ip_address or '—'}\n"
                    f"Контакт: {TELEGRAM_CONTACT_URL}"
                )
                flash("Спасибо! Мы свяжемся с вами в ближайшее время.", "success")
            except Exception as exc:
                db.session.rollback()
                logger.exception("Contact form processing failed: %s", exc)
                notify_error(
                    "Форма обратной связи",
                    (
                        f"{type(exc).__name__}: {exc}; "
                        f"ip={request.remote_addr or '—'}; "
                        f"email={form.email.data or '—'}"
                    ),
                )
                flash("Произошла ошибка при отправке формы. Попробуйте позже.", "danger")
        else:
            for errors in form.errors.values():
                for err in errors:
                    flash(err, "danger")
        return redirect(url_for("index") + "#contact")

    @app.route("/api/cookie-consent", methods=["POST"])
    def api_cookie_consent():
        """Сохранение согласия на cookies (IP, User-Agent, дата)."""
        try:
            validate_csrf(request.headers.get("X-CSRFToken"))
        except ValidationError:
            return jsonify({"ok": False, "error": "csrf"}), 400
        ua = (request.headers.get("User-Agent") or "")[:512]
        row = CookieConsent(
            ip_address=request.remote_addr or "unknown",
            user_agent=ua,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True})

    @app.route("/api/audit", methods=["POST"])
    def api_audit():
        """Сохранение результатов диагностики потенциала и расчёт показателя автоматизации."""
        try:
            validate_csrf(request.headers.get("X-CSRFToken"))
        except ValidationError:
            return jsonify({"ok": False, "error": "csrf"}), 400
        data = request.get_json(silent=True) or {}
        try:
            q1 = int(data.get("q1", 0))
            q2 = int(data.get("q2", 0))
            q3 = int(data.get("q3", 0))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "bad_input"}), 400
        score = compute_automation_score(q1, q2, q3)
        answers = {"q1": q1, "q2": q2, "q3": q3}
        row = AuditResult(
            answers_json=json.dumps(answers, ensure_ascii=False),
            automation_score=score,
            ip_address=request.remote_addr,
        )
        db.session.add(row)
        db.session.commit()
        send_telegram_notification(
            "📊 Диагностика потенциала автоматизации\n\n"
            f"ID записи: {row.id}\n"
            f"Оценка: {score}%\n"
            f"Ответы: q1={q1}, q2={q2}, q3={q3}\n"
            f"IP: {row.ip_address or '—'}\n\n"
            f"Контакт: {TELEGRAM_CONTACT_URL}"
        )
        return jsonify({"ok": True, "id": row.id, "score": score})

    @app.route("/privacy")
    def privacy():
        """Открывает HTML-страницу с текстом из privacy-policy.md."""
        policy_path = os.path.join(app.root_path, "privacy-policy.md")
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                policy_markdown = f.read()
        except OSError as exc:
            logger.exception("Failed to read privacy policy file: %s", exc)
            policy_markdown = (
                "Не удалось загрузить текст политики конфиденциальности. "
                "Попробуйте обновить страницу позже."
            )
        return render_template("privacy.html", policy_markdown=policy_markdown)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        """Вход в админ-панель."""
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))
        form = AdminLoginForm()
        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            user = User.query.filter_by(email=email).first()
            if user and user.is_admin and user.check_password(form.password.data):
                login_user(user, remember=True)
                nxt = request.args.get("next")
                if nxt and nxt.startswith("/"):
                    return redirect(nxt)
                return redirect(url_for("admin_dashboard"))
            flash("Неверный email или пароль.", "danger")
        return render_template("admin/login.html", form=form)

    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        """Выход из админ-панели."""
        logout_user()
        flash("Вы вышли из системы.", "info")
        return redirect(url_for("admin_login"))

    @app.route("/admin")
    @login_required
    def admin_dashboard():
        """Таблицы заявок и результатов аудита."""
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        audits = AuditResult.query.order_by(AuditResult.created_at.desc()).all()
        return render_template(
            "admin/dashboard.html", feedbacks=feedbacks, audits=audits
        )

    @app.post("/admin/feedback/<int:fid>/delete")
    @login_required
    def admin_feedback_delete(fid: int):
        """Удаление заявки обратной связи."""
        row = db.session.get(Feedback, fid)
        if row is None:
            abort(404)
        db.session.delete(row)
        db.session.commit()
        flash("Заявка удалена.", "info")
        return redirect(url_for("admin_dashboard"))

    @app.post("/admin/audit/<int:aid>/delete")
    @login_required
    def admin_audit_delete(aid: int):
        """Удаление записи диагностики потенциала (AuditResult)."""
        row = db.session.get(AuditResult, aid)
        if row is None:
            abort(404)
        db.session.delete(row)
        db.session.commit()
        flash("Запись аудита удалена.", "info")
        return redirect(url_for("admin_dashboard"))

    @app.post("/predict")
    def predict():
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        logger.info(
            "POST /predict: ip=%s ua=%s message_len=%s",
            request.remote_addr,
            (request.headers.get("User-Agent") or "")[:160],
            len(user_message),
        )
        if not user_message:
            logger.warning("POST /predict rejected: empty message")
            return jsonify({"answer": "Сообщение не получено"}), 400
        try:
            # Проксируем сообщение к FastAPI-боту на локальном порту 8000.
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"message": user_message},
                timeout=15
            )
            logger.info("FastAPI /chat response status=%s", response.status_code)
            response.raise_for_status()
            bot_data = response.json()
            bot_answer = (bot_data.get("answer") or "").strip()

            if is_unknown_answer(bot_answer):
                logger.info("Assistant fallback triggered for message: %s", user_message[:240])
                send_telegram_notification(
                    "🤖 Ассистент не уверен в ответе, нужен оператор\n\n"
                    f"Вопрос пользователя:\n{user_message}\n\n"
                    f"IP: {request.remote_addr or '—'}\n"
                    f"Контакт: {TELEGRAM_CONTACT_URL}"
                )
                return jsonify(
                    {
                        "answer": (
                            "Я не уверен в точном ответе. Передал ваш вопрос в поддержку, "
                            "мы свяжемся с вами в ближайшее время."
                        )
                    }
                )

            logger.info("POST /predict completed successfully")
            return jsonify({"answer": bot_answer or "Не удалось сформировать ответ"})
        except Exception as e:
            logger.exception("POST /predict failed: %s", e)
            notify_error(
                "Чат поддержки /predict",
                (
                    f"{type(e).__name__}: {e}; "
                    f"ip={request.remote_addr or '—'}; "
                    f"message={user_message[:240]}"
                ),
            )
            return jsonify({"answer": "Ошибка связи с ассистентом"}), 500    

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
