import pytest
from flask import url_for
from flask_jwt_extended import create_access_token

from housechef.database.models import DietType


@pytest.mark.usefixtures("db", "client")
class TestDietTypesApi:
    def setup(self):
        for i in range(5):
            DietType.create(name=f"DietType{i}")

    def test_get_diet_type(self, client):
        resp = client.get(url_for("api_v1.get_diet_type", diet_type_id=1))
        assert resp.status_code == 200

    def test_get_missing_diet_type(self, client):
        resp = client.get(url_for("api_v1.get_diet_type", diet_type_id=10000))
        assert resp.status_code == 404

    def test_update_diet_type(self, client, admin_headers):
        resp = client.put(
            url_for("api_v1.get_diet_type", diet_type_id=1),
            headers=admin_headers,
            json=dict(name="testing"),
        )
        assert resp.status_code == 200
        assert resp.json["data"]["name"] == "testing"

    def test_bad_update_diet_type(self, client, admin_headers):
        resp = client.put(
            url_for("api_v1.get_diet_type", diet_type_id=1),
            headers=admin_headers,
            json=dict(name="testing", time_created=None),
        )
        assert resp.status_code == 400

    def test_unauthorized_update_diet_type(self, client):
        resp = client.put(
            url_for("api_v1.get_diet_type", diet_type_id=1),
            json=dict(name="testing"),
        )
        assert resp.status_code == 401

    def test_update_missing_diet_type(self, client, admin_headers):
        resp = client.put(
            url_for("api_v1.get_diet_type", diet_type_id=10000),
            headers=admin_headers,
            json=dict(name="testing"),
        )
        assert resp.status_code == 404

    def test_delete_diet_type(self, client, admin_headers):
        resp = client.delete(
            url_for("api_v1.get_diet_type", diet_type_id=1),
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_delete_missing_diet_type(self, client, admin_headers):
        resp = client.delete(
            url_for("api_v1.get_diet_type", diet_type_id=10000),
            headers=admin_headers,
        )
        assert resp.status_code == 404

    def test_unauthorized_diet_type(self, client):
        resp = client.delete(
            url_for("api_v1.get_diet_type", diet_type_id=1),
        )
        assert resp.status_code == 401
