from app import app
from flask import url_for


# Gets xmr stats
@app.template_filter()
def currentxmrprice(theid):
    from app.classes.monero import MoneroPrices
    from app import db

    moneroprice = db.session.query(MoneroPrices).filter_by(id=theid).first()
    theprice = moneroprice.price

    return theprice


# Gets btc stats
@app.template_filter()
def currentbtcprice(theid):
    from app.classes.btc import BtcPrices
    from app import db

    btcprice = db.session.query(BtcPrices).filter_by(id=theid).first()
    theprice = btcprice.price

    return theprice


# Gets btc stats donated
@app.template_filter()
def currentbchprice(theid):
    from app.classes.bch import BchPrices
    from app import db

    bchprice = db.session.query(BchPrices).filter_by(id=theid).first()
    theprice = bchprice.price

    return theprice


# Gets btc stats donated
@app.template_filter()
def currentltcprice(theid):
    from app.classes.user import LtcPrices
    from app import db

    ltcprice = db.session.query(LtcPrices).filter_by(id=theid).first()
    theprice = ltcprice.price

    return theprice


# Gets user profile picture
@app.template_filter('profilepicture')
def profilepicture(user_id):
    from app.classes.user import User
    from app import db

    getuser = db.session.query(User)
    getuser = getuser.filter(User.id == user_id).first()

    if getuser.profileimage == '':
        return url_for('common.profile_image', filename='noprofile.png')

    else:
        filenameofprofile = getuser.profileimage
        return url_for('common.profile_image', filename=filenameofprofile)


# Gets user level
@app.template_filter('userwidthtonextlevel')
def userwidthtonextlevel(user_id):
    from app.classes.user import UserStats
    from app import db
    from app.common.functions import floating_decimals

    userstatspoints = db.session.query(UserStats)
    userstatspoints = userstatspoints.filter_by(user_id=user_id).first()

    if 0 <= userstatspoints.user_level <= 3:
        user1widthh = (userstatspoints.user_exp / 300) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 4 <= userstatspoints.user_level <= 7:
        user1widthh = (userstatspoints.user_exp / 500) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 8 <= userstatspoints.user_level <= 10:
        user1widthh = (userstatspoints.user_exp / 1000) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 11 <= userstatspoints.user_level <= 14:
        user1widthh = (userstatspoints.user_exp / 1500) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 16 <= userstatspoints.user_level <= 20:
        user1widthh = (userstatspoints.user_exp / 2000) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 21 <= userstatspoints.user_level <= 25:
        user1widthh = (userstatspoints.user_exp / 2250) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 26 <= userstatspoints.user_level <= 30:
        user1widthh = (userstatspoints.user_exp / 5500) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 26 <= userstatspoints.user_level <= 30:
        user1widthh = (userstatspoints.user_exp / 10000) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 26 <= userstatspoints.user_level <= 30:
        user1widthh = (userstatspoints.user_exp / 15000) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 30 <= userstatspoints.user_level <= 50:
        user1widthh = (userstatspoints.user_exp / 20000) * 100
        user1width = floating_decimals(user1widthh, 0)
    elif 51 <= userstatspoints.user_level <= 100:
        user1widthh = (userstatspoints.user_exp / 25000) * 100
        user1width = floating_decimals(user1widthh, 0)
    else:
        user1widthh = (userstatspoints.user_exp / 1000) * 100
        user1width = floating_decimals(user1widthh, 0)
    return user1width


# Gets user level
@app.template_filter('userlevel')
def userlevel(user_id):
    from app.classes.user import UserStats
    from app import db

    userlevelnumber = db.session.query(UserStats)
    userlevelnumber = userlevelnumber.filter_by(user_id=user_id).first()

    thenumber = userlevelnumber.user_level
    return thenumber


# Gets user level
@app.template_filter('userupvotes')
def userupvotes(user_id):
    from app.classes.user import UserStats
    from app import db

    userlevelnumber = db.session.query(UserStats)
    userlevelnumber = userlevelnumber.filter_by(user_id=user_id).first()

    thenumber_comments = userlevelnumber.comment_upvotes
    thenumber_posts = userlevelnumber.post_upvotes
    thenumber = int(thenumber_comments) + int(thenumber_posts)
    return thenumber


# Gets user level
@app.template_filter('userdownvotes')
def userdownvotes(user_id):
    from app.classes.user import UserStats
    from app import db

    userlevelnumber = db.session.query(UserStats)
    userlevelnumber = userlevelnumber.filter_by(user_id=user_id).first()

    thenumber_comments = userlevelnumber.comment_downvotes
    thenumber_posts = userlevelnumber.post_downvotes
    thenumber = int(thenumber_comments) + int(thenumber_posts)
    return thenumber

# Gets user level
@app.template_filter('usertotalpost')
def usertotalpost(user_id):
    from app.classes.user import UserStats
    from app import db

    userlevelnumber = db.session.query(UserStats)
    userlevelnumber = userlevelnumber.filter(UserStats.user_id == user_id).first()

    thenumber = userlevelnumber.total_posts
    return thenumber


# Gets user level
@app.template_filter('usertotalcomment')
def usertotalcomment(user_id):
    from app.classes.user import UserStats
    from app import db

    userlevelnumber = db.session.query(UserStats)
    userlevelnumber = userlevelnumber.filter(UserStats.user_id == user_id).first()

    thenumber = userlevelnumber.total_comments
    return thenumber


# Gets user name
@app.template_filter('getuser_name')
def getuser_name(user_id):
    from app.classes.user import User
    from app import db
    try:
        userperson = db.session.query(User).filter(user_id == User.id).first()
        thename = userperson.user_name
        return thename
    except:
        return "tipvote"


# Gets user btc stats recieved
@app.template_filter('getuserbtcstats_total_recieved')
def getuserbtcstats_total_recieved(user_id):
    from app.classes.monero import UserStatsBTC
    from app import db

    total_btc_query = db.session.query(UserStatsBTC).filter(UserStatsBTC.user_id == user_id).first()
    total_btc_recieved = total_btc_query.total_recievedfromposts_btc + total_btc_query.total_recievedfromcomments_btc
    return total_btc_recieved


# Gets user btc stats donated
@app.template_filter('getuserbtcstats_total_donated')
def getuserbtcstats_total_donated(user_id):
    from app.classes.monero import UserStatsBTC
    from app import db

    total_btc_query = db.session.query(UserStatsBTC).filter(UserStatsBTC.user_id == user_id).first()
    total_btc_donated = total_btc_query.total_donated_to_postcomments_btc

    return total_btc_donated


# Gets user xmr stats recieved
@app.template_filter('getuserxmrstats_total_recieved')
def getuserxmrstats_total_recieved(user_id):
    from app.classes.monero import UserStatsXMR
    from app import db

    total_xmr_query = db.session.query(UserStatsXMR).filter(UserStatsXMR.user_id == user_id).first()
    total_xmr_recieved = total_xmr_query.total_recievedfromposts_xmr + total_xmr_query.total_recievedfromcomments_xmr
    return total_xmr_recieved


# Gets user xmr stats donated
@app.template_filter('getuserxmrstats_total_donated')
def getuserxmrstats_total_donated(user_id):
    from app.classes.monero import UserStatsXMR
    from app import db

    total_xmr_query = db.session.query(UserStatsXMR).filter(UserStatsXMR.user_id == user_id).first()
    total_xmr_donated = total_xmr_query.total_donated_to_postcomments_xmr

    return total_xmr_donated
