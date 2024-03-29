# coding=utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, flash
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from datetime import datetime
import bleach
from markdown import markdown


class Streaming(db.Model):
    __tablename__ = 'streaming'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main"}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    online = db.Column(db.Integer)


class Updates(db.Model):
    __tablename__ = 'updates'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main"}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    update_version = db.Column(db.String(140))
    update_title = db.Column(db.String(140))
    information = db.Column(db.TEXT)
    github_url = db.Column(db.TEXT)


class GiveawayAll(db.Model):
    __tablename__ = 'avengers_promotion_giveaway_all'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_promotion"}

    id = db.Column(db.Integer, primary_key=True)
    # id of top post
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))
    # total amount raised for post
    total_usd = db.Column(db.DECIMAL(20, 2))
    # last promotion given
    last_promotion = db.Column(db.TIMESTAMP())
    # start of contest
    start_promotion = db.Column(db.TIMESTAMP())
    # end of contest
    end_promotion = db.Column(db.TIMESTAMP())
    # name of person leading contest
    leader_user_id = db.Column(db.Integer)
    leader_user_name = db.Column(db.String(140))


class Coins(db.Model):
    __tablename__ = 'coins'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_coins"}

    id = db.Column(db.Integer, primary_key=True)
    image_thumbnail = db.Column(db.String(300))
    created = db.Column(db.TIMESTAMP())
    # coin info
    coin_name = db.Column(db.String(140))
    coin_rarity = db.Column(db.Integer)
    coin_description = db.Column(db.TEXT)
    points_value = db.Column(db.Integer)


class DisplayCoins(db.Model):
    __tablename__ = 'displayrewardcoins'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_coins"}

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP())
    user_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    # coin info
    image_thumbnail_0 = db.Column(db.String(300))
    coin_name_0 = db.Column(db.String(140))
    coin_rarity_0 = db.Column(db.Integer)
    coin_description_0 = db.Column(db.TEXT)
    points_value_0 = db.Column(db.Integer)

    # coin info
    image_thumbnail_1 = db.Column(db.String(300))
    coin_name_1 = db.Column(db.String(140))
    coin_rarity_1 = db.Column(db.Integer)
    coin_description_1 = db.Column(db.TEXT)
    points_value_1 = db.Column(db.Integer)

    seen_by_user = db.Column(db.Integer)
    new_user_level = db.Column(db.Integer)


class TempUrl(db.Model):
    __tablename__ = 'temp_url'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_subforum"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.INTEGER)
    timestamp = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    url = db.Column(db.TEXT)
    title = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    image = db.Column(db.TEXT)
    subcommon_name = db.Column(db.String(140))
    subcommon_id = db.Column(db.Integer)


class RecentTips(db.Model):
    __tablename__ = 'avengers_tips_stats_recent'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_tips"}

    id = db.Column(db.Integer, primary_key=True)
    # identify forum, post, and comment
    subcommon_id = db.Column(db.Integer, db.ForeignKey('avengers_subforum.avengers_subforum_subforum.id'))
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    subcommon_name = db.Column(db.String(140))
    created_user_id = db.Column(db.Integer)
    created_user_name = db.Column(db.String(140))
    recieved_user_id = db.Column(db.Integer)
    recieved_user_name = db.Column(db.String(140))

    # amounts
    currency_type = db.Column(db.Integer)
    amount_btc = db.Column(db.DECIMAL(20, 8))
    amount_bch = db.Column(db.DECIMAL(20, 8))
    amount_xmr = db.Column(db.DECIMAL(20, 12))
    amount_usd = db.Column(db.DECIMAL(20, 2))


class ExpTable(db.Model):
    __tablename__ = 'user_exp'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user"}

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    type = db.Column(db.INTEGER)
    amount = db.Column(db.INTEGER)
    created = db.Column(db.TIMESTAMP())


