from unittest.mock import patch

from housechef.extensions import spoon
from housechef.tasks.ingredient_lookup import get_recipe_ingredient_nutrition


def test_ingredient_collection(
    celery_session_app, celery_session_worker, celery_includes, recipe, db, app
):
    assert len(recipe.ingredients) == 10
    recipe_ingredients = []
    ingredient_resp = []
    for x in range(11):
        recipe_ingredients.append(
            dict(
                ingredient_id=x,
                ingredient_string=f"ingredient{x}",
                spoonacular_id=x,
            )
        )
        ingredient_resp.append(
            dict(
                original=f"ingredient{x}",
                id=x,
                nutrition={
                    "nutrients": [
                        {"amount": 10, "name": "Calories"},
                        {"amount": 10, "name": "Fat"},
                        {"amount": 10, "name": "Protein"},
                        {"amount": 10, "name": "Carbohydrates"},
                    ]
                },
            )
        )
    with app.app_context():
        with patch("housechef.extensions.spoon.parse_ingredients") as mocked_fn:
            mocked_fn.return_value.json.return_value = ingredient_resp
            task = get_recipe_ingredient_nutrition.delay(recipe_ingredients, recipe.id)
            task.get()
            spoon.parse_ingredients.assert_called()

        # recipe now has 10 ingredients, each with a value of 10
        # for all nutrients.
        db.session.refresh(recipe)
        assert recipe.calories == 100
        assert recipe.macros["calories"] == 100
        assert recipe.macros["fat"] == 100
        assert recipe.macros["protein"] == 100
        assert recipe.macros["carbohydrates"] == 100
