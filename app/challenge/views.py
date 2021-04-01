
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, request
from flask_login import current_user
from app import db
from werkzeug.datastructures import CombinedMultiDict
from app.business import business

from app.profile.forms import FriendForm
from app.create.forms import BusinessPostForm
from app.edit.forms import DeletePostTextForm
from app.business.forms import SubscribeForm

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute

from app.classes.post import CommonsPost
from app.classes.business import Business, BusinessFollowers, BusinessStats

from sqlalchemy import func
from datetime import datetime


@business.route('/<string:business_name>', methods=['GET'])
def main(business_name):


    return render_template('business/main.html')
