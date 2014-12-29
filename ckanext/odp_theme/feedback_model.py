
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
        """Produce a dict summing votes for different incentives to release
           a dataset"""

        result = {}
        query = model.Session.query(cls).autoflush(False).filter(
            cls.dataset == package
        )
        cols = {
            'economic': cls.economic_comment,
            'social': cls.social_comment,
            'public_service': cls.public_service_comment,
            'other': cls.other_comment
        }
        for key, col in cols.iteritems():
            result[key] = query.filter(col != None).count()
        return result


def init_db():  # inspired by db.py from ckanext-pages

    unpublished_feedback_table = sqlalchemy.Table(
        'ckanext_unpublished_feedback', model.meta.metadata,
        sqlalchemy.Column('id', types.Integer, primary_key=True),
        sqlalchemy.Column('user', types.String),
        sqlalchemy.Column('dataset', types.String),
        sqlalchemy.Column('economic_comment', types.Text),
        sqlalchemy.Column('social_comment', types.Text),
        sqlalchemy.Column('public_service_comment', types.Text),
        sqlalchemy.Column('other_comment', types.Text),
        sqlalchemy.Column('reponding_for_org', types.Boolean),
        sqlalchemy.Column('future_contact', types.Boolean),
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
