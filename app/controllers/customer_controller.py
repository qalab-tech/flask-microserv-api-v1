from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor

from app.db import get_db_connection, release_db_connection
from app.services.customer_service import get_customers, update_customer
from app.logger_config import setup_logger

logger = setup_logger("customer_controller")
customer_bp = Blueprint('customers', __name__)

@customer_bp.route('/', methods=['GET'])
def get_customers_route():
    """GET all customers"""
    return jsonify(get_customers())

# Read customer by ID
@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_route(customer_id):
    """GET customer by customer_id"""
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s;", (customer_id,))
    customer = cursor.fetchone()
    if customer:
        logger.info(f"Retrieved customer: {customer}")
        return jsonify(customer), 200
    else:
        logger.warning(f"Customer not found: ID={customer_id}")
        return jsonify({"error": "Customer not found"}), 404

    cursor.close()
    connection.close()

@customer_bp.route('/', methods=['POST'])
def create_new_customer():
    """Create new customer"""
    data = request.json
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        logger.warning("Invalid input: Name and address are required")
        return jsonify({"error": "Name and address are required"}), 400
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO customers (name, address) VALUES (%s, %s) RETURNING customer_id;",
        (name, address)
    )
    customer_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()
    logger.info(f"Customer created: ID={customer_id}, Name={name}, Address={address}")
    return jsonify({"customer_id": customer_id, "name": name, "address": address}), 201

@customer_bp.route('/<int:customer_id>', methods=['PATCH'])
def patch_customer_route(customer_id):
    """PATCH (partial update) method implementation"""
    data = request.json

    if not data:
        logger.warning(f"No data provided for customer ID {customer_id}")
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name')
    address = data.get('address')

    if not name and not address:
        logger.warning(f"Invalid input: at least one field (name or address) is required for customer ID {customer_id}")
        return jsonify({"error": "At least one field (name or address) is required"}), 400

    update_fields = []
    update_values = []

    if name:
        update_fields.append("name = %s")
        update_values.append(name)
    if address:
        update_fields.append("address = %s")
        update_values.append(address)

    update_values.append(customer_id)

    query = f"UPDATE customers SET {', '.join(update_fields)} WHERE customer_id = %s RETURNING customer_id;"

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query, tuple(update_values))
    updated_customer_id = cursor.fetchone()
    connection.commit()


    if updated_customer_id:
        logger.info(f"Customer updated: ID={customer_id}, Name={name}, Address={address}")
        return jsonify({"customer_id": customer_id, "name": name, "address": address}), 200
    else:
        logger.warning(f"Customer not found for update: ID={customer_id}")
        return jsonify({"error": "Customer not found"}), 404
    cursor.close()
    release_db_connection(connection)
    connection.close()
@customer_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer_route(customer_id):
    """Update customer"""
    data = request.json
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        logger.warning("Invalid input: Name and address are required")
        return jsonify({"error": "Name and address are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE customers SET name = %s, address = %s WHERE customer_id = %s RETURNING customer_id;",
        (name, address, customer_id)
    )
    updated_customer_id = cursor.fetchone()
    connection.commit()
    release_db_connection(connection)

    if updated_customer_id:
        logger.info(f"Customer updated: ID={customer_id}, Name={name}, Address={address}")
        return jsonify({"customer_id": customer_id, "name": name, "address": address}), 200
    else:
        logger.warning(f"Customer not found for update: ID={customer_id}")
        return jsonify({"error": "Customer not found"}), 404

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer_route(customer_id):
    """DELETE method"""
    connection = None
    cursor = None
    success = False

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM customers WHERE customer_id = %s RETURNING customer_id;", (customer_id,))
        deleted_customer_id = cursor.fetchone()

        if deleted_customer_id:
            connection.commit()
            success = True
            logger.info(f"Customer deleted: ID={customer_id}")
            return jsonify({"message": "Customer deleted"}), 200
        else:
            logger.warning(f"Customer not found for deletion: ID={customer_id}")
            return jsonify({"error": "Customer not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        if connection:  # Проверяем, было ли успешно установлено соединение
            connection.rollback()  # Откатываем изменения, если что-то пошло не так
            logger.error("Rollback performed due to an error.")

        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            if success:
                release_db_connection(connection)  # Возвращаем соединение в пул, только если операция прошла успешно

            else:
                # Если операция не прошла успешно, не возвращаем соединение в пул, чтобы избежать использования закрытого соединения
                logger.warning("Connection not returned to pool because of a failure.")
