from flask_restx import fields

links_envelope = {
    "name": "meta_envelope",
    "fields": {
        "self": fields.String(),
        "next": fields.String(),
        "prev": fields.String(),
    },
}

meta_envelope = {
    "name": "links_envelope",
    "fields": {
        "per_page": fields.Integer,
        "page": fields.Integer,
        "total_pages": fields.Integer,
        "total_items": fields.Integer,
    },
}

response_envelope = {
    "name": "response_envelope",
    "fields": {
        "data": fields.Raw(),
        "message": fields.String(),
    },
}
