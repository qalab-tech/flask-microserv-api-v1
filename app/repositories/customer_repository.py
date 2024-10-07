# /app/repositories/customer_repository.py
from app.db import get_db_connection
from app.db import release_db_connection
from app.logger_config import setup_logger

logger = setup_logger("customer_repository")

def get_all_customers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    release_db_connection(connection)
    # connection.close()
    logger.info(f"Retrieved {len(customers)} customers")
    return customers

def update_customer_db(customer_id, data):
    connection = get_db_connection()
    cursor = connection.cursor()
    if data.get('name'):
        cursor.execute("UPDATE customers SET name = %s WHERE customer_id = %s", (data['name'], customer_id))
        logger.info(f"Customer's name updated successfully, new name is {data['name']}")
    if data.get('address'):
        cursor.execute("UPDATE customers SET address = %s WHERE customer_id = %s", (data['address'], customer_id))
        logger.info(f"Customer's address updated successfully, new address is {data['address']}")
    connection.commit()
    release_db_connection(connection)
    connection.close()


# def create_customer_db():
#     return None
"""TO-DO!"""