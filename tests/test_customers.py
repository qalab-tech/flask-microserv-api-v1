import requests
import pytest
from faker.proxy import Faker
import os

fake = Faker()

# Flask microservice Base URL
BASE_URL = os.getenv("CUSTOMERS_BASE_URL", "http://192.168.88.18:5000/api/v1/customers")


@pytest.fixture(scope="session")
def auth_token():
    """Get auth token"""
    url = "http://192.168.88.18:5001/auth/login"  # authorization URL
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


def test_create_customer(new_customer_data, auth_token):
    """Test create new customer"""
    headers = {"Authorization": auth_token}
    response = requests.post(BASE_URL, json=new_customer_data, headers=headers)
    assert response.status_code == 201
    customer = response.json()
    assert "customer_id" in customer
    assert customer["name"] == new_customer_data["name"]
    assert customer["address"] == new_customer_data["address"]
    # Delete new created customer
    requests.delete(f"{BASE_URL}/{customer['customer_id']}", headers=headers)


def test_get_all_customers(auth_token):
    """Test all customers"""
    headers = {"Authorization": auth_token}
    response = requests.get(BASE_URL, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_customer(new_customer, auth_token):
    """Test get customer by id"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    customer = response.json()
    assert response.status_code == 200
    assert isinstance(customer, dict)


def test_update_customer(new_customer, new_customer_data, auth_token):
    """Test UPDATE customer"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    updated_data = {
        "name": new_customer_data["name"],
        "address": new_customer_data["address"]
    }
    response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    updated_customer = response.json()
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Additional data update check
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 200
    customer = response.json()
    assert customer["name"] == updated_data["name"]
    assert customer["address"] == updated_data["address"]


def test_delete_customer(new_customer, auth_token):
    """Test DELETE customer"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.delete(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 200
    # Check that customer is deleted
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 404
