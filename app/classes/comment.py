from app import db
from datetime import datetime
import bleach
from markdown import markdown


# List of user ids and commentupvotes
class CommentsUpvotes(db.Model):
    __tablename__ = 'avengers_comments_upvotes'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_comments", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)


class BtcCommentTips(db.Model):
    __tablename__ = 'avengers_tips_btc_comments'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # from to
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))
    recieved_user_id = db.Column(db.Integer)
    recieved_user_name = db.Column(db.String(140))

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    # amounts
    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class XmrCommentTips(db.Model):
    __tablename__ = 'avengers_tips_xmr_comments'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # from to
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))
    recieved_user_id = db.Column(db.Integer)
    recieved_user_name = db.Column(db.String(140))

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    # amounts
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class BchCommentTips(db.Model):
    __tablename__ = 'avengers_tips_bch_comments'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # from to
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))
    recieved_user_id = db.Column(db.Integer)
    recieved_user_name = db.Column(db.String(140))

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    # amounts
    amount_bch = db.Column(db.DECIMAL(20, 8))
    amount_usd = db.Column(db.DECIMAL(20, 2))



class Comments(db.Model):
    __tablename__ = 'avengers_comments_comments'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_comments", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    # each comment increases..replaced id for comment pathing
    index_id = db.Column(db.Integer)
    # future variable perhaps for security
    realid = db.Column(db.String(40))

    # time created
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)

    # connect for vote commentupvotes
    commons_post_id = db.Column(db.Integer,
                                db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    # user_name
    user_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    visible_user_id = db.Column(db.Integer)
    visible_user_name = db.Column(db.String(140))
    userhidden = db.Column(db.Integer)

    # stats
    total_exp_commons = db.Column(db.Integer)
    downvotes_on_comment = db.Column(db.Integer)
    upvotes_on_comment = db.Column(db.Integer)

    # reported
    active = db.Column(db.Integer)
    hidden = db.Column(db.Integer)
    deleted = db.Column(db.Integer)

    # donations
    total_recieved_btc = db.Column(db.DECIMAL(20, 8))
    total_recieved_btc_usd = db.Column(db.DECIMAL(20, 2))
    total_recieved_xmr = db.Column(db.DECIMAL(20, 12))
    total_recieved_xmr_usd = db.Column(db.DECIMAL(20, 2))
    total_recieved_bch = db.Column(db.DECIMAL(20, 8))
    total_recieved_bch_usd = db.Column(db.DECIMAL(20, 2))
    subcommon_id = db.Column(db.Integer)

    # used for sorting
    thread_timestamp = db.Column(db.TIMESTAMP())
    thread_upvotes = db.Column(db.Integer)
    thread_downvotes = db.Column(db.Integer)

    # the content
    body = db.Column(db.TEXT)
    body_clean = db.Column(db.Text)

    # factor how many digits ..6 = 1 million
    _N = 6

    # pathing
    path = db.Column(db.TEXT, index=True)
    comment_parent_id = db.Column(db.Integer,
                                  db.ForeignKey('avengers_comments.avengers_comments_comments.id'))
    replies = db.relationship('Comments',
                              backref=db.backref('parent',
                                                 remote_side=[id]),
                              lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.index_id, self._N)

        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1
