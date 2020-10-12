from flask import \
    render_template, \
    request, \
    url_for, \
    flash
from flask_login import current_user
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from app.common.decorators import login_required
from werkzeug.datastructures import CombinedMultiDict
from app import db, app
from app.frontpage import frontpage
from app.create.forms import MainPostForm
from app.vote.forms import VoteForm
from app.subforum.forms import SubscribeForm

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute

from app.models import \
    BtcPostTips, \
    RecentTips, \
    DisplayCoins, \
    Notifications, \
    BtcPrices, \
    MoneroPrices, \
    BchPrices, \
    LtcPrices, \
    Subscribed, \
    SubForums, \
    CommonsPost, \
    Business, \
    BusinessFollowers, \
    Messages, \
    Mods


@frontpage.route('', methods=['GET'])
@login_required
def frontpage_home():

    """
    Returns index page and most exp posts
    :return:
    """
    subform = SubscribeForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()

    subid = 0
    navlink = 1

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    thenotes = db.session.query(Notifications)
    thenotes = thenotes.filter(Notifications.user_id == current_user.id)
    thenotes = thenotes.filter(Notifications.read == 0)
    thenotes = thenotes.count()

    # see if user leveled up and has a display to flash
    seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
    if seeiflevelup is not None:
        for levelup in seeiflevelup:
            flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
            flash("Your have recieved 2 new coins", category='success')
            db.session.delete(levelup)
        db.session.commit()

    # stats for sidebar
    # all time top tippers for posts
    top_tippers_alltime_post_btc = db.session.query(BtcPostTips) \
        .order_by(BtcPostTips.amount_usd.desc()) \
        .limit(3)

    # top tippers this week
    seven_days_ago = datetime.today() - timedelta(days=7)
    top_tippers_pastweek_post_btc = db.session.query(BtcPostTips) \
        .filter(BtcPostTips.created >= seven_days_ago) \
        .order_by(BtcPostTips.amount_usd.desc()) \
        .limit(3)

    # Most Recent Tippers
    recent_tippers_post = db.session.query(RecentTips) \
        .order_by(RecentTips.created.desc()) \
        .limit(3)
    # Trending subforums
    trending = db.session.query(SubForums) \
        .order_by(SubForums.total_exp_subcommon.desc()) \
        .limit(10)

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.all()

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    if current_user.is_authenticated:
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = [(str(row.subscriber.id),
                                          str(row.subscriber.subcommon_name)) for row in usersubforums]
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

    # business following
    if current_user.is_authenticated:
        bizfollowing = db.session.query(BusinessFollowers)
        bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
        bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

        bizfollowing = bizfollowing.all()
    else:
        bizfollowing = None

    # list of subs user belongs too
    usersublist = []
    for usersub in usersubforums:
        usersublist.append(usersub.subcommon_id)

    # query latest rooms
    new_rooms = db.session.query(SubForums) \
        .filter(SubForums.id.notin_(usersublist),
                SubForums.room_deleted == 0,
                SubForums.room_suspended == 0,
                SubForums.room_banned == 0,
                SubForums.id != 1,
                SubForums.id != 14
                ) \
        .order_by(SubForums.created.desc()).limit(6)

    # query random rooms
    random_rooms = db.session.query(SubForums).filter(
        SubForums.id.notin_(usersublist),
        SubForums.room_deleted == 0,
        SubForums.room_suspended == 0,
        SubForums.room_banned == 0,
        SubForums.id != 1,
        SubForums.id != 14
    ) \
        .order_by(func.random()) \
        .limit(6)

    page = request.args.get('page', 1, type=int)
    # POSTS sub queries where user is subbed to list
    # get posts by most exp
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.subcommon_id.in_(usersublist))
    posts = posts.filter(CommonsPost.subcommon_id != 1)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.order_by(CommonsPost.hotness_rating_now.desc(), CommonsPost.created.desc())
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('frontpage.frontpage_home', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('frontpage.frontpage_home', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('frontpage.html',
                           now=datetime.utcnow(),
                           # forms
                           subform=subform,
                           voteform=voteform,
                           mainpostform=mainpostform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           # general
                           new_rooms=new_rooms,
                           random_rooms=random_rooms,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           subid=subid,
                           themsgs=themsgs,
                           navlink=navlink,
                           usersubforums=usersubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,

                           # queries/pagination
                           trending=trending,
                           thenotes=thenotes,
                           # stats
                           top_tippers_alltime_post_btc=top_tippers_alltime_post_btc,
                           top_tippers_pastweek_post_btc=top_tippers_pastweek_post_btc,
                           recent_tippers_post=recent_tippers_post,
                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@frontpage.route('/newest', methods=['GET'])
@login_required
def frontpage_newest():

    """
    Returns index page and newest posts
    :return:
    """
    subform = SubscribeForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()


    subid = 0
    navlink = 2

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # see if user leveled up and has a display to flash
    seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
    if seeiflevelup is not None:
        for levelup in seeiflevelup:
            flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
            flash("Your have recieved 2 new coins", category='success')
            db.session.delete(levelup)
        db.session.commit()

    # Trending subforums
    trending = db.session.query(SubForums).order_by(SubForums.total_exp_subcommon.desc()).limit(10)

    thenotes = db.session.query(Notifications)
    thenotes = thenotes.filter(Notifications.user_id == current_user.id)
    thenotes = thenotes.filter(Notifications.read == 0)
    thenotes = thenotes.count()



    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)


    # get subs user belongs too and add to list

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.all()

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
    mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]

    if current_user.over_age is False:
        post_18 = 0
        allpost = 0
    else:
        allpost = 0
        post_18 = 1

    userbusiness = db.session.query(Business)
    userbusiness = userbusiness.filter(Business.user_id == current_user.id)
    userbusinesses = userbusiness.all()
    userbusinessescount = userbusiness.count()

    bizfollowing = db.session.query(BusinessFollowers)
    bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
    bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

    bizfollowing = bizfollowing.all()

    # list of subs user belongs too
    usersublist = []
    for usersub in usersubforums:
        usersublist.append(usersub.subcommon_id)

    # query latest rooms
    new_rooms = db.session.query(SubForums) \
        .filter(SubForums.id.notin_(usersublist),
                SubForums.room_deleted == 0,
                SubForums.room_suspended == 0,
                SubForums.room_banned == 0,
                SubForums.id != 1,
                SubForums.id != 14
                ) \
        .order_by(SubForums.created.desc()).limit(6)

    # query random rooms
    random_rooms = db.session.query(SubForums).filter(
        SubForums.id.notin_(usersublist),
        SubForums.room_deleted == 0,
        SubForums.room_suspended == 0,
        SubForums.room_banned == 0,
        SubForums.id != 1,
        SubForums.id != 14
    ) \
        .order_by(func.random()) \
        .limit(6)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.subcommon_id.in_(usersublist))
    posts = posts.filter(CommonsPost.subcommon_id != 1)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.order_by(CommonsPost.created.desc())
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('frontpage.frontpage_newest', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('frontpage.frontpage_newest', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('frontpage.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           # form
                           subform=subform,
                           new_rooms=new_rooms,
                           random_rooms=random_rooms,
                           voteform=voteform,
                           themsgs=themsgs,
                           mainpostform=mainpostform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           # general
                           thenotes=thenotes,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           subid=subid,
                           navlink=navlink,
                           usersubforums=usersubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,

                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@frontpage.route('/active', methods=['GET'])
@login_required
def frontpage_mostactive():

    """
    Returns index page and most voted/commented posts
    :return:
    """
    subform = SubscribeForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()

    subid = 0
    navlink = 3

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # see if user leveled up and has a display to flash
    seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
    if seeiflevelup is not None:
        for levelup in seeiflevelup:
            flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
            flash("Your have recieved 2 new coins", category='success')
            db.session.delete(levelup)
        db.session.commit()

    # Trending subforums
    trending = db.session.query(SubForums).order_by(SubForums.total_exp_subcommon.desc()).limit(10)

    thenotes = db.session.query(Notifications)
    thenotes = thenotes.filter(Notifications.user_id == current_user.id)
    thenotes = thenotes.filter(Notifications.read == 0)
    thenotes = thenotes.count()

    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)


    # get subs user belongs too and add to list
    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.all()

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
    mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in
                                     usersubforums]

    if current_user.over_age is False:
        post_18 = 0
        allpost = 0
    else:
        allpost = 0
        post_18 = 1

    userbusiness = db.session.query(Business)
    userbusiness = userbusiness.filter(Business.user_id == current_user.id)
    userbusinesses = userbusiness.all()
    userbusinessescount = userbusiness.count()

    bizfollowing = db.session.query(BusinessFollowers)
    bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
    bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

    bizfollowing = bizfollowing.all()

    # list of subs user belongs too
    usersublist = []
    for usersub in usersubforums:
        usersublist.append(usersub.subcommon_id)

    # query latest rooms
    new_rooms = db.session.query(SubForums) \
        .filter(SubForums.id.notin_(usersublist),
                SubForums.room_deleted == 0,
                SubForums.room_suspended == 0,
                SubForums.room_banned == 0,
                SubForums.id != 1,
                SubForums.id != 14
                ) \
        .order_by(SubForums.created.desc()).limit(6)

    # query random rooms
    random_rooms = db.session.query(SubForums).filter(
        SubForums.id.notin_(usersublist),
        SubForums.room_deleted == 0,
        SubForums.room_suspended == 0,
        SubForums.room_banned == 0,
        SubForums.id != 1,
        SubForums.id != 14
    ) \
        .order_by(func.random()) \
        .limit(6)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.subcommon_id.in_(usersublist))
    posts = posts.filter(CommonsPost.subcommon_id != 1)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.order_by(CommonsPost.comment_count.desc(), CommonsPost.created.desc())
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('frontpage.frontpage_mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('frontpage.frontpage_mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('frontpage.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,

                           # forms
                           mainpostform=mainpostform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           subform=subform,

                           # general
                           new_rooms=new_rooms,
                           random_rooms=random_rooms,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotes=thenotes,
                           subid=subid,
                           themsgs=themsgs,
                           navlink=navlink,
                           usersubforums=usersubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,

                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )



@frontpage.route('/top', methods=['GET'])
@login_required
def frontpage_top():

    """
    Returns index page and most voted/commented posts
    :return:
    """
    subform = SubscribeForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()

    subid = 0
    navlink = 5

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # see if user leveled up and has a display to flash
    seeiflevelup = db.session.query(DisplayCoins).filter(DisplayCoins.user_id == current_user.id).all()
    if seeiflevelup is not None:
        for levelup in seeiflevelup:
            flash("You have leveled up to level: " + str(levelup.new_user_level), category='success')
            flash("Your have recieved 2 new coins", category='success')
            db.session.delete(levelup)
        db.session.commit()

    # Trending subforums
    trending = db.session.query(SubForums).order_by(SubForums.total_exp_subcommon.desc()).limit(10)

    thenotes = db.session.query(Notifications)
    thenotes = thenotes.filter(Notifications.user_id == current_user.id)
    thenotes = thenotes.filter(Notifications.read == 0)
    thenotes = thenotes.count()

    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)


    # get subs user belongs too and add to list

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.all()

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
    mainpostform.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in
                                     usersubforums]

    if current_user.over_age is False:
        post_18 = 0
        allpost = 0
    else:
        allpost = 0
        post_18 = 1

    userbusiness = db.session.query(Business)
    userbusiness = userbusiness.filter(Business.user_id == current_user.id)
    userbusinesses = userbusiness.all()
    userbusinessescount = userbusiness.count()

    bizfollowing = db.session.query(BusinessFollowers)
    bizfollowing = bizfollowing.join(Business, (BusinessFollowers.business_id == Business.id))
    bizfollowing = bizfollowing.filter(current_user.id == BusinessFollowers.user_id)

    bizfollowing = bizfollowing.all()

    # list of subs user belongs too
    usersublist = []
    for usersub in usersubforums:
        usersublist.append(usersub.subcommon_id)

    # query latest rooms
    new_rooms = db.session.query(SubForums) \
        .filter(SubForums.id.notin_(usersublist),
                SubForums.room_deleted == 0,
                SubForums.room_suspended == 0,
                SubForums.room_banned == 0,
                SubForums.id != 1,
                SubForums.id != 14
                ) \
        .order_by(SubForums.created.desc()).limit(6)

    # query random rooms
    random_rooms = db.session.query(SubForums).filter(
        SubForums.id.notin_(usersublist),
        SubForums.room_deleted == 0,
        SubForums.room_suspended == 0,
        SubForums.room_banned == 0,
        SubForums.id != 1,
        SubForums.id != 14
    ) \
        .order_by(func.random()) \
        .limit(6)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.subcommon_id.in_(usersublist))
    posts = posts.filter(CommonsPost.subcommon_id != 1)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.order_by(CommonsPost.highest_exp_reached.desc())
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('frontpage.frontpage_mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('frontpage.frontpage_mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('frontpage.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,

                           # forms
                           mainpostform=mainpostform,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           subform=subform,
                           themsgs=themsgs,
                           usersubforums=usersubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,

                           # general
                           new_rooms=new_rooms,
                           random_rooms=random_rooms,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotes=thenotes,
                           subid=subid,
                           navlink=navlink,

                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )
