from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, \
    request

from itsdangerous import URLSafeTimedSerializer
from app.sendmsg import send_email

from werkzeug.datastructures import CombinedMultiDict
from flask_login import current_user
from datetime import datetime
from sqlalchemy import or_
from app.common.decorators import login_required

from app import db, app
from app.main.forms import ApplyToPrivate, CreateUpdateForm
from app.subforum.forms import SubscribeForm, JoinRoomForm
from app.vote.forms import VoteForm
from app.create.forms import MainPostForm

from app.models import \
    Subscribed, \
    SubForums, \
    CommonsPost, \
    PrivateApplications, \
    RecentTips, \
    BtcPrices, \
    MoneroPrices, \
    BchPrices, \
    LtcPrices, \
    DisplayCoins, \
    Notifications, \
    User, \
    Business, \
    BusinessStats, \
    BusinessFollowers, \
    Messages,\
    Mods, \
    GiveawayAll, \
    Updates

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute


@app.route('/', methods=['GET', 'POST'])
def index():

    """
    Returns index page and hottest posts
    :return:
    """
    now = datetime.utcnow()
    navlink = 1

    subform = SubscribeForm()
    voteform = VoteForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)

    if current_user.is_authenticated:
        # see if user leveled up and has a display to flash
        seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
        if seeiflevelup is not None:
            for levelup in seeiflevelup:
                flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
                flash("Your have recieved 2 new coins", category='success')
                db.session.delete(levelup)
            db.session.commit()

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        therecmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        thesendmsgs = sendmsgs.count()

        themsgs = int(thesendmsgs) + int(therecmsgs)
    else:
        themsgs = 0

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.filter(Notifications.read == 0)
        thenotes = thenotes.count()

    else:
        thenotes = 0

    # owned business
    if current_user.is_authenticated:
        userbusiness = db.session.query(Business)
        userbusiness = userbusiness.filter(Business.user_id == current_user.id)
        userbusinesses = userbusiness.all()
        userbusinessescount = userbusiness.count()
    else:
        userbusinesses = None
        userbusinessescount = 0

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    if current_user.is_authenticated:
        # get subs user belongs too
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.all()
        guestsubforums = None

        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()


    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.filter(SubForums.room_banned == 0,
                                               SubForums.room_deleted == 0,
                                               SubForums.room_suspended == 0
                                               )
        guestsubforums = guestsubforums.filter(SubForums.id != 1, SubForums.id != 13)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(7)
        usersubforums = None
        seeifmod = None
        moddingcount = None
        seeifowner = None
        ownercount = None

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = \
            [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None

    # get current giveaway
    thegiveaway = GiveawayAll.query.order_by(GiveawayAll.id.desc()).first()

    # Trending
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(5)
    recent_tippers_post_count = recent_tippers_post.count()

    # get total tips
    totaltips = db.session.query(RecentTips).count()

    if current_user.is_authenticated:
        if current_user.over_age is False:
            post_18 = 0
            allpost = 0
        else:
            allpost = 0
            post_18 = 1
    else:
        post_18 = 0
        allpost = 0

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.order_by(CommonsPost.hotness_rating_now.desc(), CommonsPost.created.desc())
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html',
                           now=now,
                           # forms
                           subform=subform,
                           voteform=voteform,
                           mainpostform=mainpostform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,

                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           themsgs=themsgs,
                           recent_tippers_post_count=recent_tippers_post_count,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           navlink=navlink,
                           thenotes=thenotes,
                           thegiveaway=thegiveaway,
                           totaltips=totaltips,

                           # queries/pagination
                           recent_tippers_post=recent_tippers_post,

                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           # coin prices
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,

                           )


@app.route('/newest', methods=['GET'])
def newest():

    """
    Returns index page and hottest posts
    :return:
    """
    subform = SubscribeForm()
    voteform = VoteForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    navlink = 2

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)
    now = datetime.utcnow()
    if current_user.is_authenticated:
        # see if user leveled up and has a display to flash
        seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
        if seeiflevelup is not None:
            for levelup in seeiflevelup:
                flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
                flash("Your have recieved 2 new coins", category='success')
                db.session.delete(levelup)
            db.session.commit()

    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.filter(Notifications.read == 0)
        thenotes = thenotes.count()
    else:
        thenotes = 0

    if current_user.is_authenticated:
        # get subs user belongs too
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
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

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name))
                                         for row in usersubforums]
    else:
        mainpostform = None

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    # owned business
    if current_user.is_authenticated:
        userbusiness = db.session.query(Business)
        userbusiness = userbusiness.filter(Business.user_id == current_user.id)
        userbusinesses = userbusiness.all()
        userbusinessescount = userbusiness.count()
    else:
        userbusinesses = None
        userbusinessescount = 0

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    # Trending
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(10)
    recent_tippers_post_count = recent_tippers_post.count()

    if current_user.is_authenticated:
        if current_user.over_age is False:
            post_18 = 0
            allpost = 0
        else:
            allpost = 0
            post_18 = 1
    else:
        post_18 = 0
        allpost = 0

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.order_by(CommonsPost.created.desc())

    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('newest', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('newest', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html',
                           now=now,
                           # forms
                           subform=subform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           mainpostform=mainpostform,
                           # general

                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           thenotes=thenotes,
                           themsgs=themsgs,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,

                           navlink=navlink,
                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@app.route('/active', methods=['GET'])
def mostactive():

    """
    Returns index page and hottest posts
    :return:
    """
    subform = SubscribeForm()
    voteform = VoteForm()

    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    navlink = 3

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)
    now = datetime.utcnow()
    if current_user.is_authenticated:
        # see if user leveled up and has a display to flash
        seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
        if seeiflevelup is not None:
            for levelup in seeiflevelup:
                flash("You have leveled up to level: " + str(levelup.new_user_leve), category='success')
                flash("Your have recieved 2 new coins", category='success')
                db.session.delete(levelup)
            db.session.commit()

    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.filter(Notifications.read == 0)
        thenotes = thenotes.count()
    else:
        thenotes = 0

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.all()
        guestsubforums = None

        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()

    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None
        seeifmod = None
        moddingcount = None
        seeifowner = None
        ownercount = None

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None

    if current_user.is_authenticated:
        if current_user.over_age is False:
            post_18 = 0
            allpost = 0
        else:
            allpost = 0
            post_18 = 1
    else:
        post_18 = 0
        allpost = 0

    # owned business
    if current_user.is_authenticated:
        userbusiness = db.session.query(Business)
        userbusiness = userbusiness.filter(Business.user_id == current_user.id)
        userbusinesses = userbusiness.all()
        userbusinessescount = userbusiness.count()
    else:
        userbusinesses = None
        userbusinessescount = 0

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    # Trending subforums
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(10)
    recent_tippers_post_count = recent_tippers_post.count()

    # POSTS sub queries
    # get posts by most exp
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.order_by(CommonsPost.comment_count.desc())

    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html',
                           now=now,

                           # forms
                           subform=subform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           thenotes=thenotes,
                           mainpostform=mainpostform,

                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           navlink=navlink,
                           themsgs=themsgs,

                           # queries/pagination
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,
                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           # prices
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@app.route('/tipped', methods=['GET'])
def coinposts():

    """
    Returns index page and hottest posts
    :return:
    """
    subform = SubscribeForm()
    voteform = VoteForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    navlink = 4

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)
    now = datetime.utcnow()

    if current_user.is_authenticated:
        # see if user leveled up and has a display to flash
        seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
        if seeiflevelup is not None:
            for levelup in seeiflevelup:
                flash("You have leveled up to level: " + str(levelup.new_user_leve), category='success')
                flash("Your have recieved 2 new coins", category='success')
                db.session.delete(levelup)
            db.session.commit()

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.filter(Notifications.read == 0)
        thenotes = thenotes.count()
    else:
        thenotes = 0

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.all()
        guestsubforums = None


        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()


    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None
        seeifmod = None
        moddingcount = None
        seeifowner = None
        ownercount = None

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None

    # Trending subforums
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(10)
    recent_tippers_post_count = recent_tippers_post.count()

    if current_user.is_authenticated:
        if current_user.over_age is False:
            post_18 = 0
            allpost = 0
        else:
            allpost = 0
            post_18 = 1
    else:
        post_18 = 0
        allpost = 0

    # owned business
    if current_user.is_authenticated:
        userbusiness = db.session.query(Business)
        userbusiness = userbusiness.filter(Business.user_id == current_user.id)
        userbusinesses = userbusiness.all()
        userbusinessescount = userbusiness.count()
    else:
        userbusinesses = None
        userbusinessescount = 0

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    # posts sub queries
    # get posts by most exp
    page = request.args.get('page', 1, type=int)

    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(or_(CommonsPost.total_recieved_btc_usd > 0, CommonsPost.total_recieved_promotion_btc_usd > 0))
    posts = posts.order_by(CommonsPost.total_recieved_promotion_btc_usd + CommonsPost.total_recieved_btc_usd,
                           CommonsPost.created.desc()
                           )

    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('coinposts', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('coinposts', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html',
                           now=now,
                           # forms
                           subform=subform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           thenotes=thenotes,
                           mainpostform=mainpostform,

                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           navlink=navlink,
                           themsgs=themsgs,

                           # queries/pagination
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,

                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@app.route('/top', methods=['GET'])
def top():

    """
    Returns index page and hottest posts
    :return:
    """
    subform = SubscribeForm()
    voteform = VoteForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    navlink = 5

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)
    now = datetime.utcnow()

    # Trending subforums
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(10)
    recent_tippers_post_count = recent_tippers_post.count()

    if current_user.is_authenticated:
        # see if user leveled up and has a display to flash
        seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
        if seeiflevelup is not None:
            for levelup in seeiflevelup:
                flash("You have leveled up to level: " + str(levelup.new_user_leve), category='success')
                flash("Your have recieved 2 new coins", category='Success')
                db.session.delete(levelup)
            db.session.commit()

    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.filter(Notifications.read == 0)
        thenotes = thenotes.count()
    else:
        thenotes = 0

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.all()
        guestsubforums = None

        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()


    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None
        seeifmod = None
        moddingcount = None
        seeifowner = None
        ownercount = None

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None

    if current_user.is_authenticated:
        if current_user.over_age is False:
            post_18 = 0
            allpost = 0
        else:
            allpost = 0
            post_18 = 1
    else:
        post_18 = 0
        allpost = 0

    # owned business
    if current_user.is_authenticated:
        userbusiness = db.session.query(Business)
        userbusiness = userbusiness.filter(Business.user_id == current_user.id)
        userbusinesses = userbusiness.all()
        userbusinessescount = userbusiness.count()
    else:
        userbusinesses = None
        userbusinessescount = 0

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    # POSTS sub queries
    # get posts by most exp
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.order_by(CommonsPost.highest_exp_reached.desc())

    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html',
                           now=now,
                           # forms
                           subform=subform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           mainpostform=mainpostform,
                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotes=thenotes,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           navlink=navlink,
                           themsgs=themsgs,

                           # queries/pagination
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,

                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


# this page is utilized if the user is banned from the sub, or
@app.route('/private/<string:subname>', methods=['GET'])
def private(subname):
    now = datetime.utcnow()
    applyform = ApplyToPrivate()

    # get subs user belongs too
    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.all()
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        guestsubforums = None
    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    getcurrentsub = db.session.query(SubForums)
    getcurrentsub = getcurrentsub.filter(SubForums.subcommon_name == subname)
    getcurrentsub = getcurrentsub.first_or_404()

    return render_template('subforums/private.html',
                           now=now,
                           applyform=applyform,
                           getcurrentsub=getcurrentsub,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           )


# this page is utilized if the user is banned from the sub, or
@app.route('/apply/private/<string:subname>', methods=['POST'])
@login_required
def apply_private(subname):
    now = datetime.utcnow()
    applyform = ApplyToPrivate()

    # get subs user belongs too
    if request.method == 'POST':
        getcurrentsub = db.session.query(SubForums)
        getcurrentsub = getcurrentsub.filter(SubForums.subcommon_name == subname)
        getcurrentsub = getcurrentsub.first_or_404()
        if applyform.validate_on_submit():

            addapplication = PrivateApplications(
                user_id=current_user.id,
                created=now,
                user_name=current_user.user_name,
                subcommon_id=getcurrentsub.id,
                message=applyform.reasonforapplying.data
            )
            db.session.add(addapplication)
            db.session.commit()
            flash("Successfully applied", category="success")
            return redirect(url_for('private', subname=subname))
        else:
            flash("Form Error. 500 characters max. No special characters", category="danger")
            return redirect(url_for('apply_private', subname=subname))


# this page is utilized if the user is banned from the sub
@app.route('/banned/<string:subname>', methods=['GET'])
def banned(subname):
    now = datetime.utcnow()
    getcurrentsub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()

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
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    return render_template('subforums/banned.html',
                           now=now,
                           getcurrentsub=getcurrentsub,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,

                           )


# this page is utilized if the user is under age
@app.route('/nsfw/<string:subname>', methods=['GET'])

def nsfw(subname):
    getcurrentsub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
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
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    return render_template('subforums/nsfw.html',
                           now=datetime.utcnow(),
                           getcurrentsub=getcurrentsub,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums
                           )


# this page is for finding new subs
@app.route('/discover', methods=['GET'])
@login_required
def discoversubs():
    now = datetime.utcnow()

    subform = SubscribeForm()

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_deleted == 0)
    usersubforums = usersubforums.filter(SubForums.room_suspended == 0)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0)
    usersubforums = usersubforums.all()

    # add user subs to a list so we dont refind them
    usersublist = []
    for usersub in usersubforums:
        usersublist.append(usersub.subcommon_id)

    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()
    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()
    themsgs = int(sendmsgs) + int(recmsgs)

    page = request.args.get('page', 1, type=int)

    popularsubs = db.session.query(SubForums)
    popularsubs = popularsubs.filter(SubForums.type_of_subcommon == 0)
    popularsubs = popularsubs.filter(SubForums.id != 1)
    popularsubs = popularsubs.filter(SubForums.id != 14)
    popularsubs = popularsubs.filter(SubForums.id.notin_(usersublist))
    popularsubs = popularsubs.filter(SubForums.room_deleted == 0)
    popularsubs = popularsubs.filter(SubForums.room_suspended == 0)
    popularsubs = popularsubs.filter(SubForums.room_banned == 0)
    popularsubs = popularsubs.order_by(SubForums.members.desc())
    popularsubs = popularsubs.paginate(page, 20, False)

    next_url = url_for('discoversubs', page=popularsubs.next_num) \
        if popularsubs.has_next else None
    prev_url = url_for('discoversubs', page=popularsubs.prev_num) \
        if popularsubs.has_prev else None

    return render_template('main/discover.html',
                           # forms
                           subform=subform,
                           # variables
                           now=now,
                           usersubforums=usersubforums,
                           themsgs=themsgs,
                           # pagination
                           popularsubs=popularsubs.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           )


# this page is for finding new subs
@app.route('/boss', methods=['GET'])
def bossofroom():
    now = datetime.utcnow()
    if request.method == "POST":
        pass

    if request.method == "GET":
        if current_user.is_authenticated:
            usersubforums = db.session.query(Subscribed)
            usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
            usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
            usersubforums = usersubforums.filter(SubForums.id != 1)
            usersubforums = usersubforums.filter(SubForums.room_deleted == 0)
            usersubforums = usersubforums.filter(SubForums.room_suspended == 0)
            usersubforums = usersubforums.filter(SubForums.room_banned == 0)
            usersubforums = usersubforums.all()
            guestsubforums = None
        else:
            guestsubforums = db.session.query(SubForums)
            guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
            guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
            guestsubforums = guestsubforums.filter(SubForums.room_suspended == 0)
            guestsubforums = guestsubforums.filter(SubForums.room_banned == 0)
            guestsubforums = guestsubforums.filter(SubForums.id != 1)
            guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
            guestsubforums = guestsubforums.limit(20)
            usersubforums = None

        if current_user.is_authenticated:
            recmsgs = db.session.query(Messages)
            recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
            recmsgs = recmsgs.count()

            sendmsgs = db.session.query(Messages)
            sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
            sendmsgs = sendmsgs.count()

            themsgs = int(sendmsgs) + int(recmsgs)
        else:
            themsgs = 0

        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()

        return render_template('main/boss.html',
                               now=now,
                               seeifowner=seeifowner,
                               ownercount=ownercount,
                               moddingcount=moddingcount,
                               seeifmod=seeifmod,
                               usersubforums=usersubforums,
                               guestsubforums=guestsubforums,
                               themsgs=themsgs,
                               )


# this page is for finding new subs
@app.route('/discover/business', methods=['GET'])
def discoverbiz():
    if request.method == "POST":
        pass

    if request.method == "GET":

        if current_user.is_authenticated:
            usersubforums = db.session.query(Subscribed)
            usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
            usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
            usersubforums = usersubforums.filter(SubForums.id != 1)
            usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
            usersubforums = usersubforums.filter(SubForums.room_suspended != 1)
            usersubforums = usersubforums.filter(SubForums.room_banned != 1)
            usersubforums = usersubforums.all()
            guestsubforums = None
        else:
            guestsubforums = db.session.query(SubForums)
            guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
            guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
            guestsubforums = guestsubforums.filter(SubForums.id != 1)
            guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
            guestsubforums = guestsubforums.limit(20)
            usersubforums = None

        if current_user.is_authenticated:
            recmsgs = db.session.query(Messages)
            recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
            recmsgs = recmsgs.count()

            sendmsgs = db.session.query(Messages)
            sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
            sendmsgs = sendmsgs.count()

            themsgs = int(sendmsgs) + int(recmsgs)
        else:
            themsgs = 0

        newsubs = db.session.query(Business)
        newsubs = newsubs.order_by(Business.created.desc())
        newsubs = newsubs.limit(10)

        popbiz = db.session.query(Business)
        popbiz = popbiz.join(BusinessStats, (Business.id == BusinessStats.business_id))
        popbiz = popbiz.order_by(BusinessStats.total_followers.desc())
        popbiz = popbiz.limit(10)

        seeifmodding = db.session.query(Mods)
        seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmodding.all()
        moddingcount = seeifmodding.count()

        seeifownering = db.session.query(SubForums)
        seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
        seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
        seeifowner = seeifownering.all()
        ownercount = seeifownering.count()

        return render_template('main/discoverbiz.html',
                               newsubs=newsubs,
                               popbiz=popbiz,
                               ownercount=ownercount,
                               seeifmod=seeifmod,
                               seeifowner=seeifowner,
                               moddingcount=moddingcount,
                               themsgs=themsgs,
                               usersubforums=usersubforums,
                               guestsubforums=guestsubforums
                               )


# this page is for finding new subs
@app.route('/subscriptions', methods=['GET'])
def mysubscriptions():
    now = datetime.utcnow()
    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_deleted == 0)
        usersubforums = usersubforums.filter(SubForums.room_suspended == 0)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0)
        usersubforums = usersubforums.all()
        guestsubforums = None
    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.room_deleted == 0)
        guestsubforums = guestsubforums.filter(SubForums.room_banned == 0)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    page = request.args.get('page', 1, type=int)
    getlistofmysubs = db.session.query(Subscribed)
    getlistofmysubs = getlistofmysubs.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    getlistofmysubs = getlistofmysubs.filter(current_user.id == Subscribed.user_id)
    getlistofmysubs = getlistofmysubs.filter(SubForums.room_banned == 0)
    getlistofmysubs = getlistofmysubs.filter(SubForums.room_deleted == 0)

    getlistofmysubs = getlistofmysubs.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('mysubscriptions', page=getlistofmysubs.next_num) \
        if getlistofmysubs.has_next else None
    prev_url = url_for('mysubscriptions', page=getlistofmysubs.prev_num) \
        if getlistofmysubs.has_prev else None

    return render_template('main/subscriptions.html',
                           now=now,
                           getlistofmysubs=getlistofmysubs.items,

                           # pagination
                           ownercount=ownercount,
                           seeifowner=seeifowner,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           next_url=next_url,
                           prev_url=prev_url,
                           themsgs=themsgs,

                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           )


# this page is for finding new subs
@app.route('/welcome', methods=['GET'])
@login_required
def welcome():

    user = User.query.filter_by(id=current_user.id).first()
    # subscribe users to basic subs

    seeifanysubs = db.session.query(Subscribed).filter(Subscribed.user_id == current_user.id,
                                                       Subscribed.subcommon_id == 1).first()
    if seeifanysubs is None:
        subto_wall = Subscribed(
            user_id=user.id,
            subcommon_id=1,
        )
        subto_general = Subscribed(
            user_id=user.id,
            subcommon_id=31,
        )
        subto_bitcoin = Subscribed(
            user_id=user.id,
            subcommon_id=3,
        )
        subto_announce = Subscribed(
            user_id=user.id,
            subcommon_id=4,
        )
        subto_help = Subscribed(
            user_id=user.id,
            subcommon_id=5,
        )
        subto_uspoltiics = Subscribed(
            user_id=user.id,
            subcommon_id=6,
        )
        subto_worldnews = Subscribed(
            user_id=user.id,
            subcommon_id=7,
        )
        subto_usnews = Subscribed(
            user_id=user.id,
            subcommon_id=2,
        )
        subto_bugs = Subscribed(
            user_id=user.id,
            subcommon_id=21,
        )
        # PAGES

        bizstats = BusinessStats.query.filter(BusinessStats.business_id == 4).first()

        # sub to tipvote business
        subtoit = BusinessFollowers(
            user_id=current_user.id,
            business_id=4,

        )
        # add new member to sub
        current_members = bizstats.total_followers
        addmembers = current_members + 1
        bizstats.total_followers = addmembers

        # add for commit

        db.session.add(bizstats)
        db.session.add(subto_general)
        db.session.add(subto_bugs)
        db.session.add(subtoit)
        db.session.add(subto_wall)
        db.session.add(subto_worldnews)
        db.session.add(subto_usnews)
        db.session.add(subto_uspoltiics)
        db.session.add(subto_bitcoin)
        db.session.add(subto_announce)
        db.session.add(subto_help)
        db.session.commit()

    # get user subforums
    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.all()

    # email stuff
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    confirm_account_url = url_for(
        'users.confirm_account_with_token',
        token=password_reset_serializer.dumps(user.email,
                                              salt='password-reset-salt'),
        _external=True)

    # account email
    accountreg = render_template('users/email/welcome.html',
                                 user=user.user_name,
                                 now=datetime.utcnow(),
                                 password_reset_url=confirm_account_url)
    try:
        send_email('Welcome to Tipvote!', [user.email], '', accountreg)
        # end email stuff
    except:
        pass

    return render_template('main/welcome.html',
                           now=datetime.utcnow(),
                           usersubforums=usersubforums
                           )


# this page is for finding new subs
@app.route('/markdown', methods=['GET'])
def markdownguide():

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    return render_template('main/markdown.html',
                           now=datetime.utcnow(),
                           themsgs=themsgs
                           )


# this page is for finding new subs
@app.route('/disclaimer', methods=['GET'])
def disclaimer():
    # get notifications

    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    return render_template('main/disclaimer.html',
                           now=datetime.utcnow(),
                           themsgs=themsgs
                           )


# this page is for finding new subs
@app.route('/statsguide', methods=['GET'])
def statsguide():
    # get notifications
    if current_user.is_authenticated:
        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)
    else:
        themsgs = 0

    return render_template('faq/stats_explained.html',
                           now=datetime.utcnow(),
                           themsgs=themsgs
                           )


@app.route('/bugbounty', methods=['GET'])
def bugbounty():
    if request.method == 'GET':
        # get notifications
        if current_user.is_authenticated:
            recmsgs = db.session.query(Messages)
            recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
            recmsgs = recmsgs.count()

            sendmsgs = db.session.query(Messages)
            sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
            sendmsgs = sendmsgs.count()

            themsgs = int(sendmsgs) + int(recmsgs)
        else:
            themsgs = 0

        return render_template('main/bugbounty.html',
                               now=datetime.utcnow(),
                               themsgs=themsgs
                               )


@app.route('/promote/all/learnmore', methods=['GET'])
def promote_all_learnmore():
    if request.method == 'GET':

        return render_template('promote/all/learnmore.html')

    if request.method == 'POST':
        pass


@app.route('/scoring', methods=['GET'])
def scoring():
    if request.method == 'GET':

        return render_template('main/scoring.html')

    if request.method == 'POST':
        pass


@app.route('/affiliate', methods=['GET'])
def affiliate():
    if request.method == 'GET':

        return render_template('main/affiliate.html')

    if request.method == 'POST':
        pass




@app.route('/updates', methods=['GET'])
def updates():
    # get sidebar list of updates
    all_updates = db.session.query(Updates).all()
    # get the latest update
    the_update = db.session.query(Updates)\
        .order_by(Updates.created.desc())\
        .first()

    if request.method == 'GET':

        return render_template('main/updates.html',
                               all_updates=all_updates,
                               the_update=the_update
                               )

    if request.method == 'POST':
        pass


@app.route('/update/<int:update_id>', methods=['GET'])
@login_required
def specific_update(update_id):
    # get sidebar list of updates
    all_updates = db.session.query(Updates).all()
    # get the specific update from update id
    the_update = db.session.query(Updates)\
        .filter(Updates.id == update_id)\
        .first()

    if request.method == 'GET':

        return render_template('main/updates.html',
                               all_updates=all_updates,
                               the_update=the_update
                               )

    if request.method == 'POST':
        pass


@app.route('/updateadd', methods=['GET'])
@login_required
def admin_add_update():
    form = CreateUpdateForm()

    if request.method == 'GET':
        # only admins can see page
        if current_user.admin == 0:
            return redirect(url_for('index'))

        # get sidebar list of updates
        all_updates = db.session.query(Updates).all()

        return render_template('main/addupdate.html',
                               form=form,
                               all_updates=all_updates,
                               )

    if request.method == 'POST':
        pass


@app.route('/update/post', methods=['POST'])
def admin_post_update():
    form = CreateUpdateForm()
    now = datetime.utcnow()
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        # only admins can see page
        if current_user.admin == 0:
            return redirect(url_for('index'))

        # add update
        newupdate = Updates(
            created=now,
            update_version=form.version.data,
            update_title=form.title.data,
            information=form.description.data,
            github_url=form.giturl.data,
        )
        db.session.add(newupdate)
        db.session.commit()

        flash("Added update", category='success')

        return redirect(url_for('specific_update', update_id=newupdate.id))