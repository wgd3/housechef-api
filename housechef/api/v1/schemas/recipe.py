from flask_restx import Model, fields as restxFields
from marshmallow import fields

from housechef.database.models import Recipe, RecipeDietType, DietType
from housechef.extensions import db, ma
from .diet_type import DietTypeSchema
from .dish_type import DishTypeSchema
from .cuisine import CuisineSchema
from .recipe_ingredient import RecipeIngredientSchema
from .restx_schema import RestXSchema


class RecipeSchema(ma.SQLAlchemyAutoSchema, RestXSchema):
    id = ma.Int(dump_only=True)
    time_created = ma.auto_field(dump_only=True)
    time_updated = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    recipe_url = ma.auto_field()
    thumbnail_url = ma.auto_field()
    image_url = ma.auto_field()
    author = ma.auto_field()
    rating = ma.auto_field()
    servings = ma.auto_field()
    prep_time = ma.auto_field()
    cook_time = ma.auto_field()
    source_name = ma.auto_field()

    diets = fields.Function(lambda recipe: [dt.name for dt in recipe.diets])
    dish_types = fields.Function(lambda recipe: [dt.name for dt in recipe.dish_types])
    cuisines = fields.Function(lambda recipe: [c.name for c in recipe.cuisines])

    ingredients = fields.List(
        fields.Nested(
            RecipeIngredientSchema,
            only=(
                "amount",
                "unit",
                "us_unit_short",
                "us_unit_long",
                "us_amount",
                "metric_unit_short",
                "metric_unit_long",
                "metric_amount",
                "original_string",
            ),
        )
    )

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api_v1.get_recipe", values=dict(recipe_id="<id>")),
            # "collection": ma.URLFor("api_v1.list_recipes"),
        }
    )

    @staticmethod
    def get_restx_model() -> Model:
        return Model(
            "recipe_model",
            {
                "id": restxFields.Integer(readonly=True),
                "time_created": restxFields.DateTime(readonly=True),
                "time_updated": restxFields.DateTime(readonly=True),
                "name": restxFields.String(),
                "macros": restxFields.Raw(readonly=True),
                "directions": restxFields.List(restxFields.String),
                "image_url": restxFields.String(),
                "recipe_url": restxFields.String(),
                "thumbnail_url": restxFields.String(),
                "author": restxFields.String(),
                "servings": restxFields.Integer(),
                "rating": restxFields.Integer(),
                "prep_time": restxFields.Integer(),
                "cook_time": restxFields.Integer(),
                "source_name": restxFields.String(),
                "diets": restxFields.List(restxFields.String),
                "dish_types": restxFields.List(restxFields.String),
                "tags": restxFields.List(restxFields.String),
                "cuisines": restxFields.List(restxFields.String),
                "ingredients": restxFields.List(restxFields.Raw),
            },
        )

    class Meta:
        model = Recipe
        sqla_session = db.session
        load_instance = True
        ordered = True
        fields = (
            "id",
            "time_created",
            "time_updated",
            "name",
            "macros",
            "directions",
            "image_url",
            "recipe_url",
            "thumbnail_url",
            "author",
            "servings",
            "rating",
            "prep_time",
            "cook_time",
            "source_name",
            "diets",
            "dish_types",
            "tags",
            "cuisines",
            "ingredients",
        )
