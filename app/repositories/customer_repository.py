from app.db import get_db_connection, release_db_connection
from app.logger_config import setup_logger

logger = setup_logger("customer_repository")

def fetch_all_customers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    release_db_connection(connection)
    return customers

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
