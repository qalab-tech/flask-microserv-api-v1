# /app/services/customer_service.py
from app.repositories.customer_repository import get_all_customers, update_customer_db, create_customer_db
from app.logger_config import setup_logger

logger = setup_logger("customer_service")


def get_customers():
    customers = get_all_customers()
    if not customers:
        logger.info("No customers found")
    return customers


def update_customer(customer_id, data):
    # Data validation
    validation_error = validate_customer_data(data)
    if validation_error:
        logger.error(f"Update error for customer {customer_id}: {validation_error}")
        return {"error": validation_error}, 400

    # Update logic
    result = update_customer_db(customer_id, data)
    if result:
        logger.info(f"Customer {customer_id} updated successfully")
        return result
    else:
        logger.error(f"Failed to update customer {customer_id}")
        return {"error": "Update failed"}, 500


def create_customer(data):
    # Data validation before creation
    validation_error = validate_customer_data(data)
    if validation_error:
        logger.error(f"Creation error: {validation_error}")
        return {"error": validation_error}, 400

    # Creation logic
    result = create_customer_db(data)
    if result:
        logger.info(f"Customer created successfully")
        return result
    else:
        logger.error(f"Customer creation failed")
        return {"error": "Creation failed"}, 500


def validate_customer_data(data):
    # E-mail validation
    if 'name' not in data or not data['name']:
        return "Customer name is required"
    if 'email' in data and '@' not in data['email']:
        return "Invalid email format"
    return None
