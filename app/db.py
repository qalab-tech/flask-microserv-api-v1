import psycopg2
from psycopg2 import pool
import os
from app.logger_config import setup_logger

logger = setup_logger("db_connection")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://customers_user:MBVf3JDWSsupmsV9LQf19YfuFIE5Nbpf@dpg-crpa9dqj1k6c73c2jt3g-a.oregon-postgres.render.com/customers_jxqa")

# Init Pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 50, DATABASE_URL)  # Увеличил maxconn до 50
    if connection_pool:
        logger.info("Connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating connection pool: {str(e)}")
    raise

def get_db_connection():
    """Get connection from pool"""
    try:
        connection = connection_pool.getconn()
        if connection:
            logger.info("Successfully connected to the database")
            return connection
    except Exception as e:
        logger.error(f"Error getting connection from pool: {str(e)}")
        raise

def release_db_connection(connection):
    """Return connection to pool"""
    try:
        if connection:
            connection_pool.putconn(connection)
            logger.info("Connection returned to pool")
    except Exception as e:
        logger.error(f"Error releasing connection: {str(e)}")

def close_all_connections():
    """Close all connections from pool"""
    try:
        if connection_pool:
            connection_pool.closeall()
            logger.info("All connections in the pool closed")
    except Exception as e:
        logger.error(f"Error closing all connections: {str(e)}")

