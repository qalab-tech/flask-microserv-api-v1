import requests
import pytest
from tests.utils.decorators import handle_requests_exceptions
import os
from dotenv import load_dotenv

load_dotenv()

# Flask microservice Base URL

BASE_URL = os.getenv("CUSTOMERS_BASE_URL")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")


@handle_requests_exceptions
def test_options_customers(auth_token):
    """Test OPTIONS customers endpoint"""  # Expected response example
    # expected_methods = 'OPTIONS, GET, POST, HEAD'
    headers = {"Authorization": auth_token}
    response = requests.options(BASE_URL, headers=headers)
    # connection = response.headers['Connection']  # Convert both strings to sets and compare
    assert response.status_code == 200
    # assert connection == 'keep-alive'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@handle_requests_exceptions
def test_options_customer(auth_token, new_customer_data):
    """Test OPTIONS customer endpoint"""
    expected_methods = 'PATCH, PUT, DELETE, GET, OPTIONS, HEAD'
    headers = {"Authorization": auth_token}
    response = requests.post(BASE_URL, json=new_customer_data, headers=headers)
    customer = response.json()
    customer_id = customer['customer_id']
    response = requests.options(f"{BASE_URL}/{customer_id}", headers=headers)
    actual_methods = response.headers['Allow']
    assert set(actual_methods.split(', ')) == set(
        expected_methods.split(', ')), f"Expected: {expected_methods}, but got: {actual_methods}"
    # Delete new created customer
    requests.delete(f"{BASE_URL}/{customer_id}", headers=headers)


@handle_requests_exceptions
def test_head(auth_token):
    # Test HEAD HTTP Method
    headers = {"Authorization": auth_token}
    response = requests.options(BASE_URL, headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@handle_requests_exceptions
def test_create_customer(new_customer_data, auth_token, db_connection):
    """Test create new customer"""
    headers = {"Authorization": auth_token}
    response = requests.post(BASE_URL, json=new_customer_data, headers=headers)
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    customer = response.json()
    assert "customer_id" in customer
    assert customer["name"] == new_customer_data["name"]
    assert customer["address"] == new_customer_data["address"]
    # Check data in Postgres database
    cursor = db_connection.cursor()
    query = "SELECT name, address FROM customers WHERE customer_id = %s"
    cursor.execute(query, (customer["customer_id"],))
    db_data = cursor.fetchone()
    assert db_data is not None, "Customer was not found in the database"
    assert db_data[0] == new_customer_data["name"], "Name does not match database"
    assert db_data[1] == new_customer_data["address"], "Address does not match database"
    # Delete new created customer
    requests.delete(f"{BASE_URL}/{customer['customer_id']}", headers=headers)


@handle_requests_exceptions
def test_get_all_customers(auth_token):
    """Test all customers"""
    headers = {"Authorization": auth_token}
    response = requests.get(BASE_URL, headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert isinstance(response.json(), list)


@handle_requests_exceptions
def test_get_customer(new_customer, auth_token):
    """Test get customer by id"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    customer = response.json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert isinstance(customer, dict)


@handle_requests_exceptions
def test_update_customer(new_customer, new_customer_data, auth_token, db_connection):
    """Test UPDATE customer"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    updated_data = {
        "name": new_customer_data["name"],
        "address": new_customer_data["address"]
    }

    # Send PUT request to update customer
    response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    # Check API response
    updated_customer = response.json()
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Verify in the database
    cursor = db_connection.cursor()
    cursor.execute("SELECT name, address FROM customers WHERE customer_id = %s", (customer_id,))
    db_customer = cursor.fetchone()  # Example: ('Updated Name', 'Updated Address')
    assert db_customer is not None, "Customer not found in database"
    assert db_customer[0] == updated_data["name"]
    assert db_customer[1] == updated_data["address"]


@pytest.mark.parametrize("update_data, field, new_value", [
    ({"name": "Updated Name"}, "name", "Updated Name"),  # TestCase: patch name
    ({"address": "New Address 123"}, "address", "New Address 123")  # TestCase: patch address
])
@handle_requests_exceptions
def test_patch_customer_parametrized(new_customer, auth_token, update_data, field, new_value, db_connection):
    """Test PATCH customer with parameterized cases for updating name or address"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}

    # Send PATCH request to update customer
    response = requests.patch(f"{BASE_URL}/{customer_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    # Check API response
    updated_customer = response.json()
    assert updated_customer[field] == new_value

    # Verify in the database
    cursor = db_connection.cursor()
    cursor.execute("SELECT name, address FROM customers WHERE customer_id = %s", (customer_id,))
    db_customer = cursor.fetchone()
    assert db_customer is not None, "Customer not found in database"

    # Check the updated field
    if field == "name":
        assert db_customer[0] == new_value  # Check updated name
    elif field == "address":
        assert db_customer[1] == new_value  # Check updated address


@handle_requests_exceptions
def test_delete_customer(new_customer, auth_token, db_connection):
    """Test DELETE customer"""
    customer_id = new_customer["customer_id"]
    headers = {"Authorization": auth_token}
    response = requests.delete(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    # Check that customer is deleted
    response = requests.get(f"{BASE_URL}/{customer_id}", headers=headers)
    assert response.status_code == 404

    # Verify in database
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    assert cursor.fetchone() is None
