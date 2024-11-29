from flask import Flask
from app.controllers.customer_controller import customers_bp
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    PrometheusMetrics(app)
    # Register BluePrint
    app.register_blueprint(customers_bp, url_prefix='/api/v1')

    return app


# Export env variable app for Gunicorn
app = create_app()
