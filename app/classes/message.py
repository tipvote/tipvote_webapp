from app import db
from datetime import datetime
import bleach
from markdown import markdown


class LegalMessages(db.Model):
    __tablename__ = 'msg_messages_legal'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_msg"}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_message = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    read_rec = db.Column(db.Integer)
    read_send = db.Column(db.Integer)
    msg_type = db.Column(db.Integer)

    sender_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    sender_user_user_name = db.Column(db.String(120))

    rec_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    rec_user_user_name = db.Column(db.String(120))

    biz_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    biz_name = db.Column(db.String(120))

    body = db.Column(db.TEXT)
    body_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.body_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

db.event.listen(LegalMessages.body, 'set', LegalMessages.on_changed_body)


class LegalReply(db.Model):
    __tablename__ = 'msg_messages_replies_legal'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_msg"}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    message_id = db.Column(db.Integer)

    sender_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    sender_user_user_name = db.Column(db.String(120))

    rec_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    rec_user_user_name = db.Column(db.String(120))

    biz_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    biz_name = db.Column(db.String(120))

    body = db.Column(db.TEXT)
    body_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.body_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

db.event.listen(LegalReply.body, 'set', LegalReply.on_changed_body)


class Messages(db.Model):
    __tablename__ = 'msg_messages'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_msg"}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_message = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    read_rec = db.Column(db.Integer)
    read_send = db.Column(db.Integer)
    msg_type = db.Column(db.Integer)

    sender_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    sender_user_user_name = db.Column(db.String(120))

    rec_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    rec_user_user_name = db.Column(db.String(120))

    biz_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    biz_name = db.Column(db.String(120))

    body = db.Column(db.TEXT)
    body_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.body_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(Messages.body, 'set', Messages.on_changed_body)


class Reply(db.Model):
    __tablename__ = 'msg_messages_replies'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_msg"}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    message_id = db.Column(db.Integer)

    sender_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    sender_user_user_name = db.Column(db.String(120))

    rec_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    rec_user_user_name = db.Column(db.String(120))

    biz_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    biz_name = db.Column(db.String(120))

    body = db.Column(db.TEXT)
    body_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.body_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(Reply.body, 'set', Reply.on_changed_body)
