import pytest
from flask import url_for

from housechef.extensions import pwd_context
from housechef.database.models import User, Household


@pytest.mark.usefixtures("db", "client")
class TestUserGET:
    def test_get_user(self, app, client, db, test_user, test_user_headers):

        # test get_user
        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        rep = client.get(user_url, headers=test_user_headers)
        assert rep.status_code == 200

        data = rep.get_json()["data"]
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["active"] == test_user.active

    def test_get_user_as_non_admin_user(
        self, app, client, db, test_user, test_user_headers, user_factory
    ):

        # create fake, non-test user
        user = user_factory.create()
        db.session.add(user)
        db.session.commit()

        # test get_user
        user_url = url_for("api_v1.get_user", user_id=user.id)
        rep = client.get(user_url, headers=test_user_headers)
        assert rep.status_code == 403

    def test_get_user_as_admin(self, app, client, db, test_user, admin_headers):

        # test get_user
        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        rep = client.get(user_url, headers=admin_headers)
        assert rep.status_code == 200

        data = rep.get_json()["data"]
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["active"] == test_user.active

    def test_get_missing_user_as_user(self, client, test_user_headers):
        """If a non-admin user requests another user, they'll receive a 403"""
        # test get_user
        user_url = url_for("api_v1.get_user", user_id=10000)
        rep = client.get(user_url, headers=test_user_headers)
        assert rep.status_code == 403

    def test_get_missing_user_as_admin(self, client, admin_headers):
        """If an admin user requests another user, they'll receive a 404"""
        # test get_user
        user_url = url_for("api_v1.get_user", user_id=10000)
        rep = client.get(user_url, headers=admin_headers)
        assert rep.status_code == 404


@pytest.mark.usefixtures("db", "client")
class TestUserPUT:
    def test_put_user(self, client, db, test_user, test_user_headers):

        data = {"username": "updated", "password": "new_password"}

        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        # test update user
        rep = client.put(user_url, json=data, headers=test_user_headers)
        assert rep.status_code == 200

        data = rep.get_json()["data"]
        assert data["username"] == "updated"
        assert data["email"] == test_user.email
        assert data["active"] == test_user.active

        db.session.refresh(test_user)
        assert pwd_context.verify("new_password", test_user.password)

    def test_put_wrong_user_as_user(self, client, db, user_factory, test_user_headers):

        user = user_factory.create()
        db.session.add(user)
        db.session.commit()

        data = {"username": "updated", "password": "new_password"}

        user_url = url_for("api_v1.get_user", user_id=user.id)
        # test update user
        rep = client.put(user_url, json=data, headers=test_user_headers)
        assert rep.status_code == 403

    def test_put_wrong_user_as_admin(self, client, db, user_factory, admin_headers):

        user = user_factory.create()
        db.session.add(user)
        db.session.commit()

        data = {"username": "updated", "password": "new_password"}

        user_url = url_for("api_v1.get_user", user_id=user.id)
        # test update user
        rep = client.put(user_url, json=data, headers=admin_headers)
        assert rep.status_code == 200

        data = rep.get_json()["data"]
        assert data["username"] == "updated"
        assert data["email"] == user.email
        assert data["active"] == user.active

    def test_put_user_invalid_payload(self, client, db, test_user, test_user_headers):

        data = {"username": "updated", "password": "new_password", "time_created": None}

        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        # test update user
        rep = client.put(user_url, json=data, headers=test_user_headers)
        assert rep.status_code == 400


@pytest.mark.usefixtures("db", "client")
class TestUserDELETE:
    def test_delete_user(self, client, db, test_user, test_user_headers):
        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        rep = client.delete(user_url, headers=test_user_headers)
        assert rep.status_code == 200
        assert db.session.query(User).filter_by(id=test_user.id).first() is None

    def test_delete_user_as_different_user(
        self, client, db, user_factory, test_user, test_user_headers
    ):
        other_user = user_factory.create()
        db.session.add(other_user)
        db.session.commit()

        user_url = url_for("api_v1.get_user", user_id=other_user.id)
        rep = client.delete(user_url, headers=test_user_headers)
        assert rep.status_code == 403

    def test_delete_user_as_admin(self, client, db, test_user, admin_headers):
        user_url = url_for("api_v1.get_user", user_id=test_user.id)
        rep = client.delete(user_url, headers=admin_headers)
        assert rep.status_code == 200
        assert db.session.query(User).filter_by(id=test_user.id).first() is None

    def test_delete_missing_user_as_user(
        self, client, db, test_user, test_user_headers
    ):

        user_url = url_for("api_v1.get_user", user_id=1000)
        rep = client.delete(user_url, headers=test_user_headers)
        assert rep.status_code == 403

    def test_delete_missing_user_as_admin(self, client, db, test_user, admin_headers):

        user_url = url_for("api_v1.get_user", user_id=1000)
        rep = client.delete(user_url, headers=admin_headers)
        assert rep.status_code == 404


@pytest.mark.usefixtures("db", "client")
class TestUserListPOST:
    def test_create_user(self, client, db, test_user):
        users_url = url_for("api_v1.list_users")
        user_data = {
            "username": "created",
            "password": "admin",
            "email": "create@mail.com",
            "household_id": test_user.household_id,
        }

        rep = client.post(
            users_url, json=user_data, headers={"Content-Type": "application/json"}
        )
        assert rep.status_code == 201

        data = rep.get_json()["data"]
        user = User.get_by_id(data["id"])

        assert user.username == "created"
        assert user.email == "create@mail.com"

    def test_create_user_with_bad_payload(self, client, db, test_user):
        users_url = url_for("api_v1.list_users")
        user_data = {
            "time_created": None,
            "username": "created",
            "password": "admin",
            "email": "create@mail.com",
            "household_id": test_user.household_id,
        }

        rep = client.post(
            users_url, json=user_data, headers={"Content-Type": "application/json"}
        )
        assert rep.status_code == 400

        # data = rep.get_json()["data"]
        # user = User.get_by_id(data["id"])
        #
        # assert user.username == "created"
        # assert user.email == "create@mail.com"


@pytest.mark.usefixtures("db", "client")
class TestUserListGET:
    def test_get_all_users(self, client, db, user_factory, admin_headers):
        users_url = url_for("api_v1.list_users")
        users = user_factory.create_batch(10)

        db.session.add_all(users)
        db.session.commit()

        rep = client.get(users_url, headers=admin_headers)
        assert rep.status_code == 200

        results = rep.get_json()["data"]
        for user in users:
            assert any(u["id"] == user.id for u in results)

    def test_get_all_users_without_admin_role(
        self, client, db, user_factory, test_user_headers
    ):
        users_url = url_for("api_v1.list_users")
        users = user_factory.create_batch(10)

        db.session.add_all(users)
        db.session.commit()

        rep = client.get(users_url, headers=test_user_headers)
        assert rep.status_code == 401


@pytest.mark.usefixtures("db", "client")
class TestUserAuthLogin:
    def setup(self):
        self.login_url = url_for("api_v1.auth_login")
        self.user = User.create(
            username="test",
            email="test@test.com",
            password="test",
            household_id=1,
        )

    def test_successful_login(self, client, db):

        resp = client.post(
            self.login_url, json={"username": "test", "password": "test"}
        )

        assert resp.status_code == 200
        assert "access_token" in resp.json
        assert "refresh_token" in resp.json

    def test_missing_username(self, client, db):

        resp = client.post(self.login_url, json={"password": "test"})

        assert resp.status_code == 400

    def test_missing_password(self, client, db):

        resp = client.post(self.login_url, json={"username": "test"})

        assert resp.status_code == 400

    def test_incorrect_password(self, client, db):

        resp = client.post(self.login_url, json={"username": "test", "password": "tt"})

        assert resp.status_code == 401
