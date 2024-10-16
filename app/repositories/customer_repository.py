from app.db import get_db_connection, release_db_connection
from app.logger_config import setup_logger
import psycopg2.extras

logger = setup_logger("customer_repository")

def fetch_all_customers():
    connection = get_db_connection()
    cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)  # Используем RealDictCursor для возврата словарей
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()  # Получаем список словарей
    release_db_connection(connection)
    return customers


def fetch_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            logger.info(f"No customer found with id {customer_id}")
            return None

        return customer
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def insert_customer(name, address):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO customers (name, address) VALUES (%s, %s) RETURNING customer_id;",
        (name, address)
    )
    customer_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    release_db_connection(connection)
    return customer_id

def update_customer_in_db(customer_id, name, address):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE customers SET name = %s, address = %s WHERE customer_id = %s RETURNING customer_id;",
        (name, address, customer_id)
    )
    updated_customer_id = cursor.fetchone()
    connection.commit()
    cursor.close()
    release_db_connection(connection)
    return updated_customer_id

def delete_customer_in_db(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = %s RETURNING customer_id;", (customer_id,))
    deleted_customer_id = cursor.fetchone()
    connection.commit()
    cursor.close()
    release_db_connection(connection)
    return deleted_customer_id
