from app import db
from datetime import datetime
import bleach
from markdown import markdown

from app.classes.message import LegalMessages

class Subscribed(db.Model):
    __tablename__ = 'subscribed_rooms'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))

class SubForumStats(db.Model):
    __tablename__ = 'avengers_subforum_subforum_Stats'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}
    id = db.Column(db.Integer, primary_key=True)
    subcommon_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    total_posts = db.Column(db.Integer)
    total_exp_subcommon = db.Column(db.Integer)
    members = db.Column(db.Integer)

    def __repr__(self):
        return '<Subcommon {}>'.format(self.subcommon_name)

class PayoutSubOwner(db.Model):
    __tablename__ = 'avengers_tips_payout_subowner'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    sub_owner_user_id = db.Column(db.Integer)
    sub_owner_user_name = db.Column(db.String(140))
    tipper_user_id = db.Column(db.Integer)
    tipper_user_name = db.Column(db.String(140))

    # amounts
    currency_type = db.Column(db.Integer)
    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_bch = db.Column(db.DECIMAL(20, 8))
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_usd = db.Column(db.DECIMAL(20, 2))

class SubForumCustom(db.Model):
    __tablename__ = 'avengers_subforum_subforum_custom'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}
    id = db.Column(db.Integer, primary_key=True)
    subcommon_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    banner_image = db.Column(db.String(140))
    mini_image = db.Column(db.String(140))

    def __repr__(self):
        return '<Subcommon {}>'.format(self.subcommon_name)


class SubForumCustomInfoOne(db.Model):
    __tablename__ = 'avengers_subforum_subforum_info_one'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}
    id = db.Column(db.Integer, primary_key=True)
    subcommon_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    enabled = db.Column(db.Integer)
    description = db.Column(db.TEXT)
    description_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.description_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(SubForumCustomInfoOne.description, 'set', SubForumCustomInfoOne.on_changed_body)


class PrivateMembers(db.Model):
    __tablename__ = 'avengers_subforum_privatemembers'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))


class PrivateApplications(db.Model):
    __tablename__ = 'avengers_subforum_privatemembers_application'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    user_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    message = db.Column(db.TEXT)
    message_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.message_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(PrivateApplications.message, 'set', LegalMessages.on_changed_body)


# the subforums
class SubForums(db.Model):
    __tablename__ = 'avengers_subforum_subforum'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('CommonsPost', backref='posts', lazy='dynamic')

    subscription = db.relationship('Subscribed', backref='subscriber', lazy='dynamic')
    privmembers = db.relationship('PrivateMembers', backref='privatemembers', lazy='dynamic')
    privapps = db.relationship('PrivateMembers', backref='privateapps', lazy='dynamic')
    recenttips = db.relationship('RecentTips', backref='recentips', lazy='dynamic')
    subcustom = db.relationship('SubForumCustom', backref='custom', uselist=False)
    custominfoone = db.relationship('SubForumCustomInfoOne', backref='infoone', uselist=False)
    substats = db.relationship('SubForumStats', backref='stats', uselist=False)
    reported_posts = db.relationship('ReportedPosts', backref='reportedposts', lazy='dynamic')
    reported_comments = db.relationship('ReportedComments', backref='reportedcomments', lazy='dynamic')
    mods = db.relationship('Mods', backref='mods', lazy='dynamic')
    banned = db.relationship('Banned', backref='banned', lazy='dynamic')
    muted = db.relationship('Muted', backref='muted', lazy='dynamic')

    subcommon_name = db.Column(db.String(140))
    # date created
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    creator_user_id = db.Column(db.Integer)
    creator_user_name = db.Column(db.String(140))

    type_of_subcommon = db.Column(db.Integer)
    exp_required = db.Column(db.Integer)
    age_required = db.Column(db.Integer)
    allow_text_posts = db.Column(db.Integer)
    allow_url_posts = db.Column(db.Integer)
    allow_image_posts = db.Column(db.Integer)
    total_exp_subcommon = db.Column(db.Integer)
    members = db.Column(db.Integer)
    mini_image = db.Column(db.String(140))

    room_banned = db.Column(db.Integer)
    room_suspended = db.Column(db.Integer)
    room_deleted = db.Column(db.Integer)

    description = db.Column(db.TEXT)
    description_clean = db.Column(db.TEXT)

    def __repr__(self):
        return '<Subcommon {}>'.format(self.subcommon_name)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe',
                        'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
                            'a': ['href', 'rel'],
                            'img': ['src', 'alt']
                        }
        target.description_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(SubForums.description, 'set', SubForums.on_changed_body)

# banned sub users
class Mods(db.Model):
    __tablename__ = 'avengers_subforum_mods'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(140))

    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))

# banned sub users
class Banned(db.Model):
    __tablename__ = 'avengers_subforum_banned'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))

# tempbanned sub users
class Muted(db.Model):
    __tablename__ = 'avengers_subforum_muted'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(140))

    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    muted_start = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    muted_end = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
