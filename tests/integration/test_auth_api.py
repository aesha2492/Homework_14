# tests/integration/test_auth_api.py


def test_register_success(client):  # Use the client fixture from conftest
    payload = {"email": "testuser@example.com", "password": "strongpass123"}
    response = client.post("/register", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "strongpass123"}
    r1 = client.post("/register", json=payload)
    assert r1.status_code in (200, 201)

    r2 = client.post("/register", json=payload)
    assert r2.status_code == 400


def test_login_success(client):
    # First register
    payload = {"email": "loginuser@example.com", "password": "strongpass123"}
    r1 = client.post("/register", json=payload)
    assert r1.status_code in (200, 201)

    # Then login
    r2 = client.post("/login", json=payload)
    assert r2.status_code == 200
    data = r2.json()
    assert "access_token" in data


def test_login_invalid_credentials(client):
    payload = {"email": "nosuch@example.com", "password": "whatever"}
    r = client.post("/login", json=payload)
    assert r.status_code == 401
