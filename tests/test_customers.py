import requests
import pytest
from faker.proxy import Faker
import os

fake = Faker()

# Flask microservice Base URL
# BASE_URL = os.getenv("BASE_URL")
BASE_URL = "http://127.0.0.1:5000/api/v1/customers"


# Fixture for customer data creation
@pytest.fixture
def new_customer_data():
    return {"name": fake.name(), "address": fake.address()}


# Fixture to create a new customer in database
@pytest.fixture
def new_customer(new_customer_data):
    response = requests.post(BASE_URL, json=new_customer_data)
    assert response.status_code == 201
    customer = response.json()
    yield customer  # get customer data for using in tests
    # Delete customer after all tests
    requests.delete(f"{BASE_URL}/{customer['customer_id']}")


# New customer creation test
def test_create_customer(new_customer_data):
    """Create new customer test"""
    response = requests.post(BASE_URL, json=new_customer_data)
    assert response.status_code == 201
    customer = response.json()
    assert "customer_id" in customer
    assert customer["name"] == new_customer_data["name"]
    assert customer["address"] == new_customer_data["address"]
    # Remove created customer
    requests.delete(f"{BASE_URL}/{customer['customer_id']}")


def test_get_all_customers():
    """GET all customers test"""
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_customer(new_customer):
    """Test get customer by id"""
    customer_id = new_customer["customer_id"]
    response = requests.get(f"{BASE_URL}/{customer_id}")
    customer = response.json()
    assert response.status_code == 200
    assert isinstance(customer, dict)


def test_update_customer(new_customer, new_customer_data):
    """Test UPDATE customer"""
    customer_id = new_customer["customer_id"]

    # New customer data for update
    updated_data = {
        "name": new_customer_data["name"],
        "address": new_customer_data["address"]
    }

    # Send UPDATE request
    response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data)
    assert response.status_code == 200

    # Check of correct data UPDATE
    updated_customer = response.json()
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Additional UPDATE check
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200
    customer = response.json()
    assert customer["name"] == updated_data["name"]
    assert customer["address"] == updated_data["address"]


def test_delete_customer(new_customer):
    """Test DELETE customer"""
    customer_id = new_customer["customer_id"]
    # Delete customer
    response = requests.delete(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200
    # Check the customer doesn't exist
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 404
