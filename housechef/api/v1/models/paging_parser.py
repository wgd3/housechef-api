from flask_restx import reqparse

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument(
    "per_page",
    type=int,
    help="Number of items to return per page",
    required=False,
    default=10,
)
pagination_parser.add_argument(
    "page",
    type=int,
    help="Which page of items to return",
    required=False,
    default=1,
)
pagination_parser.add_argument(
    "sort_by",
    choices=["id", "time_created", "time_updated", "name"],
    help="Sort result list by this column",
)
pagination_parser.add_argument(
    "sort_order",
    choices=[
        "asc",
        "desc",
    ],
    help="Sort direction",
)
