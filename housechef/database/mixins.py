import datetime as dt
import enum
import json

from sqlalchemy import not_
from sqlalchemy.sql import func

from housechef.extensions import db

Column = db.Column
relationship = db.relationship


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, dt):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class SerializableMixin(object):
    """Base SQLAlchemy Model for automatic serialization and
    deserialization of columns and nested relationships.
    Usage::
        >>> class User(Model):
        >>>     id = db.Column(db.Integer(), primary_key=True)
        >>>     email = db.Column(db.String(), index=True)
        >>>     name = db.Column(db.String())
        >>>     password = db.Column(db.String())
        >>>     posts = db.relationship('Post', backref='user', lazy='dynamic')
        >>>     ...
        >>>     default_fields = ['email', 'name']
        >>>     hidden_fields = ['password']
        >>>     readonly_fields = ['email', 'password']
        >>>
        >>> class Post(Model):
        >>>     id = db.Column(db.Integer(), primary_key=True)
        >>>     user_id = db.Column(db.String(), db.ForeignKey('user.id'), nullable=False)
        >>>     title = db.Column(db.String())
        >>>     ...
        >>>     default_fields = ['title']
        >>>     readonly_fields = ['user_id']
        >>>
        >>> model = User(email='john@localhost')
        >>> db.session.add(model)
        >>> db.session.commit()
        >>>
        >>> # update name and create a new post
        >>> validated_input = {'name': 'John', 'posts': [{'title':'My First Post'}]}
        >>> model.set_columns(**validated_input)
        >>> db.session.commit()
        >>>
        >>> print(model.to_dict(show=['password', 'posts']))
        >>> {u'email': u'john@localhost', u'posts': [{u'id': 1, u'title': u'My First Post'}], u'name': u'John', u'id': 1}
    """

    # Stores changes made to this model's attributes. Can be retrieved
    # with model.changes
    _changes = {}

    def __init__(self, **kwargs):
        kwargs["_force"] = True
        self._set_columns(**kwargs)

    def _set_columns(self, **kwargs):
        force = kwargs.get("_force")

        readonly = []
        if hasattr(self, "readonly_fields"):
            readonly = self.readonly_fields
        if hasattr(self, "hidden_fields"):
            readonly += self.hidden_fields

        readonly += [
            "id",
            "time_created",
            "time_updated",
        ]

        changes = {}

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()

        for key in columns:
            allowed = True if force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    changes[key] = {"old": val, "new": kwargs[key]}
                    setattr(self, key, kwargs[key])

        for rel in relationships:
            allowed = True if force or rel not in readonly else False
            exists = True if rel in kwargs else False
            if allowed and exists:
                is_list = self.__mapper__.relationships[rel].uselist
                if is_list:
                    valid_ids = []
                    query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    for item in kwargs[rel]:
                        if (
                            "id" in item
                            and query.filter_by(id=item["id"]).limit(1).count() == 1
                        ):
                            obj = cls.query.filter_by(id=item["id"]).first()
                            col_changes = obj.set_columns(**item)
                            if col_changes:
                                col_changes["id"] = str(item["id"])
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(item["id"]))
                        else:
                            col = cls()
                            col_changes = col.set_columns(**item)
                            query.append(col)
                            db.session.flush()
                            if col_changes:
                                col_changes["id"] = str(col.id)
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(col.id))

                    # delete related rows that were not in kwargs[rel]
                    for item in query.filter(not_(cls.id.in_(valid_ids))).all():
                        col_changes = {
                            "id": str(item.id),
                            "deleted": True,
                        }
                        if rel in changes:
                            changes[rel].append(col_changes)
                        else:
                            changes.update({rel: [col_changes]})
                        db.session.delete(item)

                else:
                    val = getattr(self, rel)
                    if self.__mapper__.relationships[rel].query_class is not None:
                        if val is not None:
                            col_changes = val.set_columns(**kwargs[rel])
                            if col_changes:
                                changes.update({rel: col_changes})
                    else:
                        if val != kwargs[rel]:
                            setattr(self, rel, kwargs[rel])
                            changes[rel] = {"old": val, "new": kwargs[rel]}

        return changes

    def set_columns(self, **kwargs):
        self._changes = self._set_columns(**kwargs)
        if "modified" in self.__table__.columns:
            self.modified = dt.utcnow()
        if "updated" in self.__table__.columns:
            self.updated = dt.utcnow()
        if "modified_at" in self.__table__.columns:
            self.modified_at = dt.utcnow()
        if "updated_at" in self.__table__.columns:
            self.updated_at = dt.utcnow()
        return self._changes

    @property
    def changes(self):
        return self._changes

    def reset_changes(self):
        self._changes = {}

    def to_dict(self, show=None, hide=None, path=None, show_all=None):
        """Return a dictionary representation of this model."""

        if not show:
            show = []
        if not hide:
            hide = []
        hidden = []
        if hasattr(self, "hidden_fields"):
            hidden = self.hidden_fields
        default = []
        if hasattr(self, "default_fields"):
            default = self.default_fields

        ret_data = {}

        if not path:
            path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split(".", 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = ".%s" % item
                item = "%s%s" % (path, item)
                return item

            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = "%s.%s" % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is "id" or check in show or key in default:
                val = getattr(self, key)
                if isinstance(val, (dt.datetime, dt.date)):
                    ret_data[key] = val.isoformat()
                elif isinstance(val, (enum.Enum,)):
                    ret_data[key] = val.value
                else:
                    ret_data[key] = getattr(self, key)

        for key in relationships:
            check = "%s.%s" % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    ret_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(
                            item.to_dict(
                                show=show,
                                hide=hide,
                                path=("%s.%s" % (path, key.lower())),
                                show_all=show_all,
                            )
                        )
                else:
                    if self.__mapper__.relationships[key].query_class is not None:
                        ret_data[key] = getattr(self, key).to_dict(
                            show=show,
                            hide=hide,
                            path=("%s.%s" % (path, key.lower())),
                            show_all=show_all,
                        )
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            check = "%s.%s" % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                try:
                    ret_data[key] = json.loads(json.dumps(val, cls=DateTimeEncoder))
                except:
                    pass

        return ret_data


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


class TimestampMixin(object):
    time_created = Column(db.DateTime, default=func.now(), server_default=func.now())
    time_updated = Column(db.DateTime, onupdate=func.now())


class PkModel(Model):
    """Base model class that includes CRUD convenience methods, plus adds a 'primary key' column named ``id``."""

    __abstract__ = True
    id = Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
            (
                isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            return cls.query.get(int(record_id))
        return None


class LookupByNameMixin(object):
    @classmethod
    def get_by_name(cls, name: str):
        if hasattr(cls, "username"):
            return cls.query.filter(cls.username.lower() == name.lower())
        return cls.query.filter(cls.name.lower() == name.lower()).one_or_none()


def reference_col(
    tablename: str,
    nullable=False,
    pk_name="id",
    foreign_key_kwargs=None,
    column_kwargs=None,
):
    """Column that adds primary key foreign key reference.
    Usage: ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        db.ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )
