from flask import Flask
from app.controllers.customer_controller import customers_bp


def create_app():
    app = Flask(__name__)

    # Register BluePrint
    app.register_blueprint(customers_bp, url_prefix='/api/v1')

    return app


# Export env variable app for Gunicorn
app = create_app()
