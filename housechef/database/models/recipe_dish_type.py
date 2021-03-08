from housechef.extensions import db


class RecipeDishType(db.Model):
    __tablename__ = "recipe_dish_types"
    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id", "dish_type_id", name="_recipe_dish_type_constraint"
        ),
    )

    """Primary Keys"""
    # Parent
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    # Child
    dish_type_id = db.Column(
        db.Integer, db.ForeignKey("dish_types.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    # Parent
    recipe = db.relationship("Recipe", back_populates="recipe_dish_types")
    # Child
    dish_type = db.relationship("DishType", back_populates="recipes", lazy="joined")

    def __init__(self, dish_type=None, recipe=None):
        """Called when appending DishType objects to Recipe objects, child used as first arg"""
        self.dish_type = dish_type
        self.recipe = recipe

    def __repr__(self):
        return f"<RecipeDishType - {self.recipe.name} / {self.dish_type.name}>"
