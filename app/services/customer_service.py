# /app/services/customer_service.py
from app.repositories.customer_repository import get_all_customers, update_customer_db
from app.logger_config import setup_logger

logger = setup_logger("customer_service")

def get_customers():
    return get_all_customers()

def update_customer(customer_id, data):
    # Input data validation
    if not data.get('name') and not data.get('address'):
        return {"error": "No data to update"}, 400
    return update_customer_db(customer_id, data)
