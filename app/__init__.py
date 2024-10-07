from flask import Flask
from app.controllers.customer_controller import customer_bp

app = Flask(__name__)

def create_app():
    # Register controllers
    app.register_blueprint(customer_bp)
    return app

