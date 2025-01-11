import sys
import os
import json

# Add the directory containing 'freddy_fazber.py' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from freddy_fazber import app, db, User, Order, Pizza, Topping, OrderItem

import pytest
from freddy_fazber import app, db


@pytest.fixture
def client():
    # Create a test client for the Flask app
    with app.test_client() as client:
        # Set up the app context and initialize the database
        with app.app_context():
            db.create_all()  # Create all tables in the test database
            yield client  # This allows tests to use the client
            db.drop_all()  # Clean up the database after tests


def test_create_order(client):
    # Przygotowanie danych
    user = User(
        username="test_user",
        email="test@example.com",
        password="testpassword123",
        name="Test",
        surname="User",
        telephone_number="1234567890",
    )
    db.session.add(user)
    db.session.commit()

    payload = {
        "user_id": user.id,
        "location": "123 Main Street",
        "delivery_time": "2025-01-11 18:30:00",
        "items": [{"pizza_id": 1, "topping_ids": [1, 2]}],
    }

    # Wysłanie żądania POST do /order
    response = client.post(
        "/order", data=json.dumps(payload), content_type="application/json"
    )

    # Sprawdzanie odpowiedzi
    assert response.status_code == 201
    assert response.json["message"] == "Order created successfully"
