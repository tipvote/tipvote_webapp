from passwords import \
    database_connection, \
    mailuser, \
    mailpass, \
    secretkey, \
    wtfkey


# LIVE CONNECTION
# used for live connection
# main
SQLALCHEMY_DATABASE_URI_0 = database_connection
SQLALCHEMY_BINDS = {
    'avengers': SQLALCHEMY_DATABASE_URI_0,
}
DEBUG = False

# END live Connection

# TEST CONNECTION
'''
# Utilize this for testing enviroment.  Add your username and password

# database name =  avengers
# schemas = avengers_admin, avengers_coins, avengers_comments, 
# avengers_main, avengers_msg, avengers_post, avengers_promotion, avengers_subforum,
# avengers_tips, avengers_user, avengers_user_business, avengers_wallet_bch,
# avengers_wallet_bch_test, avengers_wallet_btc, avengers_wallet_btc_test,
# avengers_wallet_monero,avengers_wallet_monero_stagenet, avengers_wallet_monero_testnet


# databases info
PSQL_USERNAME = 'username'
PSQL_PW = 'password'
PSQL_SERVER = '127.0.0.1:5432'

# this websites db
PSQL_DBNAME1 = 'avengers'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(PSQL_USERNAME,
                                                               PSQL_PW,
                                                               PSQL_SERVER,
                                                               PSQL_DBNAME1)
DEBUG = True
'''
# END Test connection


# hardcoded path for search
POSTS_PER_PAGE = 25

# Mail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = mailuser
MAIL_PASSWORD = mailpass
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_DEFAULT_SENDER = '"tipvote.com" <donotreply@tipvote.com>'

# Images
UPLOADED_FILES_DEST = '/nfs'

UPLOADED_FILES_ALLOW = ['png', 'jpeg', 'jpg', 'png', 'gif']
MAX_CONTENT_LENGTH = 5 * 2500 * 2500
ALLOWED_EXTENSIONS = ['png', 'jpeg', 'jpg', 'png', 'gif']

# secret keys
SECRET_KEY = secretkey
WTF_CSRF_TIME_LIMIT = None
WTF_CSRF_SECRET_KEY = wtfkey
WTF_CSRF_ENABLED = True
SESSION_PERMANENT = True


# sqlalchemy config
SQLALCHEMY_TRACK_MODIFICATIONS = False
TRAP_HTTP_EXCEPTIONS = True
PROPAGATE_EXCEPTIONS = True

# gunicorn config
pythonpath = '/home/droid/tipvote/venv/bin/python3'
bind = '0.0.0.0:5000'
proc_name = 'runProduction:app'
workers = 4
worker_rlimit_nofile = 20000
worker_connections = 1024


ALLOWED_HOSTS = [
    '127.0.0.1',
    '0.0.0.0'

]

btc_donate_to_me = '1LyX9Um4jevu49tkE6nZPaXHrna2gVa7Gy'

