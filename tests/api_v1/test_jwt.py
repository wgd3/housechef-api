from flask import url_for

from flask_jwt_extended import create_refresh_token

from housechef.database.models import User, Household


def test_get_tokens(client, db, user_factory):
    user = user_factory.create()
    db.session.add(user)
    db.session.commit()

    resp = client.post(
        url_for("api_v1.auth_login"),
        json={"username": user.username, "password": "mypwd"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json
    assert "refresh_token" in resp.json


def test_get_refresh_token(client, db):
    household = Household.create(name="house")
    user = User.create(
        username="testuser",
        email="noreply@housechef.io",
        password="none",
        household_id=household.id,
    )
    refresh_token = create_refresh_token(identity=user)

    resp = client.post(
        url_for("api_v1.auth_refresh"),
        headers={
            "Authorization": f"Bearer {refresh_token}",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json
