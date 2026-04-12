# -*- coding: utf-8 -*-
"""
Flask-WTF формы: обратная связь и вход в админку.
Все поля с валидацией и CSRF по умолчанию.
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    """Форма связи на лендинге (имя, email, компания, сообщение)."""

    name = StringField(
        "Имя",
        validators=[DataRequired(message="Укажите имя."), Length(max=120)],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Укажите email."),
            Email(message="Некорректный email."),
            Length(max=120),
        ],
    )
    company = StringField(
        "Компания",
        validators=[DataRequired(message="Укажите компанию."), Length(max=200)],
    )
    message = TextAreaField(
        "Сообщение",
        validators=[DataRequired(message="Введите сообщение."), Length(max=5000)],
    )
    submit = SubmitField("Отправить")


class AdminLoginForm(FlaskForm):
    """Форма входа в админ-панель."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email."),
            Email(message="Некорректный email."),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(message="Введите пароль.")],
    )
    submit = SubmitField("Войти")
