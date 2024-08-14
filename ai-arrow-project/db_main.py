import os
from data import db_session
from flask import Flask

from data.user import Users
from data.context import ChatHistory


db_session.global_init("ai-arrow-project/db/history.db")
db_sess = db_session.create_session()

