from app.db import get_db_connection, release_db_connection
from app.logger_config import setup_logger
import psycopg2.extras
from app.performance_monitor import log_duration

logger = setup_logger("customer_repository")


@log_duration
def fetch_all_customers():
    connection = get_db_connection()
    cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)  # Use RealDictCursor to get dictionaries
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()  # Get list of dictionaries
    cursor.close()
    release_db_connection(connection)
    return customers


@log_duration
def fetch_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            logger.info(f"No customer found with id {customer_id}")
        logger.info(f"Customer with id={customer_id} found in database")
        return customer
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        cursor.close()
        release_db_connection(connection)


@log_duration
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


@log_duration
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


@log_duration
def patch_customer_in_db(customer_id, name=None, address=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Create query parts dynamically
    fields_to_update = []
    values = []
    if name is not None:
        fields_to_update.append("name = %s")
        values.append(name)

    if address is not None:
        fields_to_update.append("address = %s")
        values.append(address)
    # Add customer_id to SQL query parameters
    values.append(customer_id)
    # Format SQL query
    sql_query = f"UPDATE customers SET {', '.join(fields_to_update)} WHERE customer_id = %s RETURNING customer_id;"
    # Execute query
    cursor.execute(sql_query, tuple(values))
    updated_customer_id = cursor.fetchone()
    connection.commit()
    cursor.close()
    release_db_connection(connection)
    return updated_customer_id


@log_duration
def delete_customer_in_db(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = %s RETURNING customer_id;", (customer_id,))
    deleted_customer_id = cursor.fetchone()
    connection.commit()
    cursor.close()
    release_db_connection(connection)
    return deleted_customer_id
