import datetime
import json
import os
import sys

from sqlalchemy import inspect

from housechef.database.models import (
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
)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def dump_tables(dump_dir: str):

    if not os.path.isdir(dump_dir):
        print(f"{dump_dir} is not a valid directory!")
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
        print(f"Dumping {model.__tablename__}...")
        outfile_name = f"{model.__tablename__}.json"
        data = []
        for row in model.query.all():
            obj = object_as_dict(row)
            data.append(obj)
        with open(os.path.join(dump_dir, outfile_name), "w") as outfile:
            json.dump(data, outfile, default=default, sort_keys=True)
        print(f"Dumped {len(data)} {model.__tablename__} records!\n")
