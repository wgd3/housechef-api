from housechef.extensions import db


class RecipeIngredient(db.Model):
    """Association object for recipe ingredients"""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id", "ingredient_id", name="_recipe_ingredient_constraint"
        ),
    )

    """Primary Keys"""
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), primary_key=True, nullable=False
    )

    """Original Strings
    
    In the Spoonacular response, it grabs the original ingredient string from the recipe, which
    can contain special formatting. For display purposes, this is stored in this table
    """
    original_string = db.Column(db.String)

    """Quantities"""
    amount = db.Column(db.Float)
    unit = db.Column(db.String)
    us_amount = db.Column(db.Float)
    us_unit_short = db.Column(db.String)
    us_unit_long = db.Column(db.String)
    metric_amount = db.Column(db.Float)
    metric_unit_short = db.Column(db.String)
    metric_unit_long = db.Column(db.String)

    """Nutrition"""
    caffeine = db.Column(db.Float)
    calcium = db.Column(db.Float)
    calories = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    choline = db.Column(db.Float)
    copper = db.Column(db.Float)
    fat = db.Column(db.Float)
    fiber = db.Column(db.Float)
    folate = db.Column(db.Float)
    folic_acid = db.Column(db.Float)
    iron = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    manganese = db.Column(db.Float)
    mono_unsaturated_fat = db.Column(db.Float)
    net_carbohydrates = db.Column(db.Float)
    phosphorous = db.Column(db.Float)
    poly_unsaturated_fat = db.Column(db.Float)
    potassium = db.Column(db.Float)
    protein = db.Column(db.Float)
    saturated_fat = db.Column(db.Float)
    selenium = db.Column(db.Float)
    sodium = db.Column(db.Float)
    sugar = db.Column(db.Float)
    vitamin_a = db.Column(db.Float)
    vitamin_b1 = db.Column(db.Float)
    vitamin_b12 = db.Column(db.Float)
    vitamin_b2 = db.Column(db.Float)
    vitamin_b3 = db.Column(db.Float)
    vitamin_b5 = db.Column(db.Float)
    vitamin_b6 = db.Column(db.Float)
    vitamin_c = db.Column(db.Float)
    vitamin_d = db.Column(db.Float)
    vitamin_e = db.Column(db.Float)
    vitamin_k = db.Column(db.Float)
    zinc = db.Column(db.Float)

    """Glycemic Information"""
    glycemic_index = db.Column(db.Float)
    glycemic_load = db.Column(db.Float)

    """Cost Information"""
    estimated_cost_cents = db.Column(db.Float)

    """Relationships"""
    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipes")

    def __repr__(self):
        return f"<RecipeIngredient {self.ingredient.name} in {self.recipe.name}>"
