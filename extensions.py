# -*- coding: utf-8 -*-
"""
Общие расширения Flask без циклических импортов (БД, Login Manager).
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Экземпляр SQLAlchemy; инициализация в create_app()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "admin_login"
login_manager.login_message = "Войдите в панель администратора."
