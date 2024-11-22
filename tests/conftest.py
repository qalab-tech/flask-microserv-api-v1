import pytest
import psycopg2
import requests
import os
from faker.proxy import Faker
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

# Create Faker Object for fake customer data
fake = Faker()

# Load ENVs
BASE_URL = os.getenv("CUSTOMERS_BASE_URL")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
CUSTOMERS_DATABASE_URL = os.getenv("CUSTOMERS_DATABASE_URL")


@pytest.fixture(scope="function")
def db_connection():
    """Get database connection"""
    connection = psycopg2.connect(CUSTOMERS_DATABASE_URL)
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def auth_token():
    """Get auth token"""
    url = f"{AUTH_BASE_URL}/auth/login"  # authorization URL
    credentials = {"username": "test", "password": "test"}
    response = requests.post(url, json=credentials)
    response.raise_for_status()
    token = response.json()["token"]
    return f"Bearer {token}"


@pytest.fixture
def new_customer_data():
    """Fake customer data generation"""
    return {"name": fake.name(), "address": fake.address()}


@pytest.fixture
def new_customer(new_customer_data, auth_token):
    """Create a new customer in the database and delete after the test"""
    headers = {"Authorization": auth_token}
    response = requests.post(BASE_URL, json=new_customer_data, headers=headers)
    assert response.status_code == 201
    customer = response.json()
    yield customer
    # Delete customer after test
    requests.delete(f"{BASE_URL}/{customer['customer_id']}", headers=headers)
