from flask_restx import fields, Model

meal_model = Model(
    "Meal Model",
    {
        "date": fields.Date(required=True, help="Date on which the meal takes place"),
        "recipes": fields.List(fields.Integer, required=False, default=[]),
        "household_id": fields.Integer(
            required=True, help="House to assign the meal to"
        ),
        "id": fields.Integer(readonly=True),
        "time_created": fields.DateTime(readonly=True),
        "time_updated": fields.DateTime(readonly=True),
    },
)
