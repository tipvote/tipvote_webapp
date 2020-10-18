# coding=utf-8
from flask import Flask, session
from flask import render_template
from datetime import timedelta
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import \
    CSRFProtect
from flask_qrcode import QRcode
from werkzeug.routing import BaseConverter

from sqlalchemy.orm import sessionmaker
from config import \
    SQLALCHEMY_DATABASE_URI_0, \
    WTF_CSRF_ENABLED, \
    UPLOADED_FILES_ALLOW, \
    MAX_CONTENT_LENGTH, \
    SECRET_KEY, \
    UPLOADED_FILES_DEST,\
    SESSION_PERMANENT,\
    WTF_CSRF_TIME_LIMIT, WTF_CSRF_SECRET_KEY

from flask_mistune import Mistune


app = Flask(__name__, static_url_path='',
            static_folder="/home/droid/tipvote/app/static",
            template_folder="/home/droid/tipvote/app/templates")


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


# ----------------------------------------------------------------------
app.config.from_object('config')

Session = sessionmaker()

# ----------------------------------------------------------------------
# configuration
app.url_map.converters['regex'] = RegexConverter
app.jinja_env.autoescape = True

app.config['UPLOADED_FILES_DEST'] = UPLOADED_FILES_DEST
app.config['UPLOADED_FILES_ALLOW'] = UPLOADED_FILES_ALLOW

app.config['SECRET_KEY'] = SECRET_KEY

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SESSION_PERMANENT'] = SESSION_PERMANENT
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['WTF_CSRF_ENABLED'] = WTF_CSRF_ENABLED
app.config['WTF_CSRF_TIME_LIMIT'] = WTF_CSRF_TIME_LIMIT
app.config['WTF_CSRF_SECRET_KEY'] = WTF_CSRF_SECRET_KEY

# ----------------------------------------------------------------------

Session.configure(bind=SQLALCHEMY_DATABASE_URI_0)
# ----------------------------------------------------------------------
csrf = CSRFProtect(app)
db = SQLAlchemy(app)

moment = Moment(app)
QRcode(app)
mail = Mail(app)
Mistune(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.anonymous_user = "Guest"
login_manager.login_view = 'users.login'
login_manager.needs_refresh_message = u"Session timed out, please re-login"
login_manager.needs_refresh_message_category = "info"


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=365)


from .common import filters, filters_btc, filters_xmr, filters_comments

# main
app.jinja_env.filters['user_name'] = filters.getuser_name
app.jinja_env.filters['profilepicture'] = filters.profilepicture
app.jinja_env.filters['currentxmrprice'] = filters.currentxmrprice
app.jinja_env.filters['currentbtcprice'] = filters.currentbtcprice
app.jinja_env.filters['currentbchprice'] = filters.currentbchprice
app.jinja_env.filters['currentltcprice'] = filters.currentltcprice

# coin filters profile stats
app.jinja_env.filters['getuserbtcstats_total_recieved'] = filters.getuserbtcstats_total_recieved
app.jinja_env.filters['getuserbtcstats_total_donated'] = filters.getuserbtcstats_total_donated
app.jinja_env.filters['getuserxmrstats_total_recieved'] = filters.getuserxmrstats_total_recieved
app.jinja_env.filters['getuserxmrstats_total_donated'] = filters.getuserxmrstats_total_donated

# btc
app.jinja_env.filters['btctousd'] = filters_btc.btctousd
app.jinja_env.filters['btcprice'] = filters_btc.btcprice
app.jinja_env.filters['btctostring'] = filters_btc.btctostring

# xmr
app.jinja_env.filters['xmrtocurrency'] = filters_xmr.xmrtocurrency
app.jinja_env.filters['xmrprice'] = filters_xmr.xmrprice
app.jinja_env.filters['xmrtousd'] = filters_xmr.xmrtousd
app.jinja_env.filters['xmrtostring'] = filters_xmr.xmrtostring
# ----------------------------------------------------------------------


@app.errorhandler(404)
def app_handle_404(e):
    return render_template('errors/404.html'), 404


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    x = db.session.query(User).filter(User.id == int(user_id)).first()
    return x

# ----------------------------------------------------------------------
# routing
# main

# profile
from .profile import profile as profile_blueprint
app.register_blueprint(profile_blueprint, url_prefix='/u')
from .profile import views

# business
from .business import business as business_blueprint
app.register_blueprint(business_blueprint, url_prefix='/b')
from .business import views

# subforum
from .subforum import subforum as subforum_blueprint
app.register_blueprint(subforum_blueprint, url_prefix='/a')
from .subforum import views

# all / landing / index
from .main import main as main_blueprint
app.register_blueprint(main_blueprint, url_prefix='/main')
from .main import views

# rooms
from .frontpage import frontpage as frontpage_blueprint
app.register_blueprint(frontpage_blueprint, url_prefix='/rooms')
from .frontpage import views

# followers
from .followers import followers as followers_blueprint
app.register_blueprint(followers_blueprint, url_prefix='/following')
from .followers import views

# user
from .users import users as users_blueprint
app.register_blueprint(users_blueprint, url_prefix='/user')
from .users import views

# admin
from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix='/admin')
from .admin import views

# common
from .common import common as common_blueprint
app.register_blueprint(common_blueprint, url_prefix='/common')
from .common import views

# tip
from .tip import tip as tip_blueprint
app.register_blueprint(tip_blueprint, url_prefix='/tip')
from .tip import views

# coins
from .coins import coins as coins_blueprint
app.register_blueprint(coins_blueprint, url_prefix='/coins')
from .coins import views

# vote
from .vote import vote as vote_blueprint
app.register_blueprint(vote_blueprint, url_prefix='/vote')
from .vote import views

# promote
from .promote import promote as promote_blueprint
app.register_blueprint(promote_blueprint, url_prefix='/promote')
from .promote import views

# mod
from .mod import mod as mod_blueprint
app.register_blueprint(mod_blueprint, url_prefix='/mod')
from .mod import views

# message
from .message import message as message_blueprint
app.register_blueprint(message_blueprint, url_prefix='/message')
from .message import views

# legal
from .legal import legal as legal_blueprint
app.register_blueprint(legal_blueprint, url_prefix='/legal')
from .legal import views

# ads
from .ads import ads as ads_blueprint
app.register_blueprint(ads_blueprint, url_prefix='/ads')
from .ads import views

# create
from .create import create as create_blueprint
app.register_blueprint(create_blueprint, url_prefix='/create')
from .create import views

# learn
from .learn import learn as learn_blueprint
app.register_blueprint(learn_blueprint, url_prefix='/learn')
from .learn import views

# edit
from .edit import edit as edit_blueprint
app.register_blueprint(edit_blueprint, url_prefix='/edit')
from .edit import views

from .business_edit import business_edit as business_edit_blueprint
app.register_blueprint(business_edit_blueprint, url_prefix='/businessedit')
from .business_edit import views


# profile photos
from .profile_photos import photos as photos_blueprint
app.register_blueprint(photos_blueprint, url_prefix='/photos')
from .profile_photos import views

from .profile_edit import profileedit as profileedit_blueprint
app.register_blueprint(profileedit_blueprint, url_prefix='/profileedit')
from .profile_edit import views


# wallets
# xmr
from .wallet_xmr import wallet_xmr as wallet_xmr_blueprint
app.register_blueprint(wallet_xmr_blueprint, url_prefix='/xmr')
from .wallet_xmr_stagenet import wallet_xmr_stagenet as wallet_xmr_stagenet_blueprint
app.register_blueprint(wallet_xmr_stagenet_blueprint, url_prefix='/xmrstagenet')


# btc
from .wallet_btc import wallet_btc as wallet_btc_blueprint
app.register_blueprint(wallet_btc_blueprint, url_prefix='/btc')

from .wallet_btc_test import wallet_btc_test as wallet_btc_test_blueprint
app.register_blueprint(wallet_btc_test_blueprint, url_prefix='/btctest')


# bch
from .wallet_bch import wallet_bch as wallet_bch_blueprint
app.register_blueprint(wallet_bch_blueprint, url_prefix='/bch')
# btc


db.configure_mappers()
db.create_all()
db.session.commit()

