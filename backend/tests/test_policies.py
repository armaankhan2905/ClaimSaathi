from app.seed import seed


def _login_demo(client):
    from app.config import get_settings

    s = get_settings()
    r = client.post("/api/auth/login", json={"email": s.demo_email, "password": s.demo_password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_seed_is_idempotent(db_session):
    seed(db_session)
    user = seed(db_session)
    assert len(user.policies) == 2


def test_list_policies_for_demo_user(client, db_session):
    seed(db_session)
    r = client.get("/api/policies", headers=_login_demo(client))
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert names == ["Suraksha Health Plus", "DriveSure Comprehensive"]
    assert r.json()[0]["cover_since"] == "2022-03-12"


def test_other_users_cannot_see_or_delete_policy(client, db_session, auth_headers):
    seed(db_session)
    demo_policy_id = client.get("/api/policies", headers=_login_demo(client)).json()[0]["id"]
    assert client.get("/api/policies", headers=auth_headers).json() == []
    assert client.get(f"/api/policies/{demo_policy_id}", headers=auth_headers).status_code == 404
    assert client.delete(f"/api/policies/{demo_policy_id}", headers=auth_headers).status_code == 404


def test_delete_own_policy(client, db_session):
    seed(db_session)
    headers = _login_demo(client)
    pid = client.get("/api/policies", headers=headers).json()[0]["id"]
    assert client.delete(f"/api/policies/{pid}", headers=headers).status_code == 204
    assert len(client.get("/api/policies", headers=headers).json()) == 1
