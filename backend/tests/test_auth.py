SIGNUP = {"full_name": "Asha Verma", "email": "Asha.Verma@example.com", "password": "secret-pass-1"}


def test_signup_returns_token_and_user(client):
    r = client.post("/api/auth/signup", json=SIGNUP)
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == "asha.verma@example.com"
    assert body["user"]["preferred_language"] == "en"


def test_duplicate_email_rejected_case_insensitively(client):
    client.post("/api/auth/signup", json=SIGNUP)
    r = client.post("/api/auth/signup", json={**SIGNUP, "email": "ASHA.VERMA@example.com"})
    assert r.status_code == 409


def test_short_password_rejected(client):
    r = client.post("/api/auth/signup", json={**SIGNUP, "password": "short"})
    assert r.status_code == 422


def test_login_and_me(client):
    client.post("/api/auth/signup", json=SIGNUP)
    r = client.post("/api/auth/login", json={"email": SIGNUP["email"], "password": SIGNUP["password"]})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Asha Verma"


def test_wrong_password(client):
    client.post("/api/auth/signup", json=SIGNUP)
    r = client.post("/api/auth/login", json={"email": SIGNUP["email"], "password": "wrong-password"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_update_language(client, auth_headers):
    r = client.patch("/api/auth/me", json={"preferred_language": "hi"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["preferred_language"] == "hi"
    bad = client.patch("/api/auth/me", json={"preferred_language": "fr"}, headers=auth_headers)
    assert bad.status_code == 422


def test_dev_bypass(client):
    r = client.post("/api/auth/dev-bypass")
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == "rohit.demo@example.com"

