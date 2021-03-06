from flask import \
    render_template,\
    redirect,\
    url_for
from flask_login import current_user
from app import db
from app.coins import coins

from app.classes.btc import BtcPrices
from app.classes.monero import MoneroPrices
from app.classes.bch import BchPrices
from app.classes.ltc import LtcPrices
from app.classes.notification import Notifications
from app.classes.models import Coins
from app.classes.subforum import SubForums, Subscribed
from app.classes.user import UserCoins, DailyChallenge, UserDailyChallenge
from sqlalchemy import or_, func
from datetime import datetime


@coins.route('/', methods=['GET'])
def overview():

    """
    landing page for coins...shows users what coins he owns and how to get them etc
    :return:
    """

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)
    allcoins = db.session.query(Coins).all()

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(25)
    else:
        thenotes = 0
        thenotescount = 0

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.all()
        guestsubforums = None
    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.room_banned == 0,
                                               SubForums.room_deleted == 0,
                                               SubForums.room_suspended == 0
                                               )
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    # get users daily missions
    if current_user.is_authenticated:
        getuserdaily = db.session.query(UserDailyChallenge)\
            .filter(UserDailyChallenge.user_id == current_user.id)\
            .all()
    else:
        getuserdaily = db.session.query(DailyChallenge)\
            .order_by(func.random())\
            .limit(2)

    return render_template('coins/overview.html',
                           now=datetime.utcnow(),

                           # general
                           getuserdaily=getuserdaily,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           thenotes=thenotes,
                           thenotescount=thenotescount,

                           # coin prices
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           allcoins=allcoins,
                           )


@coins.route('/bank', methods=['GET'])
def bank():

    """
    Shows user coins
    :return:
    """
    if current_user.is_authenticated:
        pass
    else:
        return redirect(url_for('coins.overview'))
    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(25)
    else:
        thenotes = 0
        thenotescount = 0

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.all()

    # queries
    usercoins = db.session.query(UserCoins).filter(UserCoins.user_id == current_user.id).all()

    allcoins = db.session.query(Coins).all()

    return render_template('coins/bank.html',
                           now=datetime.utcnow(),
                           # forms
                           # general
                           usersubforums=usersubforums,
                           thenotes=thenotes,
                           # coin prices
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           # queries
                           usercoins=usercoins,
                           thenotescount=thenotescount,
                           allcoins=allcoins,
                           )
