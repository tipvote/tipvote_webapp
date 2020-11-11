from app import db
from datetime import datetime
import bleach
from markdown import markdown


# used so no double upvoting
class PostUpvotes(db.Model):
    __tablename__ = 'avengers_posts_upvotes'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_post", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    vote_up = db.Column(db.Integer)
    vote_down = db.Column(db.Integer)


class CommonsPost(db.Model):
    __tablename__ = 'avengers_posts_posts'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_post", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))

    # the person recieving the post or posters wall
    user_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    visible_user_id = db.Column(db.Integer)
    visible_user_name = db.Column(db.String(140))
    userhidden = db.Column(db.Integer)

    # the poster
    poster_user_name = db.Column(db.String(140))
    poster_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    poster_visible_user_id = db.Column(db.Integer)
    poster_visible_user_name = db.Column(db.String(140))
    poster_userhidden = db.Column(db.Integer)

    # origonal post creator if shared
    content_user_name = db.Column(db.String(100))
    content_user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    creator_anon = db.Column(db.Integer)

    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    subcommon_name = db.Column(db.String(140))

    saved = db.relationship('SavedPost', backref='saved', lazy='dynamic', cascade="all,delete")
    reported_posts = db.relationship('ReportedPosts', backref='postreports', lazy='dynamic',
                                     cascade="all,delete")

    giveaway_post = db.relationship('GiveawayAll', backref='giveawayall', uselist=False)
    # tips
    xmr_post_tips = db.relationship('XmrPostTips', backref='xmrtips', lazy='dynamic')
    btc_post_tips = db.relationship('BtcPostTips', backref='btctips', lazy='dynamic')
    bch_post_tips = db.relationship('BchPostTips', backref='bchtips', lazy='dynamic')

    # Coins
    post_coins = db.relationship('PostCoins', backref='postcoins', uselist=False)
    post_donations = db.relationship('PostDonations', backref='postdonations',  uselist=False)
    post_promotions = db.relationship('PostPromotions', backref='postpromotions',  uselist=False)

    realid = db.Column(db.String(40))
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    edited = db.Column(db.TIMESTAMP(), default=datetime.utcnow)

    crawlneed = db.Column(db.Integer)
    type_of_post = db.Column(db.Integer)
    age = db.Column(db.Integer)

    comment_count = db.Column(db.Integer)
    vote_timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    last_active = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    active = db.Column(db.Integer)
    locked = db.Column(db.Integer)
    hidden = db.Column(db.Integer)
    muted = db.Column(db.Integer)
    downvotes_on_post = db.Column(db.Integer)
    upvotes_on_post = db.Column(db.Integer)
    hotness_rating_now = db.Column(db.Integer)
    total_exp_commons = db.Column(db.Integer)
    highest_exp_reached = db.Column(db.Integer)
    decay_rate = db.Column(db.String(5))
    page_views = db.Column(db.Integer)
    sticky = db.Column(db.Integer)

    # origonal id of post
    shared_post = db.Column(db.Integer)
    shared_time = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    shared_thoughts = db.Column(db.TEXT)

    thecomments = db.relationship('Comments', backref='postcomments', lazy='dynamic', cascade="all,delete")
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))

    # the text of post
    url_image = db.Column(db.TEXT)
    url_title = db.Column(db.TEXT)
    url_of_post = db.Column(db.TEXT)
    url_description = db.Column(db.TEXT)
    url_image_server = db.Column(db.TEXT)
    image_server_1 = db.Column(db.TEXT)
    post_text = db.Column(db.TEXT)
    post_text_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h1', 'h5', 'h6',
                         'img', 'video', 'div', 'iframe',
                         'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}

        target.post_text_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags,

            attributes=allowed_attrs)
        )

    def __repr__(self):
        return '<Post {}>'.format(self.post_text)

db.event.listen(CommonsPost.post_text, 'set', CommonsPost.on_changed_body)

class PostDonations(db.Model):
    __tablename__ = 'avengers_post_donations'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_post", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))
    # promotions
    total_recieved_btc = db.Column(db.DECIMAL(20, 8))
    total_recieved_btc_usd = db.Column(db.DECIMAL(20, 2))

    total_recieved_bch = db.Column(db.DECIMAL(20, 8))
    total_recieved_bch_usd = db.Column(db.DECIMAL(20, 2))

    total_recieved_xmr = db.Column(db.DECIMAL(20, 12))
    total_recieved_xmr_usd = db.Column(db.DECIMAL(20, 2))

class PostPromotions(db.Model):
    __tablename__ = 'avengers_post_promotions'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_post", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))
    # tipvote coins
    total_recieved_btc = db.Column(db.DECIMAL(20, 8))
    total_recieved_btc_usd = db.Column(db.DECIMAL(20, 2))

    total_recieved_bch = db.Column(db.DECIMAL(20, 8))
    total_recieved_bch_usd = db.Column(db.DECIMAL(20, 2))

    total_recieved_xmr = db.Column(db.DECIMAL(20, 12))
    total_recieved_xmr_usd = db.Column(db.DECIMAL(20, 2))


class PostPromote(db.Model):
    __tablename__ = 'avengers_promotion_post'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_promotion", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # from to
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))
    post_id = db.Column(db.Integer)

    # amounts
    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_bch = db.Column(db.DECIMAL(20, 8))
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class PostCoins(db.Model):
    __tablename__ = 'avengers_post_coins'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_post", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    coin_1 = db.Column(db.Integer)
    coin_2 = db.Column(db.Integer)
    coin_3 = db.Column(db.Integer)
    coin_4 = db.Column(db.Integer)
    coin_5 = db.Column(db.Integer)
    coin_6 = db.Column(db.Integer)
    coin_7 = db.Column(db.Integer)
    coin_8 = db.Column(db.Integer)
    coin_9 = db.Column(db.Integer)
    coin_10 = db.Column(db.Integer)

class BtcPostTips(db.Model):
    __tablename__ = 'avengers_tips_btc_posts'
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
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    # amounts
    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class XmrPostTips(db.Model):
    __tablename__ = 'avengers_tips_xmr_posts'
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
    post_id = db.Column(db.Integer,  db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    # amounts
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class BchPostTips(db.Model):
    __tablename__ = 'avengers_tips_bch_posts'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer,  db.ForeignKey('avengers_post.avengers_posts_posts.id'))

    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())

    # from to
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))
    recieved_user_id = db.Column(db.Integer)
    recieved_user_name = db.Column(db.String(140))

    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer)
    subcommon_name = db.Column(db.String(140))

    # amounts
    amount_bch = db.Column(db.DECIMAL(20, 8))
    amount_usd = db.Column(db.DECIMAL(20, 2))
