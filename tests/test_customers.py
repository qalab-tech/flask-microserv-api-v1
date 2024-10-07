from venv import create
import requests
import pytest
import yaml
from faker.proxy import Faker
from random import randrange

fake = Faker()


# Reading configuration from config.yaml
with open("tests/pytests_config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Flask microservice Base URL
BASE_URL = config["Base Application URL"]

@pytest.fixture
def new_customer_data():
    return {"name": fake.name(), "address": fake.address()}

@pytest.fixture
def new_customer(new_customer_data):
    # New customer creation fixture
    data = new_customer_data
    response = requests.post(BASE_URL, json=data)
    assert response.status_code == 201
    return response.json()  # Return new customer data

# Microservice TestCases

def test_get_all_customers():
    # Test retrieve all customers
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Check response is list instance

def test_create_customer(new_customer_data):
    # Test create new customer
    data = new_customer_data
    response = requests.post(BASE_URL, json=data)
    customer = response.json()
    assert response.status_code == 201
    assert "customer_id" in customer
    assert customer["name"] == data["name"]
    assert customer["address"] == data["address"]

def test_get_customer():
    # Test retrieve a customer by it's customer_id
    customer_id = str(randrange(3, 9))
    response = requests.get(f"{BASE_URL}/{customer_id}")
    customer = response.json()
    assert response.status_code == 200
    assert "customer_id" in customer
    assert "name" in customer
    assert "address" in customer

def test_update_customer(new_customer):
    # Test customer update
    customer_id = new_customer["customer_id"]
    updated_data = {"name": fake.name(), "address": "Updated Address"}
    response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data)
    assert response.status_code == 200
    updated_customer = response.json()
    assert updated_customer["customer_id"] == customer_id
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Database Update validation
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200
    customer = response.json()
    assert customer["name"] == updated_data["name"]
    assert customer["address"] == updated_data["address"]

def test_delete_customer():
    # Test Delete Customer
    customer_id = str(randrange(1, 1000))
    response = requests.delete(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted"
    # Test delete non-existing (already deleted) customer
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"