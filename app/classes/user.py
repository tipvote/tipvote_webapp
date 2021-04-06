from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from datetime import datetime
import bleach
from markdown import markdown


class DailyChallenge(db.Model):
    __tablename__ = 'daily_challenge'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name_of_challenge = db.Column(db.TEXT)
    image_of_challenge = db.Column(db.TEXT)
    how_many_to_complete = db.Column(db.Integer)
    category_of_challenge = db.Column(db.Integer)
    reward_amount = db.Column(db.TEXT)
    reward_coin = db.Column(db.Integer)


class UserDailyChallenge(db.Model):
    __tablename__ = 'user_daily_challenge'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    user_id = db.Column(db.Integer)
    id_of_challenge = db.Column(db.Integer)
    category_of_challenge = db.Column(db.Integer)
    name_of_challenge = db.Column(db.TEXT)
    image_of_challenge = db.Column(db.TEXT)
    how_many_to_complete = db.Column(db.Integer)
    current_number_of_times = db.Column(db.Integer)
    starts = db.Column(db.TIMESTAMP())
    ends = db.Column(db.TIMESTAMP())
    completed = db.Column(db.Integer)
    user_width_next_level = db.Column(db.Integer)
    reward_amount = db.Column(db.TEXT)
    reward_coin= db.Column(db.Integer)



class SavedAddresses(db.Model):
    __tablename__ = 'user_crypto_addresses'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    user_id = db.Column(db.Integer)
    bitcoin_address = db.Column(db.TEXT)
    bitcoin_cash_address = db.Column(db.TEXT)
    monero_address = db.Column(db.TEXT)



class PgpKey(db.Model):
    __tablename__ = 'user_pgpkey'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    # from to
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    user_name = db.Column(db.String(140))
    key = db.Column(db.TEXT)



class SavedPost(db.Model):
    __tablename__ = 'user_saved_posts'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('avengers_post.avengers_posts_posts.id'))


class PgpKey(db.Model):
    __tablename__ = 'user_pgpkey'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    # from to
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    user_name = db.Column(db.String(140))
    key = db.Column(db.TEXT)


class UserLargePublicInfo(db.Model):
    __tablename__ = 'user_large_public_info'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    bio = db.Column(db.TEXT)
    bio_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.bio_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(UserLargePublicInfo.bio, 'set', UserLargePublicInfo.on_changed_body)


class UserStatsXMR(db.Model):
    __tablename__ = 'user_stats_xmr'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    # given to posters/commenters
    total_donated_to_postcomments_xmr = db.Column(db.DECIMAL(20, 12))
    total_donated_to_postcomments_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from posting
    total_recievedfromposts_xmr = db.Column(db.DECIMAL(20, 12))
    total_recievedfromposts_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from comments
    total_recievedfromcomments_xmr = db.Column(db.DECIMAL(20, 12))
    total_recievedfromcomments_usd = db.Column(db.DECIMAL(20, 2))

    # given to charities
    total_donated_to_cause_xmr = db.Column(db.DECIMAL(20, 12))
    total_donated_to_cause_usd = db.Column(db.DECIMAL(20, 2))


class UserStatsBTC(db.Model):
    __tablename__ = 'user_stats_btc'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    # given to posters/commenters
    total_donated_to_postcomments_btc = db.Column(db.DECIMAL(20, 8))
    total_donated_to_postcomments_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from posting
    total_recievedfromposts_btc = db.Column(db.DECIMAL(20, 8))
    total_recievedfromposts_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from comments
    total_recievedfromcomments_btc = db.Column(db.DECIMAL(20, 8))
    total_recievedfromcomments_usd = db.Column(db.DECIMAL(20, 2))

    # given to charities
    total_donated_to_cause_btc = db.Column(db.DECIMAL(20, 8))
    total_donated_to_cause_usd = db.Column(db.DECIMAL(20, 2))


class UserStatsBCH(db.Model):
    __tablename__ = 'user_stats_bch'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    # given to posters/commenters
    total_donated_to_postcomments_bch = db.Column(db.DECIMAL(20, 8))
    total_donated_to_postcomments_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from posting
    total_recievedfromposts_bch = db.Column(db.DECIMAL(20, 8))
    total_recievedfromposts_usd = db.Column(db.DECIMAL(20, 2))

    # recieved from comments
    total_recievedfromcomments_bch = db.Column(db.DECIMAL(20, 8))
    total_recievedfromcomments_usd = db.Column(db.DECIMAL(20, 2))

    # given to charities
    total_donated_to_cause_bch = db.Column(db.DECIMAL(20, 8))
    total_donated_to_cause_usd = db.Column(db.DECIMAL(20, 2))


class UserTimers(db.Model):
    __tablename__ = 'user_timers'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer)
    account_created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_post = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_common_creation = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_comment = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    last_report = db.Column(db.TIMESTAMP(), default=datetime.utcnow())


class UserPublicInfo(db.Model):
    __tablename__ = 'user_public_info'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    bio = db.Column(db.TEXT)
    bio_clean = db.Column(db.TEXT)
    short_bio = db.Column(db.TEXT)
    short_bio_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.bio_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_two(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.short_bio_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(UserPublicInfo.bio, 'set', UserPublicInfo.on_changed_body)
db.event.listen(UserPublicInfo.short_bio, 'set', UserPublicInfo.on_changed_body_two)

class UserStats(db.Model):
    __tablename__ = 'user_stats_common'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    comment_upvotes = db.Column(db.INTEGER)
    comment_downvotes = db.Column(db.INTEGER)
    post_upvotes = db.Column(db.INTEGER)
    post_downvotes = db.Column(db.INTEGER,)
    total_posts = db.Column(db.INTEGER)
    total_comments = db.Column(db.INTEGER)
    user_level = db.Column(db.INTEGER)
    user_exp = db.Column(db.INTEGER)
    user_width_next_level = db.Column(db.String)

class BlockedUser(db.Model):
    __tablename__ = 'blocked'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    blocked_user = db.Column(db.Integer)
    blocked_user_name = db.Column(db.TEXT)

class Followers(db.Model):
    __tablename__ = 'followers'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

class BannedUser(db.Model):
    __tablename__ = 'banneduser'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    user_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer)
    reason_for_ban = db.Column(db.TEXT)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    banner_user_id = db.Column(db.Integer)
    banner_user_name = db.Column(db.String(140))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user", 'useexisting': True}

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)

    user_name = db.Column(db.TEXT)
    password_hash = db.Column(db.TEXT)
    email = db.Column(db.TEXT)
    member_since = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    wallet_pin = db.Column(db.TEXT)
    profileimage = db.Column(db.TEXT)
    bannerimage = db.Column(db.TEXT)
    last_seen = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    admin = db.Column(db.INTEGER)
    admin_role = db.Column(db.INTEGER)

    anon_id = db.Column(db.TEXT)
    anon_mode = db.Column(db.INTEGER)
    over_age = db.Column(db.BOOLEAN, default=False)

    confirmed = db.Column(db.INTEGER)
    fails = db.Column(db.INTEGER)
    locked = db.Column(db.INTEGER)
    banned = db.Column(db.INTEGER)
    post_style = db.Column(db.INTEGER)
    color_theme = db.Column(db.INTEGER)
    agree_to_tos = db.Column(db.BOOLEAN, default=False)

    contentownerposts = db.relationship('CommonsPost', backref='contentownerposts', lazy='dynamic',
                                        primaryjoin="User.id == CommonsPost.content_user_id")
    userposts = db.relationship('CommonsPost', backref='userposts', lazy='dynamic',
                                primaryjoin="User.id == CommonsPost.user_id")
    poster_posts = db.relationship('CommonsPost', backref='posterposts', lazy='dynamic',
                                   primaryjoin="User.id == CommonsPost.poster_user_id")
    usercomments = db.relationship('Comments', backref='usercomments', lazy='dynamic',
                                   primaryjoin="User.id == Comments.user_id")
    coins_user_coins = db.relationship('UserCoins', backref='usercoins', lazy='dynamic',
                                       cascade="all,delete")
    coins_display_user_coins = db.relationship('DisplayCoins', backref='displaycoins', cascade="all,delete")
    main_notes = db.relationship('Notifications', backref='notes', lazy='dynamic', cascade="all,delete")
    user_exptable = db.relationship('ExpTable', backref='exp', lazy='dynamic', cascade="all,delete")
    blocked_users = db.relationship('BlockedUser', backref='blocked', lazy='dynamic', cascade="all,delete")
    userpublicinfo = db.relationship('UserPublicInfo', backref='userinfo', uselist=False, cascade="all,delete")
    user_stats_common = db.relationship('UserStats', backref='userstats', uselist=False, cascade="all,delete")
    user_stats_btc = db.relationship('UserStatsBTC', backref='userstatsbtc', uselist=False, cascade="all,delete")
    user_stats_xmr = db.relationship('UserStatsXMR', backref='userstatsxmr', uselist=False, cascade="all,delete")
    user_stats_bch = db.relationship('UserStatsBCH', backref='userstatsbch', uselist=False, cascade="all,delete")
    user_pgp_key = db.relationship('PgpKey', backref='user_pgp_key', uselist=False, cascade="all,delete")

    sender_msg = db.relationship('Messages', backref='sendermsg', lazy='dynamic', cascade="all,delete",
                                 primaryjoin="User.id == Messages.sender_user_id")
    rec_msg = db.relationship('Messages', backref='recmsg', lazy='dynamic', cascade="all,delete",
                              primaryjoin="User.id == Messages.rec_user_id")

    reply_sender_msg = db.relationship('Reply', backref='replysendermsg', lazy='dynamic', cascade="all,delete",
                                       primaryjoin="User.id == Reply.sender_user_id")
    reply_rec_msg = db.relationship('Reply', backref='replyrecmsg', lazy='dynamic', cascade="all,delete",
                                    primaryjoin="User.id == Reply.rec_user_id")

    legal_sender_msg = db.relationship('LegalMessages', backref='legal_sendermsg', lazy='dynamic', cascade="all,delete",
                                       primaryjoin="User.id == LegalMessages.sender_user_id")
    legal_rec_msg = db.relationship('LegalMessages', backref='legal_recmsg', lazy='dynamic', cascade="all,delete",
                                    primaryjoin="User.id == LegalMessages.rec_user_id")

    legal_reply_sender_msg = db.relationship('LegalReply', backref='legal_replysendermsg', lazy='dynamic', cascade="all,delete",
                                             primaryjoin="User.id == LegalReply.sender_user_id")
    legal_reply_rec_msg = db.relationship('LegalReply', backref='legal_replyrecmsg', lazy='dynamic', cascade="all,delete",
                                          primaryjoin="User.id == LegalReply.rec_user_id")

    # business
    user_biz = db.relationship('Business', backref='userbiz', lazy='dynamic')

    # bch wallet
    bch = db.relationship('BchWallet', backref='bch', uselist=False)
    user_bch_transactions = db.relationship('TransactionsBch', backref='user_bch_transactions', lazy='dynamic')
    user_bch_unconfirmed = db.relationship('BchUnconfirmed', backref='user_bch_unconfirmed', lazy='dynamic')

    # btc wallet
    btc = db.relationship('BtcWallet', backref='btc', uselist=False)
    user_btc_transactions = db.relationship('TransactionsBtc', backref='user_btc_transactions', lazy='dynamic')
    user_btc_unconfirmed = db.relationship('BtcUnconfirmed', backref='user_btc_unconfirmed', lazy='dynamic')

    # xmr wallet
    xmr = db.relationship('MoneroWallet', backref='xmr', uselist=False)
    user_xmr_transactions = db.relationship('MoneroTransactions', backref='user_xmr_transactions', lazy='dynamic')
    user_xmr_unconfirmed = db.relationship('MoneroUnconfirmed', backref='user_xmr_unconfirmed', lazy='dynamic')

    followed = db.relationship('User',
                               secondary='avengers_user.followers',
                               primaryjoin=Followers.follower_id == id,
                               secondaryjoin=Followers.followed_id == id,
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic',
                               cascade="all,delete"
                               )

    def __init__(self,
                 user_name,
                 password_hash,
                 wallet_pin,
                 member_since,
                 profileimage,
                 bannerimage,
                 bio,
                 last_seen,
                 admin,
                 admin_role,
                 fails,
                 locked,
                 anon_id,
                 anon_mode,
                 over_age,
                 email,
                 agree_to_tos,
                 confirmed,
                 banned,
                 color_theme,
                 post_style
                 ):

        self.user_name = user_name
        self.password_hash = password_hash
        self.wallet_pin = wallet_pin
        self.member_since = member_since
        self.profileimage = profileimage
        self.bannerimage = bannerimage
        self.bio = bio
        self.last_seen = last_seen
        self.admin = admin
        self.admin_role = admin_role
        self.fails = fails
        self.locked = locked
        self.anon_id = anon_id
        self.anon_mode = anon_mode
        self.over_age = over_age
        self.email = email
        self.agree_to_tos = agree_to_tos
        self.confirmed = confirmed
        self.banned = banned
        self.color_theme = color_theme

        self.post_style = post_style
    # user followers
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            Followers.followed_id == user.id).count() > 0


    # password encryption
    @staticmethod
    def cryptpassword(password):
        return generate_password_hash(password)

    @staticmethod
    def decryptpassword(pwdhash, password):
        return check_password_hash(pwdhash, password)

    # user status
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # email auth token
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)

        return s.dumps({'id': self.id}).decode('ascii')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)

        return True

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.user_name

class UserCoins(db.Model):
    __tablename__ = 'usercoins'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_coins", 'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer)

    image_thumbnail = db.Column(db.String(300))

    user_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    obtained = db.Column(db.TIMESTAMP())
    quantity = db.Column(db.Integer)

    # coin info
    coin_name = db.Column(db.String(140))
    coin_rarity = db.Column(db.Integer)
    coin_description = db.Column(db.TEXT)
    points_value = db.Column(db.Integer)

class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.user_name = 'Guest'


login_manager.anonymous_user = AnonymousUser
