"""Click commands."""
import os

import click
from faker import Faker
from flask.cli import with_appcontext
from sqlalchemy.exc import IntegrityError

from housechef.database.models import Household, Note, Recipe, User
from housechef.extensions import db

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
@with_appcontext
def gen_test_data():
    fake = Faker()
    db.create_all()

    # generate common chefs to pull from
    chefs = _generate_chefs(5, fake)

    for i in range(3):
        household = Household.create(name=fake.street_name())
        click.echo(f'\nCreated household #{household.id} "{household.name}"')

        # create users for each house
        user_count = 2 if fake.boolean(chance_of_getting_true=80) is True else 1
        for u in range(user_count):
            user = User.create(
                username=fake.simple_profile().get("username"),
                email=fake.email(),
                password=fake.password(length=12),
                household_id=household.id,
            )
            click.echo(f'Created user "{user.username}"')

            # create a couple recipes for each user
            recipe_count = fake.pyint(max_value=10)
            for r in range(recipe_count):
                try:
                    recipe = Recipe.create(
                        name=_generate_recipe_name(fake),
                        recipe_url=f"{fake.url()}recipes/recipe.html",
                        image_url=fake.image_url(),
                        thumbnail_url=fake.image_url(),
                        author=fake.random_element(elements=chefs),
                        rating=fake.pyint(min_value=1, max_value=5),
                        servings=fake.pyint(min_value=1, max_value=10),
                        prep_time=fake.pyint(min_value=5, max_value=60),
                        cook_time=fake.pyint(min_value=5, max_value=360),
                        user_id=user.id,
                    )
                    # potentially add a note to the recipe
                    if fake.boolean():
                        note = Note.create(text=fake.text(), recipe_id=recipe.id)
                except IntegrityError as ie:
                    db.session.rollback()

        household.save()


@click.command()
@with_appcontext
def create_test_user():
    household = Household.create(name="Test Household")
    user = User.create(
        username="testuser",
        email="noreply@housechef.io",
        password="testuser",
        household_id=household.id,
    )
    click.echo(f"Created used 'testuser' with password 'testuser' successfully!")


def _generate_chefs(chef_count, fake):
    chefs = []
    for i in range(chef_count):
        chefs.append(fake.name())
    return chefs


def _generate_recipe_name(fake) -> str:
    verbs = ["Grilled", "Roasted", "Baked", "Fried", "Seared", "Stuffed", "Sauteed"]
    main_ingredients = [
        "Chicken Breast",
        "Chicken Thigh",
        "Sirloin",
        "Ribeye",
        "Strip Steak",
        "Tenderloin",
        "Pork Tenderloin",
        "Pork Chop",
        "Salmon",
        "Shrimp",
    ]
    sides = [
        "Beans",
        "Potatoes",
        "Rice",
        "Asparagus",
        "Broccoli",
        "Sweet Potato",
        "Cauliflower",
        "Risotto",
    ]
    locales = ["Mediterranean", "Italian", "Mexican", "Asian", "Spanish", "Indian"]
    return f'{fake.random_element(elements=verbs) if fake.boolean() else ""} {fake.random_element(elements=locales)} {fake.random_element(elements=main_ingredients)}{" with " + fake.random_element(elements=sides) if fake.boolean() else ""}'
