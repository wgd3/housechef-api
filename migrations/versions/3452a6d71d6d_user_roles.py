"""user roles

Revision ID: 3452a6d71d6d
Revises: 98e15207e4ba
Create Date: 2021-03-01 12:53:41.508092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3452a6d71d6d"
down_revision = "98e15207e4ba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    # op.create_unique_constraint('_recipe_cuisine_constraint', 'recipe_cuisines', ['recipe_id', 'cuisine_id'])
    # op.create_unique_constraint('_recipe_dish_type_constraint', 'recipe_dish_types', ['recipe_id', 'dish_type_id'])
    # op.create_unique_constraint('_recipe_ingredient_constraint', 'recipe_ingredients', ['recipe_id', 'ingredient_id'])
    # op.create_unique_constraint('_recipe_tag_constraint', 'recipe_tags', ['recipe_id', 'tag_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_constraint('_recipe_tag_constraint', 'recipe_tags', type_='unique')
    # op.drop_constraint('_recipe_ingredient_constraint', 'recipe_ingredients', type_='unique')
    # op.drop_constraint('_recipe_dish_type_constraint', 'recipe_dish_types', type_='unique')
    # op.drop_constraint('_recipe_cuisine_constraint', 'recipe_cuisines', type_='unique')
    op.drop_table("user_roles")
    op.drop_table("roles")
    # ### end Alembic commands ###