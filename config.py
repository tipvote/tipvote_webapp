from passwords import \
    database_connection, \
    mailuser, \
    mailpass, \
    secretkey, \
    wtfkey


test = 0

if test == 1:
    UPLOADED_FILES_DEST = '/nfs/tipvote'
    pythonpath = '/../../tipvote/venv/bin/python3'
    bind = '0.0.0.0:5010'
    proc_name = 'runLan:app'
    workers = 4
    worker_rlimit_nofile = 20000
    worker_connections = 1024
else:
    UPLOADED_FILES_DEST = '/nfs/tipvote'
    pythonpath = '/../../tipvote/venv/bin/python3'
    bind = '0.0.0.0:5010'
    proc_name = 'runProduction:app'
    workers = 4
    worker_rlimit_nofile = 20000
    worker_connections = 1024

# main
SQLALCHEMY_DATABASE_URI_0 = database_connection

SQLALCHEMY_BINDS = {
    'avengers': SQLALCHEMY_DATABASE_URI_0,
}
DEBUG = False

# hardcoded path for search
POSTS_PER_PAGE = 20

# Mail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = mailuser
MAIL_PASSWORD = mailpass
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_DEFAULT_SENDER = '"donotreply@tipvote.com" <donotreply@tipvote.com>'
MAIL_DEBUG = True
TESTING = False
MAIL_SUPPRESS_SEND = False

# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 465
# MAIL_USERNAME = 'eddwinn@gmail.com'
# MAIL_PASSWORD = '!Julie774edwin943'
# MAIL_USE_SSL = True
# MAIL_USE_TLS = False
# MAIL_DEFAULT_SENDER = '"eddwinn@gmail.com" <eddwinn@gmail.com>'
# MAIL_DEBUG = True
# TESTING = False
# MAIL_SUPPRESS_SEND = False


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

ALLOWED_HOSTS = [
    '127.0.0.1',
    '0.0.0.0'
]
