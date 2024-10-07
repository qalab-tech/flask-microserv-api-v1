from flask import Flask
from app.controllers.customer_controller import customer_bp  # Импортируем Blueprints

def create_app():
    app = Flask(__name__)

    # Регистрируем Blueprints
    app.register_blueprint(customer_bp, url_prefix='/api/v1/customers')  # Префикс можно установить здесь

    return app


