
import datetime

import sqlalchemy
import sqlalchemy.types as types

import ckan.model as model
from ckan.model.meta import engine


class UnpublishedFeedback(model.DomainObject):
    """Model for Unpublished Feedback"""

    @classmethod
    def get(cls, **kw):
        """Get feedback for given filter params"""

        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    @classmethod
    def get_for_package(cls, package):
        """Get all feedback for a given package"""

        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(dataset=package).order_by(cls.modified.desc())

    @classmethod
    def count_for_package(cls, package):
        """Produce a sum of votes for unpublished datasets"""

        result = {}
        query = model.Session.query(cls).autoflush(False).filter(
            cls.dataset == package
        )
        return query.count()


def init_db():  # inspired by db.py from ckanext-pages

    unpublished_feedback_table = sqlalchemy.Table(
        'ckanext_unpublished_comments', model.meta.metadata,
        sqlalchemy.Column('id', types.Integer, primary_key=True),
        sqlalchemy.Column('user', types.String),
        sqlalchemy.Column('dataset', types.String),
        sqlalchemy.Column('comments', types.Text),
        sqlalchemy.Column('modified', types.DateTime,
                          default=datetime.datetime.utcnow)
    )

    try:
        model.meta.metadata.create_all(engine)
    except sqlalchemy.exc.ProgrammingError:
        pass

    model.meta.mapper(
        UnpublishedFeedback,
        unpublished_feedback_table,
    )
