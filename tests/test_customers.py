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

def test_update_customer():
    # Create new customer for update
    new_customer_data = {
        "name": fake.name(),
        "address": "123 Test St"
    }
    create_response = requests.post(f"{BASE_URL}", json=new_customer_data)
    assert create_response.status_code == 201

    # Get customer_id of created customer
    customer_id = create_response.json()["customer_id"]

    # Customer data update
    updated_data = {"name": fake.name(), "address": "Updated Address"}
    update_response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data)
    assert update_response.status_code == 200

    # Check customer updated successfully
    updated_customer = update_response.json()
    assert updated_customer["customer_id"] == customer_id
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Check database update
    db_response = requests.get(f"{BASE_URL}/{customer_id}")
    assert db_response.status_code == 200
    customer = db_response.json()
    assert customer["name"] == updated_data["name"]
    assert customer["address"] == updated_data["address"]


def test_delete_customer():
    # DELETE customer Test
    customer_data = {
        "name": "Test Customer",
        "address": "123 Test St"
    }
    create_response = requests.post(f"{BASE_URL}", json=customer_data)
    assert create_response.status_code == 201

    # Get created customer_id
    customer_id = create_response.json()["customer_id"]

    # Delete customer testing
    delete_response = requests.delete(f"{BASE_URL}/{customer_id}")
    assert delete_response.status_code == 200