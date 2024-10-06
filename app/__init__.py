# /app/__init__.py
from flask import Flask
from app.controllers.customer_controller import customer_bp

def create_app():
    app = Flask(__name__)

    # Register controllers
    app.register_blueprint(customer_bp)

    return app
