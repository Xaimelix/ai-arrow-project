import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class ChatHistory(SqlAlchemyBase):
    __tablename__ = 'chatHistory'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    context = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_user = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    is_text = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    user = orm.relationship('Users')