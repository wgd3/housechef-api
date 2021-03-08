import pytest
from dotenv import load_dotenv

from housechef.app import init_celery, create_app
from housechef.database.models import Recipe, RecipeIngredient
from housechef.tasks.example import dummy_task


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    # with app.app_context():
    #     yield app
    return app


@pytest.fixture(scope="session")
def celery_session_app(celery_session_app, app):
    celery = init_celery(app)

    celery_session_app.conf = celery.conf
    celery_session_app.Task = celery_session_app.Task

    yield celery_session_app


#
#
# @pytest.fixture(scope="session")
# def celery_worker_pool():
#     return "solo"


# @pytest.fixture(scope="session")
# def celery_includes():
#     return ["housechef.tasks"]


# @pytest.fixture(scope="session")
# def celery_worker_parameters():
#     # type: () -> Mapping[str, Any]
#     """Redefine this fixture to change the init parameters of Celery workers.
#
#     This can be used e. g. to define queues the worker will consume tasks from.
#
#     The dict returned by your fixture will then be used
#     as parameters when instantiating :class:`~celery.worker.WorkController`.
#     """
#     return {
#         # For some reason this `celery.ping` is not registed IF our own worker is still
#         # running. To avoid failing tests in that case, we disable the ping check.
#         # see: https://github.com/celery/celery/issues/3642#issuecomment-369057682
#         # here is the ping task: `from celery.contrib.testing.tasks import ping`
#         "perform_ping_check": False,
#     }


@pytest.fixture
def recipe(db, recipe_factory, ingredient_factory):
    """Fixture to provide a fake recipe with test ingredients"""
    recipe = recipe_factory.create()
    db.session.add(recipe)
    db.session.commit()

    ingredients = ingredient_factory.create_batch(10)
    db.session.add_all(ingredients)
    db.session.commit()

    for i in ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=i.id,
        )
        db.session.add(recipe_ingredient)
        recipe.ingredients.append(recipe_ingredient)
    db.session.commit()

    return recipe
