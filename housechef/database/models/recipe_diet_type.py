from housechef.extensions import db


class RecipeDietType(db.Model):
    __tablename__ = "recipe_diet_types"
    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id", "diet_type_id", name="_recipe_diet_type_constraint"
        ),
    )

    """Primary Keys"""
    # Parent
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    # Child
    diet_type_id = db.Column(
        db.Integer, db.ForeignKey("diet_types.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    # Parent
    recipe = db.relationship("Recipe", back_populates="recipe_diet_types")
    # Child
    diet_type = db.relationship("DietType", back_populates="recipes", lazy="joined")

    def __init__(self, diet_type=None, recipe=None):
        """Called when appending DietType objects to Recipe objects, child used as first arg"""
        self.diet_type = diet_type
        self.recipe = recipe

    def __repr__(self):
        return f"<RecipeDietType - {self.recipe.name} / {self.diet_type.name}>"
