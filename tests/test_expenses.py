from unittest.mock import patch
from app.main import app
from app.api.deps import get_current_user
from app.models.user import User


def override_get_current_user():
    return User(id=1, email="test@example.com", is_approver=False)


def test_create_expense(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    payload = {
        "amount": 2500.00,
        "category_id": 1,
        "description": "Квиток на літак до Лондона",
        "expense_date": "2026-09-13",
        "payment_details": "карта"
    }


    with patch("app.api.endpoints.analyze_expense_task.delay") as mock_celery:
        response = client.post("/expenses/", json=payload)

        assert response.status_code == 201

        data = response.json()
        assert data["amount"] == "2500.00"
        assert data["status"] == "pending"

        mock_celery.assert_called_once()

    # Очищаємо підміну після тесту, щоб не зламати інші перевірки
    app.dependency_overrides.clear()