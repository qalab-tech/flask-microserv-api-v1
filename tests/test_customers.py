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

# Фикстура для создания новых данных для клиента
@pytest.fixture
def new_customer_data():
    return {"name": fake.name(), "address": fake.address()}

# Фикстура для создания нового клиента в базе
@pytest.fixture
def new_customer(new_customer_data):
    response = requests.post(BASE_URL, json=new_customer_data)
    assert response.status_code == 201
    customer = response.json()
    yield customer  # Возвращаем данные клиента для использования в тестах
    # После завершения теста удаляем клиента
    requests.delete(f"{BASE_URL}/{customer['customer_id']}")

# Тест получения всех клиентов
def test_get_all_customers():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Тест создания нового клиента
def test_create_customer(new_customer_data):
    response = requests.post(BASE_URL, json=new_customer_data)
    assert response.status_code == 201
    customer = response.json()
    assert "customer_id" in customer
    assert customer["name"] == new_customer_data["name"]
    assert customer["address"] == new_customer_data["address"]
    # Удаляем созданного клиента
    requests.delete(f"{BASE_URL}/{customer['customer_id']}")

# Тест получения клиента по ID
def test_get_customer(new_customer):
    customer_id = new_customer["customer_id"]
    response = requests.get(f"{BASE_URL}/{customer_id}")
    customer = response.json()
    assert response.status_code == 200
    assert isinstance(customer, list)


# Тест обновления данных клиента
def test_update_customer(new_customer, new_customer_data):
    customer_id = new_customer["customer_id"]

    # Получаем новые данные для обновления
    updated_data = {
        "name": new_customer_data["name"],
        "address": new_customer_data["address"]
    }

    # Отправляем запрос на обновление данных клиента
    response = requests.put(f"{BASE_URL}/{customer_id}", json=updated_data)
    assert response.status_code == 200

    # Проверяем, что данные клиента успешно обновлены
    updated_customer = response.json()
    assert updated_customer["name"] == updated_data["name"]
    assert updated_customer["address"] == updated_data["address"]

    # Дополнительно проверяем, что данные изменились в базе
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200
    customer = response.json()
    assert customer["name"] == updated_data["name"]
    assert customer["address"] == updated_data["address"]


# Тест удаления клиента
def test_delete_customer(new_customer):
    customer_id = new_customer["customer_id"]

    # Удаляем клиента
    response = requests.delete(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 200

    # Проверяем, что клиент больше не существует
    response = requests.get(f"{BASE_URL}/{customer_id}")
    assert response.status_code == 404