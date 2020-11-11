# coding=utf-8
from app import app

PORT = 5000
HOST = '0.0.0.0'
if __name__ == '__main__':
        app.run(
                host=HOST,
                port=PORT,
                threaded=True
        )
