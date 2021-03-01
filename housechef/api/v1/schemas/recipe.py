from marshmallow import fields, pre_dump, post_dump

from housechef.database.models import Recipe
from housechef.extensions import ma, db
from .recipe_ingredient import RecipeIngredientSchema


class RecipeSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    directions = fields.Raw()
    _directions = fields.Raw(load_only=True)

    macros = fields.Dict(data_key="macros")

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

    class Meta:
        model = Recipe
        sqla_session = db.session
        load_instance = True
        ordered = True
