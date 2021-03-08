import json
import os
import sys
from typing import List

from housechef.database.models import (
    Cuisine,
    DietType,
    DishType,
    Ingredient,
    Recipe,
    RecipeCuisine,
    RecipeDietType,
    RecipeDishType,
    RecipeIngredient,
    RecipeTag,
    Tag,
)
from housechef.extensions import db

model_data = {}


def load_json_data(data_dir: str):
    if not os.path.isdir(data_dir):
        print(f"{data_dir} is not a valid directory!")
        sys.exit(1)

    for model in [
        Cuisine,
        DietType,
        DishType,
        Ingredient,
        RecipeCuisine,
        RecipeDietType,
        RecipeDishType,
        RecipeIngredient,
        RecipeTag,
        Recipe,
        Tag,
    ]:
        infile = os.path.join(data_dir, f"{model.__tablename__}.json")
        if not os.path.isfile(infile):
            print(f"Unable to find JSON data for {model.__tablename__}, skipping...")
            continue

        print(f"Loading {model.__tablename__}...")
        with open(infile, "r") as json_file:
            json_data = json.load(json_file)
            model_data[model.__tablename__] = json_data

    load_cuisines(model_data["cuisines"])
    load_dish_types(model_data["dish_types"])
    load_diet_types(model_data["diet_types"])
    load_ingredients(model_data["ingredients"])
    load_tags(model_data["tags"])
    create_recipes(model_data["recipes"])
    print(f"Finished re-hydrating database!")


def load_cuisines(data: List[dict]):
    for item in data:
        copy = item.copy()
        del copy["id"]
        Cuisine.create(**copy)
    print(f"\nCreated {len(data)} cuisines")


def load_dish_types(data: List[dict]):
    for item in data:
        copy = item.copy()
        del copy["id"]
        DishType.create(**copy)
    print(f"\nCreated {len(data)} dish types")


def load_diet_types(data: List[dict]):
    for item in data:
        copy = item.copy()
        del copy["id"]
        DietType.create(**copy)
    print(f"\nCreated {len(data)} diet types")


def load_ingredients(data: List[dict]):
    for item in data:
        copy = item.copy()
        del copy["id"]
        Ingredient.create(**copy)
    print(f"\nCreated {len(data)} ingredients")


def load_tags(data: List[dict]):
    for item in data:
        copy = item.copy()
        del copy["id"]
        Tag.create(**copy)
    print(f"\nCreated {len(data)} tags")


def create_recipes(data: List[dict]):
    for old_recipe_data in data:
        copy = old_recipe_data.copy()
        del copy["id"]
        copy["household_id"] = None
        new_recipe_obj = Recipe.create(**copy)
        print(f"\n\n===\n\nCreated new new_recipe_obj: {new_recipe_obj.name}\n")

        # collect all dictionaries that have relationships with a new_recipe_obj
        recipe_cuisines: List[dict] = [
            x
            for x in model_data["recipe_cuisines"]
            if x["recipe_id"] == old_recipe_data["id"]
        ]
        print(f"Found {len(recipe_cuisines)} old RecipeCuisine objects!")

        recipe_ingredients: List[dict] = [
            x
            for x in model_data["recipe_ingredients"]
            if x["recipe_id"] == old_recipe_data["id"]
        ]
        print(f"Found {len(recipe_ingredients)} old RecipeIngredient objects!")

        recipe_diet_types: List[dict] = [
            x
            for x in model_data["recipe_diet_types"]
            if x["recipe_id"] == old_recipe_data["id"]
        ]
        print(f"Found {len(recipe_diet_types)} old RecipeDietType objects!")

        recipe_dish_types: List[dict] = [
            x
            for x in model_data["recipe_dish_types"]
            if x["recipe_id"] == old_recipe_data["id"]
        ]
        print(f"Found {len(recipe_dish_types)} old RecipeDishType objects!")

        print(f"\nEvaluating RecipeCuisines...")
        for r_c in recipe_cuisines:
            old_cuisine = next(
                c for c in model_data["cuisines"] if c["id"] == r_c["cuisine_id"]
            )
            print(f"Searching for new cuisine matching name '{old_cuisine['name']}'")
            # find the recently-hydrated Cuisine object, and update the ForeignKeys with the new IDs
            new_cuisine_obj: Cuisine = Cuisine.query.filter(
                Cuisine.name == old_cuisine["name"]
            ).one_or_none()
            print(
                f"Found new cuisine obj: {new_cuisine_obj.name} ({new_cuisine_obj.id})"
            )
            rc = RecipeCuisine(
                cuisine_id=new_cuisine_obj.id, recipe_id=new_recipe_obj.id
            )
            db.session.add(rc)
            print(
                f"Associated cuisine {new_cuisine_obj.name} with new_recipe_obj {new_recipe_obj.name}"
            )
        db.session.commit()
        print(f"\n")

        for r_dt in recipe_dish_types:
            old_dt = next(
                dt
                for dt in model_data["dish_types"]
                if dt["id"] == r_dt["dish_type_id"]
            )
            new_dt_obj = DishType.query.filter(
                DishType.name == old_dt["name"]
            ).one_or_none()
            rc = RecipeDishType(dish_type_id=new_dt_obj.id, recipe_id=new_recipe_obj.id)
            db.session.add(rc)
        db.session.commit()

        for r_dt in recipe_diet_types:
            old_dt = next(
                dt
                for dt in model_data["diet_types"]
                if dt["id"] == r_dt["diet_type_id"]
            )
            new_dt_obj = DietType.query.filter(
                DietType.name == old_dt["name"]
            ).one_or_none()
            rc = RecipeDietType(new_dt_obj, new_recipe_obj)
            db.session.add(rc)
        db.session.commit()

        print(f"Evaluating ingredients..")
        for r_i in recipe_ingredients:
            # lookup the name in the new database of ingredients, find the matching named-dict
            # in the stored model_data.
            # old_ingredient has id/name/spoonacular_id
            # RecipeIngredient uses the old_ingredient id
            old_ingredient = next(
                i for i in model_data["ingredients"] if i["id"] == r_i["ingredient_id"]
            )
            print(
                f"Found old ingredient #{old_ingredient['id']} - {old_ingredient['name']}"
            )
            new_ingredient_obj = Ingredient.query.filter(
                Ingredient.spoonacular_id == old_ingredient["spoonacular_id"]
            ).one_or_none()
            print(f"Found matching new ingredient!")

            # remove the IDs before sending all other data over
            r_i_copy = r_i.copy()
            del r_i_copy["recipe_id"]
            del r_i_copy["ingredient_id"]
            ri = RecipeIngredient(
                recipe_id=new_recipe_obj.id,
                ingredient_id=new_ingredient_obj.id,
                **r_i_copy,
            )
            db.session.add(ri)
            print(
                f"Associated ingredient {new_ingredient_obj.name} with new_recipe_obj {new_recipe_obj.name}!"
            )
        db.session.commit()
