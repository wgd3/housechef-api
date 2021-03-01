from flask import url_for
from flask_sqlalchemy import Pagination


def generate_query_metadata(paginate: Pagination):
    return {
        "_meta": {
            "per_page": paginate.per_page,
            "page": paginate.page,
            "total_items": paginate.total,
            "total_pages": paginate.pages,
        }
    }


def generate_link_metadata(paginate: Pagination, endpoint: str, **kwargs):
    return {
        "_links": {
            "self": url_for(endpoint, **kwargs),
            "next": url_for(
                endpoint,
                **{**kwargs, **{"page": paginate.next_num}},
            )
            if paginate.has_next
            else None,
            "prev": url_for(
                endpoint,
                **{**kwargs, **{"page": paginate.prev_num}},
            )
            if paginate.has_prev
            else None,
        },
    }
