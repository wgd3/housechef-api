from flask_sqlalchemy import BaseQuery, Model
from sqlalchemy import asc, desc, inspect


def set_sort_order(
        query: BaseQuery, obj_model: Model, sort_order="asc", sort_by="id", *args, **kwargs
) -> BaseQuery:
    if sort_order is not None:
        sort = asc if sort_order == "asc" else desc
    else:
        sort = asc
    # sort = asc if sort_order == "asc" else desc
    column = next((c for c in inspect(obj_model).columns if c.name == sort_by), "id")
    return query.order_by(sort(column))


def set_search_filter(
        query: BaseQuery,
        obj_model: Model,
        search_field: str = None,
        search_value=None,
        *args,
        **kwargs,
) -> BaseQuery:
    """
    Utility for modifying a SQLAlchemy query by adding a filter. This uses the 'LIKE' modifier from SQL, and adds
    wildcards to either side of the query. This does _not_ support lists of values to search through

    Args:
        query:
        obj_model:
        search_field:
        search_value:
        *args:
        **kwargs:

    Returns:
        object:

    """
    if search_field is not None and search_value is not None:
        column = next(
            (c for c in inspect(obj_model).columns if c.name == search_field), None
        )
        if column is not None:
            query = query.filter(column.like(f"%{search_value}%"))

    return query
