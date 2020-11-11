# flask imports
from flask import render_template
from flask_login import current_user
# common imports
from app import db
from app.ads import ads


@ads.route('/', methods=['GET'])
def home():
    return render_template('ads/home.html',
                           )
