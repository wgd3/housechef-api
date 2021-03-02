import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from housechef.database.models import Household, User, Recipe


@pytest.mark.usefixtures("db", "client")
class TestHouseholdApi:
    def setup(self):
        self.household = Household.create(name="TestHousehold")
        self.user = User.create(
            username="testuser",
            email="noreply@housechef.io",
            password="none",
            household_id=self.household.id,
        )
        self.access_token = create_access_token(identity=self.user)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

    def test_get_household(self, client):
        resp = client.get(
            url_for("api_v1.get_household", household_id=self.household.id),
            headers=self.headers,
        )
        assert resp.status_code == 200

    def test_get_household_without_token(self, client):
        resp = client.get(
            url_for("api_v1.get_household", household_id=self.household.id)
        )
        assert resp.status_code == 401

    def test_get_mismatched_household(self, client):
        resp = client.get(
            url_for("api_v1.get_household", household_id=100000), headers=self.headers
        )
        assert resp.status_code == 403


@pytest.mark.usefixtures("db", "client")
class TestHouseholdListApi:
    def setup(self):
        self.household = Household.create(name="TestHousehold")
        self.user = User.create(
            username="testuser",
            email="noreply@housechef.io",
            password="none",
            household_id=self.household.id,
        )
        self.access_token = create_access_token(
            identity=self.user, additional_claims={"roles": []}
        )
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

    def test_get_households(self, client):
        resp = client.get(
            url_for("api_v1.list_households"),
            headers=self.headers,
        )
        # 401 for missing the required role
        assert resp.status_code == 401

    def test_get_household_without_token(self, client):
        resp = client.get(url_for("api_v1.list_households"))
        # 401 for missing the required role
        assert resp.status_code == 401

    def test_get_households_as_admin(self, client, admin_headers):
        resp = client.get(
            url_for("api_v1.list_households"),
            headers=admin_headers,
        )
        assert resp.status_code == 200


@pytest.mark.usefixtures("db", "client")
class TestHouseholdMealApi:
    def setup(self):
        self.household = Household.create(name="TestHousehold")
        self.user = User.create(
            username="testuser",
            email="noreply@housechef.io",
            password="none",
            household_id=self.household.id,
        )
        self.access_token = create_access_token(
            identity=self.user, additional_claims={"roles": []}
        )
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

    def test_get_household_meals_as_user(self, client):
        resp = client.get(url_for("api_v1.household_meals"), headers=self.headers)
        assert resp.status_code == 200

    def test_get_household_meals_without_token(self, client):
        resp = client.get(url_for("api_v1.household_meals"))
        assert resp.status_code == 401

    def test_get_household_meals_specific_date(self, client):
        resp = client.get(
            url_for("api_v1.household_meals", date="2021-01-01"), headers=self.headers
        )
        assert resp.status_code == 200
        assert resp.json["data"] == []

    def test_get_household_meals_malformed_date(self, client):
        resp = client.get(
            url_for("api_v1.household_meals", date="2021/01/01"), headers=self.headers
        )
        assert resp.status_code == 400

    def test_add_meal_to_household_without_recipes(self, client):
        meal_data = {"date": "2021-01-01", "household_id": self.household.id}
        resp = client.post(
            url_for("api_v1.household_meals"),
            json=meal_data,
            headers={**self.headers, "Content-Type": "application/json"},
        )
        assert resp == 201

    def test_add_meal_to_household_with_recipes(self, client):

        recipe = Recipe.create(name="test", household_id=self.household.id)
        meal_data = {
            "date": "2021-01-01",
            "household_id": self.household.id,
            "recipes": [recipe.id],
        }
        resp = client.post(
            url_for("api_v1.household_meals"),
            json=meal_data,
            headers={**self.headers, "Content-Type": "application/json"},
        )
        assert resp.status_code == 201
        assert len(resp.json["data"]["recipes"]) == 1

    def test_add_meal_to_household_with_bad_date(self, client):
        meal_data = {"date": "20210-001-01", "household_id": self.household.id}
        resp = client.post(
            url_for("api_v1.household_meals"),
            json=meal_data,
            headers={**self.headers, "Content-Type": "application/json"},
        )
        assert resp == 400

    def test_add_meal_to_household_with_bad_household_id(self, client):
        meal_data = {"date": "2021-02-02", "household_id": 100000}
        resp = client.post(
            url_for("api_v1.household_meals"),
            json=meal_data,
            headers={**self.headers, "Content-Type": "application/json"},
        )
        assert resp == 400
