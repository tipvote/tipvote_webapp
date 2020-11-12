# coding=utf-8
from flask import Flask, session, request, abort
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
            static_folder="static",
            template_folder="templates")

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
app.jinja_env.filters['seeifvoted'] = filters_comments.seeifvoted
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
    from app.classes.user import User
    x = db.session.query(User).filter(User.id == int(user_id)).first()
    return x

# ----------------------------------------------------------------------
# routing
# main

from .profile import profile as profile_blueprint
from .business import business as business_blueprint
from .subforum import subforum as subforum_blueprint
from .main import main as main_blueprint
from .frontpage import frontpage as frontpage_blueprint
from .followers import followers as followers_blueprint
from .users import users as users_blueprint
from .admin import admin as admin_blueprint
from .common import common as common_blueprint
from .tip import tip as tip_blueprint
from .coins import coins as coins_blueprint
from .vote import vote as vote_blueprint
from .promote import promote as promote_blueprint
from .mod import mod as mod_blueprint
from .message import message as message_blueprint
from .legal import legal as legal_blueprint
from .ads import ads as ads_blueprint
from .create import create as create_blueprint
from .learn import learn as learn_blueprint
from .edit import edit as edit_blueprint
from .business_edit import business_edit as business_edit_blueprint
from .profile_photos import photos as photos_blueprint
from .profile_edit import profileedit as profileedit_blueprint
from .wallet_xmr import wallet_xmr as wallet_xmr_blueprint
from .wallet_xmr_stagenet import wallet_xmr_stagenet as wallet_xmr_stagenet_blueprint
from .wallet_btc import wallet_btc as wallet_btc_blueprint
from .wallet_btc_test import wallet_btc_test as wallet_btc_test_blueprint
from .wallet_bch import wallet_bch as wallet_bch_blueprint

from app.classes.module import Module, ModuleException

modules = [
    Module(profile_blueprint,'/u','profile'),
    Module(business_blueprint,'/b','business'),
    Module(subforum_blueprint,'/a','subforum'),
    Module(main_blueprint,'/main','main'),
    Module(frontpage_blueprint,'/rooms','frontpage'),
    Module(followers_blueprint,'/following','followers'),
    Module(users_blueprint,'/user','user'),
    Module(admin_blueprint,'/admin','admin'),
    Module(common_blueprint,'/common','common'),
    Module(tip_blueprint,'/tip','tip'),
    Module(coins_blueprint,'/coins','coins'),
    Module(vote_blueprint,'/vote','vote'),
    Module(promote_blueprint,'/promote','promote'),
    Module(mod_blueprint,'/mod','mod'),
    Module(message_blueprint,'/message','message'),
    Module(legal_blueprint,'/legal','legal'),
    Module(ads_blueprint,'/ads','ads'),
    Module(create_blueprint,'/create','create'),
    Module(learn_blueprint,'/learn','learn'),
    Module(edit_blueprint,'/edit','edit'),
    Module(business_edit_blueprint,'/businessedit','business_edit'),
    Module(photos_blueprint,'/photos','photos'),
    Module(profileedit_blueprint,'/profileedit','profileedit'),
    Module(wallet_xmr_blueprint,'/xmr','wallet_xmr'),
    Module(wallet_xmr_stagenet_blueprint,'/xmrstagenet','wallet_xmr_stagenet'),
    Module(wallet_btc_blueprint,'/btc','wallet_btc'),
    Module(wallet_btc_test_blueprint,'/btctest','wallet_btc_test'),
    Module(wallet_bch_blueprint,'/bch','wallet_bch')
]

# Register all modules
for m in modules:
    app.register_blueprint(m.blueprint,url_prefix=m.url_prefix)
    m.blueprint._got_registered_once = False

import threading
from werkzeug.security import generate_password_hash, check_password_hash
module_password = ''

# Rerolls module key every 50 seconds
def reroll_module_key():
    import secrets
    import time
    global module_password
    while True:
        randno = secrets.token_hex(32)
        print(f'New password: {randno}')
        module_password = generate_password_hash(randno)
        time.sleep(60*60)

new_pass = threading.Thread(target=reroll_module_key, args=())
new_pass.start()

# Takeoff blueprint
# https://github.com/pallets/flask/issues/2308, flask does not implement
# de-register app.view_functions, so we are going to do it ourselves!
@app.route('/reload/list', methods = ['GET'])
def reload():
    global module_password

    key = request.values.get('key')

    if check_password_hash(module_password,key) == False:
        abort(404)

    string = ''
    
    i = 0;

    for b in app.blueprints:
        string = f'{string}<h1>{b}</h1><hr><i>Click on any function to reload the {b} module</i><br>'
        for f in app.view_functions:
            n = f.split('.')
            if n[0] != b:
                continue
            string = f'{string}<br><a href="/reload/single?package={n[0]}&key={key}&name={b}&blueprint_index={i}">{f}</a>'
            i += 1

    return f'Functions reloadable\n\r{string}',200

@app.route('/reload/single', methods = ['GET'])
def reload_single():
    import importlib
    global module_password

    key = request.values.get('key')
    package = request.values.get('package')
    name = request.values.get('name')
    blueprint_index = int(request.values.get('blueprint_index'))

    if check_password_hash(module_password,key) == False:
        abort(404)

    # Remove caches and redo stuff
    importlib.invalidate_caches()

    # Import by variable name
    _temp = __import__(f'app.{package}.__init__', globals(), locals(), [package], 0)
    new_blueprint = getattr(_temp,package)
    new_blueprint.name = modules[blueprint_index].name
    modules[blueprint_index].blueprint = new_blueprint

    # Temporarily remove from blueprint name
    del app.blueprints[modules[blueprint_index].name]
    
    app.register_blueprint(
        modules[blueprint_index].blueprint,
        url_prefix=modules[blueprint_index].url_prefix)

    app.blueprints[modules[blueprint_index].name] = modules[blueprint_index].blueprint
    return f'Module {package} reloaded!',200

db.configure_mappers()
db.create_all()
db.session.commit()

