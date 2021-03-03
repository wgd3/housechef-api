from housechef.extensions import db


class RecipeIngredient(db.Model):
    """Association object for recipe ingredients"""

    __tablename__ = "recipe_ingredients"

    """
    This constraint was causing issues on recipe import for recipes that had (for example) "lime" and "lime seasoning".
    Both were assigned the same Spoonacular ID, which caused db issues while assigning recipe ingredients. Removing for
    now.
    """
    # __table_args__ = (
    #     db.UniqueConstraint(
    #         "recipe_id",
    #         "ingredient_id",
    #         "original_string",
    #         name="_recipe_ingredient_uix",
    #     ),
    # )

    """Primary Keys"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=False, nullable=False
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), primary_key=False, nullable=False
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
    caffeine = db.Column(db.Float, default=0.0)
    calcium = db.Column(db.Float, default=0.0)
    calories = db.Column(db.Float, default=0.0)
    carbohydrates = db.Column(db.Float, default=0.0)
    cholesterol = db.Column(db.Float, default=0.0)
    choline = db.Column(db.Float, default=0.0)
    copper = db.Column(db.Float, default=0.0)
    fat = db.Column(db.Float, default=0.0)
    fiber = db.Column(db.Float, default=0.0)
    folate = db.Column(db.Float, default=0.0)
    folic_acid = db.Column(db.Float, default=0.0)
    iron = db.Column(db.Float, default=0.0)
    magnesium = db.Column(db.Float, default=0.0)
    manganese = db.Column(db.Float, default=0.0)
    mono_unsaturated_fat = db.Column(db.Float, default=0.0)
    net_carbohydrates = db.Column(db.Float, default=0.0)
    phosphorous = db.Column(db.Float, default=0.0)
    poly_unsaturated_fat = db.Column(db.Float, default=0.0)
    potassium = db.Column(db.Float, default=0.0)
    protein = db.Column(db.Float, default=0.0)
    saturated_fat = db.Column(db.Float, default=0.0)
    selenium = db.Column(db.Float, default=0.0)
    sodium = db.Column(db.Float, default=0.0)
    sugar = db.Column(db.Float, default=0.0)
    vitamin_a = db.Column(db.Float, default=0.0)
    vitamin_b1 = db.Column(db.Float, default=0.0)
    vitamin_b12 = db.Column(db.Float, default=0.0)
    vitamin_b2 = db.Column(db.Float, default=0.0)
    vitamin_b3 = db.Column(db.Float, default=0.0)
    vitamin_b5 = db.Column(db.Float, default=0.0)
    vitamin_b6 = db.Column(db.Float, default=0.0)
    vitamin_c = db.Column(db.Float, default=0.0)
    vitamin_d = db.Column(db.Float, default=0.0)
    vitamin_e = db.Column(db.Float, default=0.0)
    vitamin_k = db.Column(db.Float, default=0.0)
    zinc = db.Column(db.Float, default=0.0)

    """Glycemic Information"""
    glycemic_index = db.Column(db.Float, default=0.0)
    glycemic_load = db.Column(db.Float, default=0.0)

    """Cost Information"""
    estimated_cost_cents = db.Column(db.Float, default=0.0)

    """Relationships"""
    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipes")

    def __repr__(self):
        return f"<RecipeIngredient {self.ingredient.name} in {self.recipe.name}>"

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
