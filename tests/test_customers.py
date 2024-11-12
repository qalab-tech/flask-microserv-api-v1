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


# def test_options_customers(auth_token):
#     """Test OPTIONS customers endpoint"""
#     # Expected response example
#     expected_methods = 'OPTIONS, GET, POST, HEAD'
#     headers = {"Authorization": auth_token}
#     response = requests.options(BASE_URL, headers=headers)
#     actual_methods = response.headers['Allow']
#     # Convert both strings to sets and compare
#     assert set(actual_methods.split(', ')) == set(expected_methods.split(', ')), f"Expected: {expected_methods}, but got: {actual_methods}"


def test_options_customer(auth_token, new_customer_data):
    """Test OPTIONS customer endpoint"""
    expected_methods = 'OPTIONS, GET, POST, HEAD, PATCH'
    headers = {"Authorization": auth_token}
    customer = requests.post(BASE_URL, json=new_customer_data, headers=headers)
    customer_id = customer['customer_id']
    response = requests.options(f"{BASE_URL}/{customer_id}", headers=headers)
    actual_methods = response.headers['Allow']
    assert set(actual_methods.split(', ')) == set(
        expected_methods.split(', ')), f"Expected: {expected_methods}, but got: {actual_methods}"
    # Delete new created customer
    requests.delete(f"{BASE_URL}/{customer_id}", headers=headers)


def test_head(auth_token):
    # Test HEAD HTTP Method
    headers = {"Authorization": auth_token}
    response = requests.options(BASE_URL, headers=headers)
    assert response.status_code == 200


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


@pytest.mark.parametrize("update_data, field, new_value", [
    ({"name": "Updated Name"}, "name", "Updated Name"),  # Тест-кейс: обновление имени
    ({"address": "New Address 123"}, "address", "New Address 123")  # Тест-кейс: обновление адреса
])
def test_patch_customer_parametrized(new_customer, auth_token, update_data, field, new_value):
    """Test PATCH customer with parameterized cases for updating name or address"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.patch(f"{BASE_URL}/{customer_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_customer = response.json()
    assert updated_customer[field] == new_value
    # Check that other fields remain unchanged
    # for key, value in new_customer.items():
    #     if key != field:
    #         assert updated_customer[key] == value
    # Additional verification: we receive customer data and check for updates
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 200
    customer = response.json()
    assert type(customer) == dict
    # assert customer[field] == new_value
    # for key, value in new_customer.items():
    #     if key != field:
    #         assert customer[key] == value


def test_delete_customer(new_customer, auth_token):
    """Test DELETE customer"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.delete(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 200
    # Check that customer is deleted
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 404
