# coding=utf-8
from app import app

PORT = 5010
HOST = '0.0.0.0'
if __name__ == '__main__':
        app.run(
                host=HOST,
                port=PORT,
                threaded=True
        )
