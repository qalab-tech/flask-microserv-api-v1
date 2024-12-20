from app.repositories.customer_repository import fetch_all_customers, fetch_customer, insert_customer, \
    update_customer_in_db, patch_customer_in_db, delete_customer_in_db
from app.logger_config import setup_logger

logger = setup_logger("customer_service")


def get_customers():
    customers = fetch_all_customers()
    customers_len = len(customers)
    if not customers:
        logger.info("No customers found")
    logger.info(f"{customers_len} customers found")
    return customers


def get_customer_by_id(customer_id):
    customer = fetch_customer(customer_id)
    if customer is None:
        logger.info(f"No such customer with id {customer_id}")

    return customer


def create_customer(data):
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        logger.error("Name and address are required")
        return {"error": "Name and address are required"}, 400
    customer_id = insert_customer(name, address)
    logger.info(f"Customer with id={customer_id}, name={name} and address={address} is added")
    return {"customer_id": customer_id, "name": name, "address": address}, 201


def update_customer(customer_id, data):
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        return {"error": "Name and address are required"}, 400
    updated_customer_id = update_customer_in_db(customer_id, name, address)
    if updated_customer_id:
        logger.info(f"Customer with id={customer_id}, name={name} and address={address} updated successfully")
        return {"customer_id": customer_id, "name": name, "address": address}, 200
    else:
        logger.error(f"Customer with id={customer_id} not found")
        return {"error": "Customer not found"}, 404


def patch_customer(customer_id, data):
    name = data.get('name')
    address = data.get('address')
    if name is None and address is None:
        return {"error": "At least one field (name or address) is required"}, 400
    patched_customer_id = patch_customer_in_db(customer_id, name=name, address=address)
    if patched_customer_id:
        logger.info(f"Customer with id={customer_id} patched successfully")
        response_data = {"customer_id": customer_id}
        if name is not None:
            response_data["name"] = name
        if address is not None:
            response_data["address"] = address
        return response_data, 200
    else:
        logger.error(f"Customer with id={customer_id} not found")
        return {"error": "Customer not found"}, 404


def delete_customer(customer_id):
    deleted_customer_id = delete_customer_in_db(customer_id)
    if deleted_customer_id:
        logger.info(f"Customer with id={customer_id} deleted successfully")
        return {"message": "Customer deleted"}, 200
    else:
        logger.error(f"Customer with id={customer_id} not found")
        return {"error": "Customer not found"}, 404
