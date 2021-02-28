from housechef.extensions import db


class RecipeDishType(db.Model):
    __tablename__ = "recipe_dish_types"
    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id", "dish_type_id", name="_recipe_dish_type_constraint"
        ),
    )

    """Primary Keys"""
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    dish_type_id = db.Column(
        db.Integer, db.ForeignKey("dish_types.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    recipe = db.relationship("Recipe", back_populates="dish_types")
    dish_type = db.relationship("DishType", back_populates="recipes")

    def __repr__(self):
        return f"<RecipeDishType - {self.recipe.name} / {self.dish_type.name}>"
