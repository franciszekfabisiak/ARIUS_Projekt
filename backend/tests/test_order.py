from freddy_fazber import app  # Import your app
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_create_order(client):
    response = client.post(
        "/order",
        json={
            "user_id": 1,
            "location": "123 Test Street",
            "delivery_time": "2025-01-15 12:30:00",
            "items": [{"pizza_id": 1, "topping_ids": [1]}],
        },
    )
    assert response.status_code == 201
    data = response.json
    assert data["message"] == "Order created successfully"
    assert "order_id" in data


def test_get_pizzas(client):
    response = client.get("/pizzas")
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert all("id" in pizza and "name" in pizza for pizza in data)


def test_get_toppings(client):
    response = client.get("/toppings")
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert all("id" in topping and "name" in topping for topping in data)


def test_get_orders(client):
    # Make sure the user exists in the database and has orders
    user_id = 1
    response = client.get(f"/orders/{user_id}")
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    if data:
        assert "order_id" in data[0]
        assert "created_at" in data[0]
        assert "items" in data[0]


def test_rate_pizzeria(client):
    response = client.post(
        "/rate",
        json={
            "user_id": 1,
            "order_id": 1,
            "rating": 5,
            "comment": "Great pizza!",
        },
    )
    assert response.status_code == 201
    data = response.json
    assert data["message"] == "Thank you for your feedback!"


def test_update_user(client):
    # Make sure the user exists in the database
    user_id = 1
    response = client.put(
        f"/update_user/{user_id}",
        json={
            "name": "Updated Name",
            "surname": "Updated Surname",
            "telephone_number": "9998887777",
        },
    )
    assert response.status_code == 200
    data = response.json
    assert data["name"] == "Updated Name"
    assert data["surname"] == "Updated Surname"
    assert data["telephone_number"] == "9998887777"


def test_register_valid_data(client):
    response = client.post(
        "/register",
        json={
            "username": "new_user2",
            "email": "new_use2r@example.com",
            "password": "password1223",
            "name": "New2",
            "surname": "Use2r",
            "telephone_number": "2551234567",
        },
    )
    assert response.status_code == 201
    data = response.json
    assert data["message"] == "User created successfully"


def test_register_missing_fields(client):
    response = client.post(
        "/register",
        json={
            "username": "invalid_user",
            "email": "invalid_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    data = response.json
    assert (
        data["message"]
        == "Invalid input. Username, email, password, name, surname, and telephone_number are required."
    )


def test_login_valid_user(client):
    response = client.post(
        "/login",
        json={
            "username": "john_doe",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Login successful"
    assert "userId" in data


def test_login_invalid_user(client):
    response = client.post(
        "/login",
        json={
            "username": "non_existent_user",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    data = response.json
    assert data["message"] == "Invalid credentials"


def test_create_order_missing_data(client):
    response = client.post(
        "/order",
        json={
            "user_id": 1,
            "items": [
                {"pizza_id": 1, "topping_ids": [1]}
            ],  # Missing 'location' and 'delivery_time'
        },
    )
    assert response.status_code == 400
    data = response.json
    assert data["message"] == "Invalid input"


def test_rate_pizzeria_missing_fields(client):
    response = client.post(
        "/rate",
        json={
            "user_id": 1,
            "order_id": 1,
        },
    )
    assert response.status_code == 400
    data = response.json
    assert data["message"] == "Invalid input"
