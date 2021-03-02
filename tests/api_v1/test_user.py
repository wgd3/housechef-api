from flask import url_for
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from housechef.extensions import pwd_context
from housechef.database.models import User, Household


def test_get_user(app, client, db, test_user, test_user_headers):

    # test get_user
    user_url = url_for("api_v1.get_user", user_id=test_user.id)
    rep = client.get(user_url, headers=test_user_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["active"] == test_user.active


def test_put_user(client, db, test_user, test_user_headers):

    data = {"username": "updated", "password": "new_password"}

    user_url = url_for("api_v1.get_user", user_id=test_user.id)
    # test update user
    rep = client.put(user_url, json=data, headers=test_user_headers)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == "updated"
    assert data["email"] == test_user.email
    assert data["active"] == test_user.active

    db.session.refresh(test_user)
    assert pwd_context.verify("new_password", test_user.password)


def test_delete_user(client, db, test_user, test_user_headers):
    user_url = url_for("api_v1.get_user", user_id=test_user.id)
    rep = client.delete(user_url, headers=test_user_headers)
    assert rep.status_code == 200
    assert db.session.query(User).filter_by(id=test_user.id).first() is None


def test_create_user(client, db, test_user, test_user_headers):
    # test bad data
    users_url = url_for("api_v1.list_users")
    # rep = client.post(users_url, json=data)
    # assert rep.status_code == 400
    household = Household.create(name="new_user_household")
    user_data = {
        "username": "created",
        "password": "admin",
        "email": "create@mail.com",
        "household_id": household.id,
    }

    rep = client.post(
        users_url, json=user_data, headers={"Content-Type": "application/json"}
    )
    assert rep.status_code == 201

    data = rep.get_json()
    user = User.get_by_id(data["user"]["id"])

    assert user.username == "created"
    assert user.email == "create@mail.com"


#
#
# def test_get_all_user(client, db, user_factory, admin_headers):
#     users_url = url_for("api_v1.list_users")
#     users = user_factory.create_batch(30)
#
#     db.session.add_all(users)
#     db.session.commit()
#
#     rep = client.get(users_url, headers=admin_headers)
#     assert rep.status_code == 200
#
#     results = rep.get_json()
#     for user in users:
#         assert any(u["id"] == user.id for u in results["results"])
