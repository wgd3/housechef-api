"""initial

Revision ID: 1c1888098494
Revises:
Create Date: 2021-03-02 17:04:57.653698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c1888098494"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cuisines",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "dish_types",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "households",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "ingredients",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("spoonacular_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("spoonacular_id"),
    )
    role_table = op.create_table(
        "roles",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("default", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(
        role_table,
        [
            {"id": 0, "name": "User", "default": True},
            {"id": 1, "name": "Admin", "default": False},
        ],
    )
    op.create_table(
        "meals",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipes",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("recipe_url", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("thumbnail_url", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("prep_time", sa.Integer(), nullable=True),
        sa.Column("cook_time", sa.Integer(), nullable=True),
        sa.Column("source_name", sa.String(), nullable=True),
        sa.Column("_directions", sa.Text(), nullable=True),
        sa.Column("household_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "shopping_lists",
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("time_removed", sa.DateTime(), nullable=True),
        sa.Column("still_needed", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.id"],
        ),
        sa.PrimaryKeyConstraint("household_id", "ingredient_id"),
    )
    op.create_table(
        "users",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("height_inches", sa.Float(), nullable=True),
        sa.Column("weight_lbs", sa.Float(), nullable=True),
        sa.Column(
            "gender", sa.Enum("male", "female", name="gender_enum"), nullable=True
        ),
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "meal_recipes",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("meal_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["meal_id"],
            ["meals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "meal_id"),
    )
    op.create_table(
        "notes",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recipe_cuisines",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("cuisine_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cuisine_id"],
            ["cuisines.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "cuisine_id"),
        sa.UniqueConstraint(
            "recipe_id", "cuisine_id", name="_recipe_cuisine_constraint"
        ),
    )
    op.create_table(
        "recipe_dish_types",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("dish_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dish_type_id"],
            ["dish_types.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "dish_type_id"),
        sa.UniqueConstraint(
            "recipe_id", "dish_type_id", name="_recipe_dish_type_constraint"
        ),
    )
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("original_string", sa.String(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("us_amount", sa.Float(), nullable=True),
        sa.Column("us_unit_short", sa.String(), nullable=True),
        sa.Column("us_unit_long", sa.String(), nullable=True),
        sa.Column("metric_amount", sa.Float(), nullable=True),
        sa.Column("metric_unit_short", sa.String(), nullable=True),
        sa.Column("metric_unit_long", sa.String(), nullable=True),
        sa.Column("caffeine", sa.Float(), nullable=True),
        sa.Column("calcium", sa.Float(), nullable=True),
        sa.Column("calories", sa.Float(), nullable=True),
        sa.Column("carbohydrates", sa.Float(), nullable=True),
        sa.Column("cholesterol", sa.Float(), nullable=True),
        sa.Column("choline", sa.Float(), nullable=True),
        sa.Column("copper", sa.Float(), nullable=True),
        sa.Column("fat", sa.Float(), nullable=True),
        sa.Column("fiber", sa.Float(), nullable=True),
        sa.Column("folate", sa.Float(), nullable=True),
        sa.Column("folic_acid", sa.Float(), nullable=True),
        sa.Column("iron", sa.Float(), nullable=True),
        sa.Column("magnesium", sa.Float(), nullable=True),
        sa.Column("manganese", sa.Float(), nullable=True),
        sa.Column("mono_unsaturated_fat", sa.Float(), nullable=True),
        sa.Column("net_carbohydrates", sa.Float(), nullable=True),
        sa.Column("phosphorous", sa.Float(), nullable=True),
        sa.Column("poly_unsaturated_fat", sa.Float(), nullable=True),
        sa.Column("potassium", sa.Float(), nullable=True),
        sa.Column("protein", sa.Float(), nullable=True),
        sa.Column("saturated_fat", sa.Float(), nullable=True),
        sa.Column("selenium", sa.Float(), nullable=True),
        sa.Column("sodium", sa.Float(), nullable=True),
        sa.Column("sugar", sa.Float(), nullable=True),
        sa.Column("vitamin_a", sa.Float(), nullable=True),
        sa.Column("vitamin_b1", sa.Float(), nullable=True),
        sa.Column("vitamin_b12", sa.Float(), nullable=True),
        sa.Column("vitamin_b2", sa.Float(), nullable=True),
        sa.Column("vitamin_b3", sa.Float(), nullable=True),
        sa.Column("vitamin_b5", sa.Float(), nullable=True),
        sa.Column("vitamin_b6", sa.Float(), nullable=True),
        sa.Column("vitamin_c", sa.Float(), nullable=True),
        sa.Column("vitamin_d", sa.Float(), nullable=True),
        sa.Column("vitamin_e", sa.Float(), nullable=True),
        sa.Column("vitamin_k", sa.Float(), nullable=True),
        sa.Column("zinc", sa.Float(), nullable=True),
        sa.Column("glycemic_index", sa.Float(), nullable=True),
        sa.Column("glycemic_load", sa.Float(), nullable=True),
        sa.Column("estimated_cost_cents", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id", "recipe_id", "ingredient_id"),
    )
    op.create_table(
        "tags",
        sa.Column(
            "time_created",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("time_updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=128), nullable=True),
        sa.Column("public", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", "user_id", name="_user_tag_constraint"),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        sa.UniqueConstraint("user_id", "role_id", name="_user_role_constraint"),
    )
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id"),
        sa.UniqueConstraint("recipe_id", "tag_id", name="_recipe_tag_constraint"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("recipe_tags")
    op.drop_table("user_roles")
    op.drop_table("tags")
    op.drop_table("recipe_ingredients")
    op.drop_table("recipe_dish_types")
    op.drop_table("recipe_cuisines")
    op.drop_table("notes")
    op.drop_table("meal_recipes")
    op.drop_table("users")
    op.drop_table("shopping_lists")
    op.drop_table("recipes")
    op.drop_table("meals")
    op.drop_table("roles")
    op.drop_table("ingredients")
    op.drop_table("households")
    op.drop_table("dish_types")
    op.drop_table("cuisines")
    # ### end Alembic commands ###
