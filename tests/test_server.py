import jwt
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.api import app, create_jwt, JWT_SECRET_KEY, JWT_ALGORITHM

client = TestClient(app)

@pytest.fixture()
def valid_token():
    return create_jwt("test_user")

@pytest.fixture()
def expired_token():
    payload = {
        "user_id": "test_user",
        "exp": datetime.now() - timedelta(days=1)
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.mark.skip(reason="Skipping the test")
def test_github_login():
    response = client.get("/github-login")
    assert response.status_code == 302
    assert "https://github.com/login/oauth/authorize" in response.headers["location"]


@pytest.mark.skip(reason="Skipping the test")
def test_verify_token(valid_token):
    headers = {
        "Authorization" : f"Bearer {valid_token}"
    }
    response = client.get("/verify-token", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert "email" in response.json()


def test_verify_token_invalid(expired_token):
    headers = {
        "Authorization": f"Bearer {expired_token}"
    }

    response = client.get("/verify-token", headers=headers)
    assert response.status_code == 401


def test_get_recommendations_unauthorized():
    response = client.post("/api/recommendations/")
    assert response.status_code == 401
