import json
import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, create_refresh_token

from housechef.database.models import Household, Role, User, UserRole
from housechef.app import create_app
from housechef.extensions import db as _db
from pytest_factoryboy import register
from tests.factories import (
    UserFactory,
    RecipeFactory,
    HouseholdFactory,
    CuisineFactory,
    IngredientFactory,
    MealFactory,
)


register(UserFactory)
register(RecipeFactory)
register(HouseholdFactory)
register(CuisineFactory)
register(IngredientFactory)
register(MealFactory)


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    return app


@pytest.fixture
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()
        Role.create(name="User", default=True)
        Role.create(name="Admin", default=False)

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def test_user(db):
    household = Household.create(name="test")
    user = User.create(
        username="testuser",
        email="noreply@housechef.io",
        password="none",
        household_id=household.id,
    )
    # user_role = Role.create(name="User")
    # user.roles.append(user_role)
    # user.save()
    return user


@pytest.fixture
def test_user_headers(test_user):
    access_token = create_access_token(
        identity=test_user,
        additional_claims={"roles": [r.name for r in test_user.roles]},
    )
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def admin_user(db):
    household = Household.create(name="AdminHouse")
    user = User.create(
        username="admin",
        email="admin@admin.com",
        password="admin",
        household_id=household.id,
    )
    # admin_role = Role.create(name="Admin")
    # user_admin_role = UserRole(user_id=user.id, role_id=admin_role.id)
    # user.roles.append(admin_role)
    # user.save()

    return user


@pytest.fixture
def admin_headers(admin_user):
    access_token = create_access_token(
        identity=admin_user,
        additional_claims={"roles": ["Admin"]},
    )
    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def admin_refresh_headers(admin_user):
    refresh_token = create_refresh_token(identity=admin_user)
    return {
        "Authorization": f"Bearer {refresh_token}",
    }
