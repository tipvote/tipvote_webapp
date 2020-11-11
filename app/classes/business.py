from app import db
from datetime import datetime
import bleach
from markdown import markdown


class Business(db.Model):
    __tablename__ = 'business'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_name = db.Column(db.TEXT)
    user_id = db.Column(db.Integer, db.ForeignKey('avengers_user.users.id'))

    business_name = db.Column(db.TEXT)
    official_business_name = db.Column(db.TEXT)
    business_tag = db.Column(db.String(150))
    business_id = db.Column(db.INTEGER)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    age = db.Column(db.INTEGER)

    profileimage = db.Column(db.TEXT)
    bannerimage = db.Column(db.TEXT)

    subscription = db.relationship('BusinessFollowers', backref='bizsubscriber', lazy='dynamic')

    contentownerposts = db.relationship('CommonsPost', backref='bizownerposts', lazy='dynamic',
                                        primaryjoin="Business.id == CommonsPost.business_id")

    biz_stats = db.relationship('BusinessStats', uselist=False, backref='user_biz_stats')
    biz_info = db.relationship('BusinessInfo', uselist=False, backref='user_biz_info')
    biz_bio = db.relationship('BusinessSpecificInfo', uselist=False, backref='user_biz_bio')
    biz_services = db.relationship('BusinessServices', uselist=False, backref='user_biz_services')
    biz_location = db.relationship('BusinessLocation', uselist=False, backref='user_biz_location')
    biz_accepts = db.relationship('BusinessAccepts', uselist=False, backref='user_biz_accepts')
    biz_msgs = db.relationship('Messages', backref='biz_msg', lazy='dynamic')
    biz_replys = db.relationship('Reply', backref='biz_reply', lazy='dynamic')


class BusinessSpecificInfo(db.Model):
    __tablename__ = 'business_specific_info'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)

    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
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


db.event.listen(BusinessSpecificInfo.bio, 'set', BusinessSpecificInfo.on_changed_body)


class BusinessFollowers(db.Model):
    __tablename__ = 'business_followers'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))


class BusinessAccepts(db.Model):
    __tablename__ = 'business_accepts_currency'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    accepts_bitcoin = db.Column(db.INTEGER)
    accepts_bitcoin_cash = db.Column(db.INTEGER)
    accepts_monero = db.Column(db.INTEGER)


class BusinessStats(db.Model):
    __tablename__ = 'business_stats'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    total_upvotes = db.Column(db.INTEGER)
    total_downvotes = db.Column(db.INTEGER)
    total_followers = db.Column(db.INTEGER)
    total_reviews = db.Column(db.INTEGER)
    page_views = db.Column(db.INTEGER)


class BusinessInfo(db.Model):
    __tablename__ = 'business_info'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    phone_number = db.Column(db.TEXT)
    phone_number_clean = db.Column(db.TEXT)
    email = db.Column(db.TEXT)
    email_clean = db.Column(db.TEXT)
    about = db.Column(db.TEXT)
    about_clean = db.Column(db.TEXT)
    website = db.Column(db.TEXT)
    website_clean = db.Column(db.TEXT)
    facebook = db.Column(db.TEXT)
    facebook_clean = db.Column(db.TEXT)
    twitter = db.Column(db.TEXT)
    twitter_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.phone_number_clean = bleach.linkify(bleach.clean(
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
        target.email_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_three(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.about_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_four(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.website_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_five(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.facebook_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_six(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.twitter_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(BusinessInfo.phone_number, 'set', BusinessInfo.on_changed_body)
db.event.listen(BusinessInfo.email, 'set', BusinessInfo.on_changed_body_two)
db.event.listen(BusinessInfo.about, 'set', BusinessInfo.on_changed_body_three)
db.event.listen(BusinessInfo.website, 'set', BusinessInfo.on_changed_body_four)
db.event.listen(BusinessInfo.facebook, 'set', BusinessInfo.on_changed_body_five)
db.event.listen(BusinessInfo.twitter, 'set', BusinessInfo.on_changed_body_six)


class BusinessServices(db.Model):
    __tablename__ = 'business_service'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    one_enabled = db.Column(db.INTEGER)
    info_one = db.Column(db.TEXT)
    info_one_clean = db.Column(db.TEXT)
    two_enabled = db.Column(db.INTEGER)
    info_two = db.Column(db.TEXT)
    info_two_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.info_one_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_two(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.info_two_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(BusinessServices.info_one, 'set', BusinessServices.on_changed_body)
db.event.listen(BusinessServices.info_two, 'set', BusinessServices.on_changed_body_two)


class BusinessLocation(db.Model):
    __tablename__ = 'business_location'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_user_business", 'useexisting': True}

    id = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('avengers_user_business.business.id'))
    address = db.Column(db.TEXT)
    address_clean = db.Column(db.TEXT)
    town = db.Column(db.TEXT)
    town_clean = db.Column(db.TEXT)
    state_or_province = db.Column(db.TEXT)
    state_or_province_clean = db.Column(db.TEXT)
    country = db.Column(db.TEXT)
    country_clean = db.Column(db.TEXT)
    zipcode = db.Column(db.TEXT)
    zipcode_clean = db.Column(db.TEXT)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.address_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_two(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.town_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_three(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.state_or_province_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_four(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.country_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))

    @staticmethod
    def on_changed_body_five(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div',
                        'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {
            'a': ['href', 'rel'],
            'img': ['src', 'alt']}
        target.zipcode_clean = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


db.event.listen(BusinessLocation.address, 'set', BusinessLocation.on_changed_body)
db.event.listen(BusinessLocation.town, 'set', BusinessLocation.on_changed_body_two)
db.event.listen(BusinessLocation.state_or_province, 'set', BusinessLocation.on_changed_body_three)
db.event.listen(BusinessLocation.country, 'set', BusinessLocation.on_changed_body_four)
db.event.listen(BusinessLocation.zipcode, 'set', BusinessLocation.on_changed_body_five)
