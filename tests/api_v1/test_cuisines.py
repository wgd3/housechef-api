import pytest
from flask import url_for
from flask_jwt_extended import create_access_token

from housechef.database.models import Cuisine


@pytest.mark.usefixtures("db", "client")
class TestCuisineApi:
    cuisines = []

    def setup(self):
        for i in range(5):
            self.cuisines.append(Cuisine.create(name=f"cuisine{i}"))

    def test_get_cuisine_by_id(self, client):
        resp = client.get(url_for("api_v1.get_cuisine", cuisine_id=1))
        assert resp.status_code == 200

    def test_get_cuisine_404(self, client):
        resp = client.get(url_for("api_v1.get_cuisine", cuisine_id=10000))
        assert resp.status_code == 404

    def test_modify_cuisine(self, client, admin_headers):
        resp = client.put(
            url_for("api_v1.get_cuisine", cuisine_id=1),
            headers=admin_headers,
            json=dict(name="testing"),
        )
        assert resp.status_code == 200
        assert resp.json["data"]["name"] == "testing"

    def test_modify_cuisine_without_headers(self, client):
        resp = client.put(
            url_for("api_v1.get_cuisine", cuisine_id=1), json=dict(name="testing")
        )
        assert resp.status_code == 401

    def test_modify_cuisine_readonly_fields(self, client, admin_headers):
        resp = client.put(
            url_for("api_v1.get_cuisine", cuisine_id=1),
            headers=admin_headers,
            json=dict(name="testing", time_created=None),
        )
        assert resp.status_code == 400

    def test_delete_cuisine(self, client, admin_headers):
        resp = client.delete(
            url_for("api_v1.get_cuisine", cuisine_id=1),
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_delete_cuisine_without_headers(self, client):
        resp = client.delete(
            url_for("api_v1.get_cuisine", cuisine_id=1),
        )
        assert resp.status_code == 401

    def test_delete_cuisine_with_missing_role(self, client, test_user_headers):
        resp = client.delete(
            url_for("api_v1.get_cuisine", cuisine_id=1), headers=test_user_headers
        )
        assert resp.status_code == 401


@pytest.mark.usefixtures("db", "client")
class TestCuisineListApi:
    cuisines = []

    def setup(self):
        for i in range(5):
            self.cuisines.append(Cuisine.create(name=f"cuisine{i}"))

    def test_get_all_cuisines(self, client):
        resp = client.get(url_for("api_v1.list_cuisines"))
        assert resp.status_code == 200
        assert len(resp.json["data"]) == len(self.cuisines)

    def test_add_cuisine(self, client, test_user_headers):
        cuisine_data = {"name": "test"}
        resp = client.post(
            url_for("api_v1.list_cuisines"),
            json=cuisine_data,
            headers=test_user_headers,
        )
        assert resp.status_code == 201

    def test_add_cuisine_without_token(self, client):
        cuisine_data = {"name": "test"}
        resp = client.post(
            url_for("api_v1.list_cuisines"),
            json=cuisine_data,
        )
        assert resp.status_code == 401

    def test_add_cuisine_with_bad_name(self, client, test_user_headers):
        cuisine_data = {"name": None}
        resp = client.post(
            url_for("api_v1.list_cuisines"),
            json=cuisine_data,
            headers=test_user_headers,
        )
        assert resp.status_code == 400

    def test_add_cuisine_with_readonly_properties(self, client, test_user_headers):
        cuisine_data = {"name": "test", "id": 5}
        resp = client.post(
            url_for("api_v1.list_cuisines"),
            json=cuisine_data,
            headers=test_user_headers,
        )
        assert resp.status_code == 400
