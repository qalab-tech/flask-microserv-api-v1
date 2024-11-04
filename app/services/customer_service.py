from app.repositories.customer_repository import fetch_all_customers, fetch_customer, insert_customer, \
    update_customer_in_db, delete_customer_in_db
from app.logger_config import setup_logger
from flask import abort, make_response, jsonify

logger = setup_logger("customer_service")


def get_customers():
    """Get all customers"""
    customers = fetch_all_customers()
    customers_len = len(customers)
    if not customers:
        logger.info("No customers found")
    logger.info(f"{customers_len} customers found")
    return customers


def get_customer_by_id(customer_id):
    customer = fetch_customer(customer_id)
    if not customer:
        logger.error(f"No such customer with id {customer_id}")
        abort(make_response(jsonify({'error': f'No such customer with id={customer_id}'}), 404))
    logger.info(f"Customer with id={customer_id} found in database")
    return customer


def create_customer(data):
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        logger.error("Name and address are required")
        abort(make_response(jsonify({'error': 'Name and address are required'}), 400))
    customer_id = insert_customer(name, address)
    logger.info(f"Customer with id={customer_id}, name={name} and address={address} is added")
    return {"customer_id": customer_id, "name": name, "address": address}, 201


def update_customer(customer_id, data):
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        logger.error("Name and address are required")
        abort(make_response(jsonify({'error': 'Name and address are required'}), 400))
    updated_customer_id = update_customer_in_db(customer_id, name, address)
    if not updated_customer_id:
        logger.error(f"Customer with id={customer_id} not found")
        abort(make_response(jsonify({'error': f'Customer with id={customer_id} not found'}), 404))
    logger.info(f"Customer with id={customer_id}, name={name} and address={address} updated successfully")
    return {"customer_id": customer_id, "name": name, "address": address}, 200


def delete_customer(customer_id):
    deleted_customer_id = delete_customer_in_db(customer_id)
    if not deleted_customer_id:
        logger.error(f"Customer with id={customer_id} not found")
        abort(make_response(jsonify({'error': f'Customer with id={customer_id} not found'}), 404))
    return {"message": "Customer deleted"}, 200



