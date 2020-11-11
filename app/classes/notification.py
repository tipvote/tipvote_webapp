from app import db
from datetime import datetime
import bleach
from markdown import markdown


class Notifications(db.Model):
    __tablename__ = 'avengers_msg_notifications'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    read = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)
    msg_type = db.Column(db.Integer)
