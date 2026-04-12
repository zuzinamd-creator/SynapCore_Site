# -*- coding: utf-8 -*-
"""
Модели SQLAlchemy для SQLite.
Таблицы: пользователи админки, заявки, согласия на cookies, результаты диагностики потенциала.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """Учётная запись администратора (Flask-Login)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        """Хеширование пароля перед сохранением."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля при входе."""
        return check_password_hash(self.password_hash, password)


class Feedback(db.Model):
    """Заявки из формы обратной связи на лендинге."""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CookieConsent(db.Model):
    """Фиксация согласия с использованием cookies (IP и дата)."""

    __tablename__ = "cookie_consents"

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AuditResult(db.Model):
    """Результаты пошаговой диагностики потенциала автоматизации (ответы и оценка)."""

    __tablename__ = "audit_results"

    id = db.Column(db.Integer, primary_key=True)
    # JSON со строковыми ключами q1, q2, q3 (выбранные варианты)
    answers_json = db.Column(db.Text, nullable=False)
    # Рассчитанный потенциал автоматизации, % (для графика и отчётов)
    automation_score = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
