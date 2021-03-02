import factory
import datetime
from faker import Faker
from housechef.database.models import User, Recipe, Household, Cuisine, Ingredient, Meal

fake = Faker()


class CuisineFactory(factory.Factory):

    name = factory.Sequence(lambda c: f"cuisine{c}")

    class Meta:
        model = Cuisine


class IngredientFactory(factory.Factory):

    name = factory.Sequence(lambda n: f"ingredient{n}")

    class Meta:
        model = Ingredient


class HouseholdFactory(factory.Factory):

    # name = fake.street_name()
    name = factory.Sequence(lambda n: f"Street{n}")

    class Meta:
        model = Household


class MealFactory(factory.Factory):
    date = datetime.date.today()

    household = factory.SubFactory(HouseholdFactory)

    class Meta:
        model = Meal


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"
    household = factory.SubFactory(HouseholdFactory)

    class Meta:
        model = User


class RecipeFactory(factory.Factory):

    name = factory.Sequence(lambda n: f"recipe{n}")
    recipe_url = factory.Sequence(lambda x: f"{fake.url()}recipe{x}.html")
    image_url = fake.image_url()
    thumbnail_url = fake.image_url()
    author = fake.name()
    servings = fake.pyint(min_value=1, max_value=5)
    prep_time = fake.pyint(min_value=10, max_value=60)
    cook_time = fake.pyint(min_value=10, max_value=360)

    _directions = "step 1\nstep 2\nstep 3"

    household = factory.SubFactory(HouseholdFactory)

    class Meta:
        model = Recipe
