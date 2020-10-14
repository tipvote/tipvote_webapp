from flask import \
    render_template, \
    request, \
    url_for, \
    flash, redirect
from flask_login import current_user
from werkzeug.datastructures import CombinedMultiDict
from datetime import datetime, timedelta
from app.common.decorators import login_required
from app import db, app
from app.followers import followers
from sqlalchemy import or_
from app.vote.forms import VoteForm
from app.subforum.forms import SubscribeForm
from app.create.forms import MainPostForm
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
    CommonsPost,\
    Followers,\
    Messages,\
    Mods

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute

POSTS_PER_PAGE = 25


@followers.route('', methods=['GET'])
@login_required
def followers_home():

    """
    Returns index page and most exp posts
    :return:
    """

    subform = SubscribeForm()
    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
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

    try:
        # get unread messages
        if current_user.is_authenticated:
            thenotes = db.session.query(Notifications)
            thenotes = thenotes.filter(Notifications.user_id == current_user.id)
            thenotes = thenotes.order_by(Notifications.timestamp.desc())
            thenotescount = thenotes.filter(Notifications.read == 0)
            thenotescount = thenotescount.count()
            thenotes = thenotes.limit(10)
        else:
            thenotes = 0
            thenotescount = 0


        recmsgs = db.session.query(Messages)
        recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
        recmsgs = recmsgs.count()

        sendmsgs = db.session.query(Messages)
        sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
        sendmsgs = sendmsgs.count()

        themsgs = int(sendmsgs) + int(recmsgs)


        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
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

        # list of friends ids
        usersublist = []
        usersubfriends = Followers.query.filter(Followers.follower_id == current_user.id).all()
        for userfriend in usersubfriends:
            usersublist.append(userfriend.followed_id)

        # POSTS sub queries where user is subbed to list
        # get posts by most exp
        page = request.args.get('page', 1, type=int)
        posts = db.session.query(CommonsPost)
        posts = posts.filter(CommonsPost.hidden == 0)
        posts = posts.filter(CommonsPost.user_id.in_(usersublist))
        posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
        posts = posts.order_by(CommonsPost.hotness_rating_now.desc(), CommonsPost.created.desc())
        posts = posts.paginate(page, POSTS_PER_PAGE, False)

        next_url = url_for('followers.followers_home', page=posts.next_num) \
            if posts.has_next else None
        prev_url = url_for('followers.followers_home', page=posts.prev_num) \
            if posts.has_prev else None
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

    return render_template('followers.html',
                           now=datetime.utcnow(),
                           # forms
                           subform=subform,
                           voteform=voteform,
                           wall_post_form=wall_post_form,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotescount=thenotescount,
                           subid=subid,
                           navlink=navlink,
                           themsgs=themsgs,

                           usersubforums=usersubforums,
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


@followers.route('/newest', methods=['GET'])
@login_required
def followers_newest():

    """
    Returns index page and newest posts
    :return:
    """
    subform = SubscribeForm()
    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
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


    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(10)
    else:
        thenotes = 0
        thenotescount = 0


    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()

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

    # list of friends ids
    usersublist = []
    usersubfriends = Followers.query.filter(Followers.follower_id == current_user.id).all()
    for userfriend in usersubfriends:
        usersublist.append(userfriend.followed_id)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.user_id.in_(usersublist))
    posts = posts.order_by(CommonsPost.created.desc())
    posts = posts.paginate(page,POSTS_PER_PAGE, False)

    next_url = url_for('followers.followers_newest', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('followers.followers_newest', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('followers.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           # form
                           wall_post_form=wall_post_form,
                           voteform=voteform,
                           subform=subform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           # general
                            thenotescount=thenotescount,

                           thenotes=thenotes,
                           themsgs=themsgs,
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           subid=subid,
                           navlink=navlink,
                           usersubforums=usersubforums,

                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@followers.route('/active', methods=['GET'])
@login_required
def followers_mostactive():

    """
    Returns index page and most voted/commented posts
    :return:
    """
    subform = SubscribeForm()

    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
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

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(10)
    else:
        thenotes = 0
        thenotescount = 0

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()

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

    # list of friends ids
    usersublist = []
    usersubfriends = Followers.query.filter(Followers.follower_id == current_user.id).all()
    for userfriend in usersubfriends:
        usersublist.append(userfriend.followed_id)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.user_id.in_(usersublist))
    posts = posts.order_by(CommonsPost.comment_count.desc(), CommonsPost.created.desc())
    posts = posts.paginate(page, POSTS_PER_PAGE, False)

    next_url = url_for('followers.followers_mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('followers.followers_mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('followers.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,

                           # forms
                           thenotescount=thenotescount,
                           subform=subform,

                           voteform=voteform,
                           wall_post_form=wall_post_form,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,

                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotes=thenotes,
                           themsgs=themsgs,
                           subid=subid,
                           navlink=navlink,
                           usersubforums=usersubforums,
                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@followers.route('/tipped', methods=['GET'])
@login_required
def followers_coinposts():

    """
    Returns index page and donation posts
    :return:
    """
    subform = SubscribeForm()

    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()

    subid = 0
    navlink = 4

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

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()


    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(10)
    else:
        thenotes = 0
        thenotescount = 0


    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    if current_user.over_age is False:
        post_18 = 0
        allpost = 0
    else:
        allpost = 0
        post_18 = 1

    # list of friends ids
    usersublist = []
    usersubfriends = Followers.query.filter(Followers.follower_id == current_user.id).all()
    for userfriend in usersubfriends:
        usersublist.append(userfriend.followed_id)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.user_id.in_(usersublist))
    posts = posts.order_by(CommonsPost.total_recieved_promotion_btc_usd + CommonsPost.total_recieved_btc_usd,
                           CommonsPost.created.desc())
    posts = posts.paginate(page, POSTS_PER_PAGE, False)

    next_url = url_for('followers.followers_coinposts', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('followers.followers_coinposts', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('followers.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,

                           # forms
                           thenotes=thenotes,
                           thenotescount=thenotescount,
                           wall_post_form=wall_post_form,
                           voteform=voteform,
                           subform=subform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,

                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           subid=subid,
                           navlink=navlink,
                           themsgs=themsgs,
                           usersubforums=usersubforums,
                           trending=trending,

                           # queries/pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@followers.route('/top', methods=['GET'])
@login_required
def followers_top():

    """
    Returns index page and most voted/commented posts
    :return:
    """
    subform = SubscribeForm()

    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
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

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(10)
    else:
        thenotes = 0
        thenotescount = 0

    recmsgs = db.session.query(Messages)
    recmsgs = recmsgs.filter(Messages.rec_user_id == current_user.id, Messages.read_rec == 1)
    recmsgs = recmsgs.count()

    sendmsgs = db.session.query(Messages)
    sendmsgs = sendmsgs.filter(Messages.sender_user_id == current_user.id, Messages.read_send == 1)
    sendmsgs = sendmsgs.count()

    themsgs = int(sendmsgs) + int(recmsgs)

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == current_user.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()

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

    # list of friends ids
    usersublist = []
    usersubfriends = Followers.query.filter(Followers.follower_id == current_user.id).all()
    for userfriend in usersubfriends:
        usersublist.append(userfriend.followed_id)

    # POSTS sub queries
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(CommonsPost)
    posts = posts.filter(CommonsPost.hidden == 0)
    posts = posts.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    posts = posts.filter(CommonsPost.user_id.in_(usersublist))
    posts = posts.order_by(CommonsPost.highest_exp_reached.desc())
    posts = posts.paginate(page, POSTS_PER_PAGE, False)

    next_url = url_for('followers.followers_mostactive', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('followers.followers_mostactive', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('followers.html',
                           now=datetime.utcnow(),
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           # forms
                           subform=subform,

                           wall_post_form=wall_post_form,
                           voteform=voteform,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,

                           # general
                           seeifmod=seeifmod,
                           moddingcount=moddingcount,
                           seeifowner=seeifowner,
                           ownercount=ownercount,
                           thenotes=thenotes,
                           thenotescount=thenotescount,
                           subid=subid,
                           themsgs=themsgs,
                           navlink=navlink,
                           usersubforums=usersubforums,
                           # queries/pagination
                           trending=trending,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )