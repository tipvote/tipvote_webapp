# coding=utf-8
from app import app


PORT = 5000
HOST = '0.0.0.0'
use_reloader = False
DEBUG = False

app.run(debug=DEBUG,
        host=HOST,
        port=PORT,
        threaded=True,
        use_reloader=use_reloader
        )
