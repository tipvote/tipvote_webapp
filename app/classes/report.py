# coding=utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, flash
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from datetime import datetime
import bleach
from markdown import markdown

# Posts that have been reported
class ReportedPosts(db.Model):
    __tablename__ = 'avengers_subforum_reported_posts'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    reporter_id = db.Column(db.Integer)
    reporter_user_name = db.Column(db.String(140))

    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    subcommon_name = db.Column(db.String(140))

    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    poster_user_id = db.Column(db.Integer)
    poster_user_name = db.Column(db.String(140))
    poster_visible_user_id = db.Column(db.Integer)
    poster_visible_user_name = db.Column(db.String(140))

# Posts that have been reported
class ReportedComments(db.Model):
    __tablename__ = 'avengers_subforum_reported_comments'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    reporter_id = db.Column(db.Integer)
    reporter_user_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    subcommon_name = db.Column(db.String(140))

    comment_id = db.Column(db.Integer)
    comment_body = db.Column(db.TEXT)
    commenter_user_id = db.Column(db.Integer)
    commenter_user_name = db.Column(db.String(140))
    commenter_visible_user_id = db.Column(db.Integer)
    commenter_visible_user_name = db.Column(db.String(140))

