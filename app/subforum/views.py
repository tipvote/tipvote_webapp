# flask imports
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash,\
    jsonify
from flask import request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import func, select

from werkzeug.datastructures import CombinedMultiDict
# relative directory
from app import db, app
from app.common.decorators import login_required
from app.subforum import subforum
from sqlalchemy import or_
# forms
from app.create.forms import \
    CreateCommentForm, \
    MainPostForm, \
    CreateCommentQuickForm, RoomPostForm
from app.profile_edit.forms import \
    SaveForm
from app.vote.forms import VoteForm
from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute, \
    StickyPostForm, \
    UnStickyPostForm, \
    NSFWForm

from app.edit.forms import \
    EditPostTextForm, \
    EditCommentForm, \
    DeleteCommentTextForm, \
    DeletePostTextForm
from app.subforum.forms import \
    SubscribeForm, \
    ReportForm

# models
from app.classes.subforum import \
    Mods, \
    Banned, \
    SubForums, \
    PrivateMembers, \
    PrivateApplications, \
    SubForumCustom, \
    SubForumCustomInfoOne, \
    SubForumStats
from app.classes.bch import BchPrices
from app.classes.btc import BtcPrices
from app.classes.monero import MoneroPrices
from app.classes.post import CommonsPost
from app.classes.comments import Comments
from app.classes.business import Business, BusinessFollowers
from app.models import \
    ReportedPosts, \
    ReportedComments, \
    Notifications, \
    RecentTips, \
    LtcPrices

@subforum.route('/<string:subname>', methods=['GET'])
def sub(subname):

    # forms
    reportform = ReportForm()
    subform = SubscribeForm()
    voteform = VoteForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    nsfwform = NSFWForm()
    subpostcommentform = CreateCommentQuickForm()

    navlink = 1


    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thesub = db.session.query(SubForums)\
        .filter(func.lower(SubForums.subcommon_name) == subname.lower())\
        .first_or_404()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))

    if thesub.room_banned == 1:
        return redirect(url_for('subforum.sub_banned', subname=subname))
    if thesub.room_suspended == 1:
        return redirect(url_for('subforum.sub_suspended', subname=subname))
    if thesub.room_deleted == 1:
        return redirect(url_for('subforum.sub_deleted', subname=subname))
    # get the stats
    substats = db.session.query(SubForumStats)\
        .filter(SubForumStats.subcommon_name == subname.lower())\
        .first()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom)\
        .filter(SubForumCustom.subcommon_id == thesub.id)\
        .first()
    # get sub info box
    subinfobox = db.session.query(SubForumCustomInfoOne)\
        .filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname.lower())\
        .first()
    subtype = thesub.type_of_subcommon
    subname = thesub.subcommon_name
    subid = int(thesub.id)
    mods = db.session.query(Mods)\
        .filter(Mods.subcommon_id == subid)\
        .all()

    if subcustom_stuff is None:
        subcustom_setup = None
    else:
        subcustom_setup = 1

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

    # see if user banned
    if current_user.is_authenticated:
        seeifbanned = db.session.query(Banned)
        seeifbanned = seeifbanned.filter(current_user.id == Banned.user_id)
        seeifbanned = seeifbanned.filter(Banned.subcommon_id == subid)
        seeifbanned = seeifbanned.first()
        # if user on banned list turn him away
        if seeifbanned is not None:
            return redirect(url_for('banned', subname=subname))

    # see if current user is a mod
    if current_user.is_authenticated:
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0

    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

    # SIDEBAR
    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)

        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
        # get users saved subcommons
        saved_subcommons = db.session.query(Subscribed)\
            .filter(Subscribed.user_id == current_user.id)\
            .all()
        # get users created subcommons
        created_subcommons = db.session.query(SubForums)\
            .filter(SubForums.creator_user_id == current_user.id)\
            .all()
    else:
        # if user isnt subscribed to anything
        seeifsubbed = None
        saved_subcommons = None
        created_subcommons = None

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.order_by((SubForums.id == 31).desc(), SubForums.subcommon_name)
        usersubforums = usersubforums.all()
        guestsubforums = None
    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.room_banned == 0,
                                               SubForums.room_deleted == 0,
                                               SubForums.room_suspended == 0
                                               )
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

    # if sub is private and user is a mod/owner
    if useramod or userowner == 1:
        if subtype == 1:
            seeifanyapplications = db.session.query(PrivateApplications)
            seeifanyapplications = seeifanyapplications.filter(PrivateApplications.subcommon_id == subid)
            seeifanyapplications = seeifanyapplications.count()
        else:
            seeifanyapplications = 0

        reportedposts = db.session.query(ReportedPosts)
        reportedposts = reportedposts.filter(ReportedPosts.subcommon_name == subname)
        reportedposts = reportedposts.count()

        reportedcomments = db.session.query(ReportedComments)
        reportedcomments = reportedcomments.filter(ReportedComments.subcommon_name == subname)
        reportedcomments = reportedcomments.count()
    else:
        reportedposts = 0
        reportedcomments = 0
        seeifanyapplications = 0

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
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = \
            [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None


    # latest tips
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.filter(RecentTips.subcommon_id == subid)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(3)
    recent_tippers_post_count = recent_tippers_post.count()

    # Get Stickies
    stickypostfrommods = db.session.query(CommonsPost)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.subcommon_name == subname)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.sticky == 1)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.hidden == 0)
    stickypostfrommods = stickypostfrommods.limit(2)

    # see if user is over age
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

    # POST QUERIES
    page = request.args.get('page', 1, type=int)
    getpost = db.session.query(CommonsPost)
    getpost = getpost.filter(CommonsPost.subcommon_name == subname)
    getpost = getpost.filter(CommonsPost.hidden == 0)
    getpost = getpost.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    getpost = getpost.filter(CommonsPost.sticky == 0)
    getpost = getpost.order_by(CommonsPost.created.desc(),
                               CommonsPost.hotness_rating_now.desc(),
                               )

    posts = getpost.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('subforum.sub', subname=subname, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('subforum.sub', subname=subname, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('subforums/sub.html',
                           now=datetime.utcnow(),
                           mainpostform=mainpostform,
                           voteform=voteform,
                           nsfwform=nsfwform,
                           subname=subname,
                            subpostcommentform=subpostcommentform,
                           thenotescount=thenotescount,
                           subform=subform,
                           subinfobox=subinfobox,
                           subcustom_stuff=subcustom_stuff,
                           subcustom_setup=subcustom_setup,
                           stickypostfrommods=stickypostfrommods,
                           navlink=navlink,
                           reportform=reportform,
                           banuserdeleteform=banuserdeleteform,
                           thesub=thesub,
                           subid=subid,
                           substats=substats,
                           usersubforums=usersubforums,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           guestsubforums=guestsubforums,
                           thenotes=thenotes,
                           saved_subcommons=saved_subcommons,
                           created_subcommons=created_subcommons,
                           seeifsubbed=seeifsubbed,
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,
                           mods=mods,
                           useramod=useramod,
                           userowner=userowner,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           seeifanyapplications=seeifanyapplications,
                           reportedposts=reportedposts,
                           reportedcomments=reportedcomments,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@subforum.route('/<string:subname>/newest', methods=['GET'])
def sub_newest(subname):
    # forms
    reportform = ReportForm()
    subform = SubscribeForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    voteform = VoteForm()
    subpostcommentform = CreateCommentQuickForm()

    navlink = 2

    subname = subname.lower()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

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

    # get the sub
    thesub = db.session.query(SubForums)\
        .filter(func.lower(SubForums.subcommon_name) == subname)\
        .first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    # get the stats
    substats = db.session.query(SubForumStats)\
        .filter(func.lower(SubForumStats.subcommon_name) == subname)\
        .first_or_404()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom)\
        .filter(SubForumCustom.subcommon_id == thesub.id).first()

    subinfobox = db.session.query(SubForumCustomInfoOne)\
        .filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname)\
        .first()

    # get id of the sub
    subid = int(thesub.id)
    if subcustom_stuff is None:
        subcustom_setup = None
    else:
        subcustom_setup = 1

    # see if user banned
    if current_user.is_authenticated:
        seeifbanned = db.session.query(Banned)
        seeifbanned = seeifbanned.filter(current_user.id == Banned.user_id)
        seeifbanned = seeifbanned.filter(Banned.subcommon_id == subid)
        seeifbanned = seeifbanned.first()
        # if user on banned list turn him away
        if seeifbanned is not None:
            return redirect(url_for('banned', subname=subname))

    # get sub mods
    mods = db.session.query(Mods).filter(Mods.subcommon_id == subid).all()
    if current_user.is_authenticated:
        # see if current user is a mod
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0

    subtype = thesub.type_of_subcommon
    subname = thesub.subcommon_name
    # 0 = Public
    # 1 = private
    # 2 = censored

    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

    # if sub is private and user is a mod/owner
    if useramod or userowner == 1:
        if subtype == 1:
            seeifanyapplications = db.session.query(PrivateApplications)
            seeifanyapplications = seeifanyapplications.filter(PrivateApplications.subcommon_id == subid)
            seeifanyapplications = seeifanyapplications.count()
        else:
            seeifanyapplications = 0

        reportedposts = db.session.query(ReportedPosts)
        reportedposts = reportedposts.filter(ReportedPosts.subcommon_name == subname)
        reportedposts = reportedposts.count()

        reportedcomments = db.session.query(ReportedComments)
        reportedcomments = reportedcomments.filter(ReportedComments.subcommon_name == subname)
        reportedcomments = reportedcomments.count()
    else:
        reportedposts = 0
        reportedcomments = 0
        seeifanyapplications = 0

    # SIDEBAR
    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)

        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
        # get users saved subcommons
        saved_subcommons = db.session.query(Subscribed).filter(Subscribed.user_id == current_user.id).all()
        # get users created subcommons
        created_subcommons = db.session.query(SubForums).filter(SubForums.creator_user_id == current_user.id).all()
    else:
        # if user isnt subscribed to anything
        seeifsubbed = 0
        saved_subcommons = None
        created_subcommons = None

    if current_user.is_authenticated:
        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.order_by((SubForums.id == 31).desc(), SubForums.subcommon_name)
        usersubforums = usersubforums.all()
        guestsubforums = None
    else:
        guestsubforums = db.session.query(SubForums)
        guestsubforums = guestsubforums.filter(SubForums.age_required == 0)
        guestsubforums = guestsubforums.filter(SubForums.type_of_subcommon == 0)
        guestsubforums = guestsubforums.filter(SubForums.id != 1)
        guestsubforums = guestsubforums.filter(SubForums.room_banned == 0,
                                               SubForums.room_deleted == 0,
                                               SubForums.room_suspended == 0
                                               )
        guestsubforums = guestsubforums.order_by(SubForums.total_exp_subcommon.desc())
        guestsubforums = guestsubforums.limit(20)
        usersubforums = None

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
        mainpostform = MainPostForm(CombinedMultiDict((request.files, request.form)), )
        mainpostform.roomname.choices = \
            [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]
    else:
        mainpostform = None

    # latest tips
    recent_tippers_post = db.session.query(RecentTips)
    recent_tippers_post = recent_tippers_post.filter(RecentTips.subcommon_id == subid)
    recent_tippers_post = recent_tippers_post.order_by(RecentTips.created.desc())
    recent_tippers_post = recent_tippers_post.limit(3)
    recent_tippers_post_count = recent_tippers_post.count()

    # Get Stickies
    stickypostfrommods = db.session.query(CommonsPost)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.subcommon_name == subname)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.hidden == 0)
    stickypostfrommods = stickypostfrommods.filter(CommonsPost.sticky == 1)
    stickypostfrommods = stickypostfrommods.limit(2)

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

    # POST QUERIES
    page = request.args.get('page', 1, type=int)
    getpost = db.session.query(CommonsPost)
    getpost = getpost.filter(CommonsPost.subcommon_name == subname)
    getpost = getpost.filter(CommonsPost.hidden == 0)
    getpost = getpost.filter(or_(CommonsPost.age == post_18, CommonsPost.age == allpost))
    getpost = getpost.filter(CommonsPost.sticky == 0)
    getpost = getpost.order_by(CommonsPost.created.desc())

    posts = getpost.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('subforum.sub_newest', subname=subname, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('subforum.sub_newest', subname=subname, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('subforums/sub.html',
                           now=datetime.utcnow(),
                           mainpostform=mainpostform,
                           subname=subname,
                           subform=subform,
                           subpostcommentform=subpostcommentform,
                           voteform=voteform,

                           navlink=navlink,
                           thenotescount=thenotescount,
                           reportform=reportform,
                           banuserdeleteform=banuserdeleteform,
                           thesub=thesub,
                           userbusinesses=userbusinesses,
                           userbusinessescount=userbusinessescount,
                           bizfollowing=bizfollowing,
                           subcustom_stuff=subcustom_stuff,
                           thenotes=thenotes,
                           subinfobox=subinfobox,
                           subid=subid,
                           substats=substats,
                           usersubforums=usersubforums,
                           stickypostfrommods=stickypostfrommods,
                           saved_subcommons=saved_subcommons,
                           subcustom_setup=subcustom_setup,
                           created_subcommons=created_subcommons,
                           seeifsubbed=seeifsubbed,
                           guestsubforums=guestsubforums,
                           recent_tippers_post=recent_tippers_post,
                           recent_tippers_post_count=recent_tippers_post_count,
                           mods=mods,
                           useramod=useramod,
                           userowner=userowner,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           seeifanyapplications=seeifanyapplications,
                           reportedposts=reportedposts,
                           reportedcomments=reportedcomments,
                           # pagination
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


@subforum.route('/<string:subname>/customize', methods=['GET'])
@login_required
def subcustom(subname):
    subname = subname.lower()

    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    # get id of the sub
    subid = int(thesub.id)
    subname = thesub.subcommon_name

    # see if current user is a mod
    seeifmod = db.session.query(Mods)
    seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
    seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmod.first()
    if seeifmod is None:
        useramod = 0
    else:
        useramod = 1
    if current_user.id == thesub.creator_user_id:
        userowner = 1
    else:
        userowner = 0
    count = userowner + useramod
    if count == 0:
        flash("You are not allowed to customize this sub", category="success")
        return redirect(url_for('subforum.sub', subname=subname))

    # do the customization

    return render_template('subforums/sub.html',
                           now=datetime.utcnow(),
                           subname=subname,
                           )


@subforum.route('/<string:subname>/customize/banner', methods=['GET'])
@login_required
def subcustom_banner(subname):

    subname = subname.lower()
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    # get id of the sub
    subid = int(thesub.id)
    subname = thesub.subcommon_name

    # see if current user is a mod
    seeifmod = db.session.query(Mods)
    seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
    seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
    seeifmod = seeifmod.first()
    if seeifmod is None:
        useramod = 0
    else:
        useramod = 1
    if current_user.id == thesub.creator_user_id:
        userowner = 1
    else:
        userowner = 0
    count = userowner + useramod
    if count == 0:
        flash("You are not allowed to customize this sub", category="success")
        return redirect(url_for('subforum.sub', subname=subname))

    # do the customization

    return render_template('subforums/sub.html',
                           now=datetime.utcnow(),
                           subname=subname,

                           )


# SubScribe to a forum
@subforum.route('/suborunsub/<string:subname>', methods=['POST'])
def subunsubtoforum(subname):
    subform = SubscribeForm()
    # get the sub

    subname = subname.lower()
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))

    # get id of the sub
    subid = int(thesub.id)

    # subscribe to a sub
    if request.method == 'POST':
        if subform.validate_on_submit():
            # see if user subscribed
            if current_user.is_authenticated:
                # see if user already subbed

                if subform.subscribe.data is True:
                    seeifsubbed = db.session.query(Subscribed)\
                        .filter(Subscribed.user_id == current_user.id,
                                Subscribed.subcommon_id == subid)\
                        .first()

                    if seeifsubbed is None:
                        # add subscribition
                        subtoit = Subscribed(
                            user_id=current_user.id,
                            subcommon_id=subid,
                        )
                        # add new member to sub
                        current_members = thesub.members
                        addmembers = current_members + 1
                        thesub.members = addmembers

                        db.session.add(thesub)
                        db.session.add(subtoit)
                        db.session.commit()
                        flash("subscribed.", category="success")

                        return redirect(url_for('subforum.sub', subname=subname))

                    else:

                        flash("You are already subbed.", category="success")
                        return redirect(url_for('subforum.sub', subname=subname))
                elif subform.unsubscribe.data is True:
                    seeifmod = db.session.query(Mods)
                    seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
                    seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
                    seeifmod = seeifmod.first()
                    if seeifmod is None:
                        pass
                    else:
                        flash("Cannot unsubscribe from sub.  You are a sub", category="success")
                        return redirect(url_for('subforum.sub', subname=subname))

                    if current_user.id == thesub.creator_user_id:
                        flash("Cannot unsubscribe from sub.  You are a sub owner.", category="success")
                        return redirect(url_for('subforum.sub', subname=subname))
                    else:
                        pass

                    # get the sub query and delete it
                    unsubtoit = db.session.query(Subscribed)
                    unsubtoit = unsubtoit.filter(Subscribed.user_id == current_user.id,
                                                 Subscribed.subcommon_id == subid)
                    unsubtoit = unsubtoit.first()
                    # add new member to sub
                    current_members = thesub.members
                    addmembers = current_members - 1
                    thesub.members = addmembers
                    db.session.add(thesub)
                    db.session.delete(unsubtoit)
                    db.session.commit()
                    flash("unsubscribed.", category="danger")
                    return redirect(url_for('subforum.sub', subname=subname))
                else:

                    flash("No Selection", category="danger")
                    return redirect(url_for('subforum.sub', subname=subname))
            else:
                flash("User must be logged in", category='danger')
                return redirect(url_for('subforum.sub', subname=subname))
        else:
            flash("Form Error", category='danger')
            return redirect(url_for('subforum.sub', subname=subname))


@subforum.route('/sub/<string:subname>', methods=['POST'])
def sub_to_forum_no_redirect(subname):

    # get the sub
    subname = subname.lower()
    thesub = db.session.query(SubForums)\
        .filter(func.lower(SubForums.subcommon_name) == subname)\
        .first()
    if thesub is None:
        return jsonify({
            'result': 'This room does not exist.',
        })

    # get id of the sub
    subid = int(thesub.id)

    if request.method == 'POST':
        # see if user subscribed
        if current_user.is_authenticated:
            # UNsubscribe to a sub
            # see if user already subbed
            seeifsubbed = db.session.query(Subscribed)\
                .filter(Subscribed.user_id == current_user.id,
                        Subscribed.subcommon_id == subid)\
                .first()

            if seeifsubbed is None:
                # add subscribition
                subtoit = Subscribed(
                    user_id=current_user.id,
                    subcommon_id=subid,
                )
                # add new member to sub
                current_members = thesub.members
                addmembers = current_members + 1
                thesub.members = addmembers

                db.session.add(thesub)
                db.session.add(subtoit)
                db.session.commit()
                return jsonify({
                    'result': 'joined',
                    'thedivid': thesub.id,
                    'newnumber': addmembers
                })
            else:
                return jsonify({
                    'result': 'You Are already a member.',
                    'thedivid': thesub.id,
                })

        else:
            return jsonify({
                'result': 'Not Authorized'
            })



@subforum.route('/unsub/<string:subname>', methods=['POST'])
def unsub_to_forum_no_redirect(subname):
    subform = SubscribeForm()

    # get the sub
    subname = subname.lower()
    thesub = db.session.query(SubForums)\
        .filter(func.lower(SubForums.subcommon_name) == subname)\
        .first()
    if thesub is None:
        return jsonify({
            'result': 'This room does not exist.',
        })

    # get id of the sub
    subid = int(thesub.id)

    # subscribe to a sub
    if request.method == 'POST':
        if subform.validate_on_submit():
            # see if user subscribed
            if current_user.is_authenticated:
                # see if user already subbed
                if subform.unsubscribe.data is True:
                    seeifmod = db.session.query(Mods)
                    seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
                    seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
                    seeifmod = seeifmod.first()

                    if seeifmod is not None:
                        return jsonify({
                            'result': 'You are a Mod cannot unsubscribe.',
                            'thedivid': thesub.id,
                        })

                    if current_user.id == thesub.creator_user_id:
                        return jsonify({
                            'result': 'You are an owner cannot unsubscribe.',
                            'thedivid': thesub.id,
                        })

                    # get the sub query and delete it
                    unsubtoit = db.session.query(Subscribed)
                    unsubtoit = unsubtoit.filter(Subscribed.user_id == current_user.id,
                                                 Subscribed.subcommon_id == subid)
                    unsubtoit = unsubtoit.first()

                    # add new member to sub
                    current_members = thesub.members
                    addmembers = current_members - 1
                    thesub.members = addmembers

                    db.session.add(thesub)
                    db.session.delete(unsubtoit)
                    db.session.commit()

                    if current_user.id == thesub.creator_user_id:
                        return jsonify({
                            'result': 'Unjoined',
                            'thedivid': thesub.id,
                            'newnumber': addmembers
                        })
                else:
                    return jsonify({
                        'result': 'No Selection',
                        'thedivid': thesub.id,
                    })
            else:
                return jsonify({
                    'result': 'Not Authorized'
                })
        else:
            return jsonify({
                'result': 'Post Error'
            })


@subforum.route('/<string:subname>/banned', methods=['GET'])
def sub_banned(subname):

    return render_template('subforums/sub_banned.html',
                           # forms
                           subname=subname
                           )


@subforum.route('/<string:subname>/suspended', methods=['GET'])
def sub_suspended(subname):

    return render_template('subforums/sub_suspended.html',
                           # forms
                           subname=subname
                           )


@subforum.route('/<string:subname>/deleted', methods=['GET'])
def sub_deleted(subname):

    return render_template('subforums/sub_deleted.html',
                           # forms
                           subname=subname
                           )


# View / Reply to a post
@subforum.route('/<string:subname>/<int:postid>', methods=['GET'])
def viewpost(subname, postid):
    """
    View / Reply to a post
    """

    viewpost = 1

    form = CreateCommentForm()
    saveform = SaveForm()
    nsfwform = NSFWForm()
    subform = SubscribeForm()
    reportform = ReportForm()
    reportcommentform = ReportForm()
    editposttextform = EditPostTextForm()
    stickypostform = StickyPostForm()
    unstickypostform = UnStickyPostForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    deletecommenttextform = DeleteCommentTextForm()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname.lower()).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    post = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()

    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
    subinfobox = db.session.query(SubForumCustomInfoOne).filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname.lower()).first()

    # get id of the sub
    subid = int(thesub.id)
    subtype = thesub.type_of_subcommon
    active = 1

    editcommenttextform = EditCommentForm(request.form)

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
        # see if current user is a mod
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0

    # see if user is invited
    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

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

    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)
        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
    else:
        seeifsubbed = 0

    # add a new page view
    currentviews = post.page_views
    if currentviews is None:
        currentviews = 0

    newviews = currentviews + 1
    post.page_views = newviews

    db.session.add(post)
    db.session.commit()

    # link viewer

    # youtube
    urltext = post.url_of_post
    utube = 'www.youtube.com'

    if utube in urltext:
        link_youtube = True
    else:
        link_youtube = False

    # tips
    # tippers post
    top_tippers_post = db.session.query(RecentTips)
    top_tippers_post = top_tippers_post.filter(RecentTips.subcommon_id == subid)
    top_tippers_post = top_tippers_post.filter(RecentTips.post_id == post.id)
    top_tippers_post = top_tippers_post.filter(RecentTips.comment_id == 0)
    top_tippers_post = top_tippers_post.order_by(RecentTips.amount_usd.desc())
    top_tippers_post = top_tippers_post.limit(10)

    #  tippers comment
    top_tippers_comments = db.session.query(RecentTips)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.subcommon_id == subid)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.post_id == post.id)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.comment_id != 0)
    top_tippers_comments = top_tippers_comments.order_by(RecentTips.amount_usd.desc())
    top_tippers_comments = top_tippers_comments.limit(10)

    # main query
    comments = db.session.query(Comments)
    comments = comments.filter(Comments.commons_post_id == post.id)
    comments = comments.order_by(Comments.thread_upvotes.desc(), Comments.path.asc())
    comments = comments.all()

    return render_template('layout/viewpost.html',
                           now=datetime.utcnow(),
                           # forms
                           form=form,
                           saveform=saveform,
                           nsfwform=nsfwform,
                           viewpost=viewpost,
                           voteform=voteform,
                           reportform=reportform,
                           stickypostform=stickypostform,
                           unstickypostform=unstickypostform,
                           seeifsubbed=seeifsubbed,
                           reportcommentform=reportcommentform,
                           subform=subform,
                           usersubforums=usersubforums,
                           editposttextform=editposttextform,
                           editcommenttextform=editcommenttextform,
                           deleteposttextform=deleteposttextform,
                           deletecommenttextform=deletecommenttextform,
                           useramod=useramod,
                           userowner=userowner,
                           subname=subname,
                           thenotescount=thenotescount,
                           thesub=thesub,
                           subinfobox=subinfobox,
                           subcustom_stuff=subcustom_stuff,
                           comments=comments,
                           post=post,
                           active=active,
                           getcurrentsub=thesub,
                           guestsubforums=guestsubforums,
                           thenotes=thenotes,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           top_tippers_post=top_tippers_post,
                           top_tippers_comments=top_tippers_comments,

                           # links
                           link_youtube=link_youtube
                           )


# View / Reply to a post
# newest post threads
@subforum.route('/<string:subname>/<int:postid>/newest', methods=['GET'])
def viewpost_newest(subname, postid):
    """
    View / Reply to a post
    """
    viewpost = 1
    form = CreateCommentForm()
    subform = SubscribeForm()
    reportform = ReportForm()
    nsfwform = NSFWForm()
    reportcommentform = ReportForm()
    editposttextform = EditPostTextForm()
    stickypostform = StickyPostForm()
    unstickypostform = UnStickyPostForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    deletecommenttextform = DeleteCommentTextForm()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname.lower()).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))

    post = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
    subinfobox = db.session.query(SubForumCustomInfoOne).filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname.lower()).first()

    # get id of the sub
    subid = int(thesub.id)
    subtype = thesub.type_of_subcommon
    active = 2
    editcommenttextform = EditCommentForm(request.form)

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
        # see if current user is a mod
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0

    # see if user is invited
    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

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

    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)
        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
    else:
        seeifsubbed = 0

    # add a new page view
    currentviews = post.page_views
    if currentviews is None:
        currentviews = 0

    newviews = currentviews + 1
    post.page_views = newviews

    db.session.add(post)
    db.session.commit()

    # tips
    # tippers post
    top_tippers_post = db.session.query(RecentTips)
    top_tippers_post = top_tippers_post.filter(RecentTips.subcommon_id == subid)
    top_tippers_post = top_tippers_post.filter(RecentTips.post_id == post.id)
    top_tippers_post = top_tippers_post.filter(RecentTips.comment_id == 0)
    top_tippers_post = top_tippers_post.order_by(RecentTips.amount_usd.desc())
    top_tippers_post = top_tippers_post.limit(10)

    #  tippers comment
    top_tippers_comments = db.session.query(RecentTips)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.subcommon_id == subid)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.post_id == post.id)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.comment_id != 0)
    top_tippers_comments = top_tippers_comments.order_by(RecentTips.amount_usd.desc())
    top_tippers_comments = top_tippers_comments.limit(10)

    # main query
    comments = db.session.query(Comments)
    comments = comments.filter(Comments.commons_post_id == post.id)
    comments = comments.order_by(Comments.thread_timestamp.desc(), Comments.path.asc())
    comments = comments.all()

    return render_template('layout/viewpost.html',
                           now=datetime.utcnow(),
                           # forms
                           form=form,
                           voteform=voteform,
                           nsfwform=nsfwform,
                           reportform=reportform,
                           stickypostform=stickypostform,
                           unstickypostform=unstickypostform,
                           seeifsubbed=seeifsubbed,
                           reportcommentform=reportcommentform,
                           subform=subform,
                           usersubforums=usersubforums,
                           editposttextform=editposttextform,
                           editcommenttextform=editcommenttextform,
                           deleteposttextform=deleteposttextform,
                           deletecommenttextform=deletecommenttextform,
                           viewpost=viewpost,
                           guestsubforums=guestsubforums,
                           useramod=useramod,
                           userowner=userowner,
                           subname=subname,
                           thesub=thesub,
                           subinfobox=subinfobox,
                           thenotescount=thenotescount,
                           subcustom_stuff=subcustom_stuff,
                           comments=comments,
                           post=post,
                           active=active,
                           getcurrentsub=thesub,
                           thenotes=thenotes,
                           top_tippers_comments=top_tippers_comments,
                           top_tippers_post=top_tippers_post,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


# View / Reply to a post
# newest post threads
@subforum.route('/<string:subname>/<int:postid>/oldest', methods=['GET'])
def viewpost_oldest(subname, postid):
    """
    View / Reply to a post
    """
    viewpost = 1
    form = CreateCommentForm()

    subform = SubscribeForm()
    reportform = ReportForm()
    reportcommentform = ReportForm()
    nsfwform = NSFWForm()
    editposttextform = EditPostTextForm()
    stickypostform = StickyPostForm()
    unstickypostform = UnStickyPostForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    deletecommenttextform = DeleteCommentTextForm()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname.lower()).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    post = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
    subinfobox = db.session.query(SubForumCustomInfoOne).filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname.lower()).first()

    # get id of the sub
    subid = int(thesub.id)
    subtype = thesub.type_of_subcommon
    active = 3
    editcommenttextform = EditCommentForm(request.form)

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
        # see if current user is a mod
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0


    # see if user is invited
    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

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

    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)
        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
    else:
        seeifsubbed = 0

    # add a new page view
    currentviews = post.page_views
    if currentviews is None:
        currentviews = 0

    newviews = currentviews + 1
    post.page_views = newviews

    db.session.add(post)
    db.session.commit()

    # tips
    # tippers post
    top_tippers_post = db.session.query(RecentTips)
    top_tippers_post = top_tippers_post.filter(RecentTips.subcommon_id == subid)
    top_tippers_post = top_tippers_post.filter(RecentTips.post_id == post.id)
    top_tippers_post = top_tippers_post.filter(RecentTips.comment_id == 0)
    top_tippers_post = top_tippers_post.order_by(RecentTips.amount_usd.desc())
    top_tippers_post = top_tippers_post.limit(10)

    #  tippers comment
    top_tippers_comments = db.session.query(RecentTips)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.subcommon_id == subid)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.post_id == post.id)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.comment_id != 0)
    top_tippers_comments = top_tippers_comments.order_by(RecentTips.amount_usd.desc())
    top_tippers_comments = top_tippers_comments.limit(10)

    # main query
    comments = db.session.query(Comments)
    comments = comments.filter(Comments.commons_post_id == post.id)
    comments = comments.order_by(Comments.thread_timestamp.asc(), Comments.path.asc())
    comments = comments.all()

    return render_template('layout/viewpost.html',
                           now=datetime.utcnow(),
                           # forms
                           form=form,
                           reportform=reportform,
                           nsfwform=nsfwform,
                           stickypostform=stickypostform,
                           thenotescount=thenotescount,
                           unstickypostform=unstickypostform,
                           seeifsubbed=seeifsubbed,
                           reportcommentform=reportcommentform,
                           subform=subform,
                           usersubforums=usersubforums,
                           editposttextform=editposttextform,
                           editcommenttextform=editcommenttextform,
                           deleteposttextform=deleteposttextform,
                           deletecommenttextform=deletecommenttextform,
                           viewpost=viewpost,
                           useramod=useramod,
                           userowner=userowner,
                           subname=subname,
                           thesub=thesub,
                           subinfobox=subinfobox,
                           subcustom_stuff=subcustom_stuff,
                           guestsubforums=guestsubforums,
                           comments=comments,
                           voteform=voteform,
                           post=post,
                           active=active,
                           getcurrentsub=thesub,
                           thenotes=thenotes,
                           top_tippers_comments=top_tippers_comments,
                           top_tippers_post=top_tippers_post,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


# View / Reply to a post
# newest post threads
@subforum.route('/<string:subname>/<int:postid>/downvoted', methods=['GET'])
def viewpost_downvoted(subname, postid):
    """
    View / Reply to a post
    """
    viewpost = 1
    form = CreateCommentForm()

    subform = SubscribeForm()
    reportform = ReportForm()
    nsfwform = NSFWForm()
    reportcommentform = ReportForm()
    editposttextform = EditPostTextForm()
    stickypostform = StickyPostForm()
    unstickypostform = UnStickyPostForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    deletecommenttextform = DeleteCommentTextForm()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thesub = db.session.query(SubForums).filter(func.lower(SubForums.subcommon_name) == subname.lower()).first()
    if thesub is None:
        flash("Sub Doesnt Exist.", category="danger")
        return redirect(url_for('index'))
    post = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
    subinfobox = db.session.query(SubForumCustomInfoOne).filter(func.lower(SubForumCustomInfoOne.subcommon_name) == subname.lower()).first()

    # get id of the sub
    subid = int(thesub.id)
    subtype = thesub.type_of_subcommon
    active = 4
    editcommenttextform = EditCommentForm(request.form)

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
        # see if current user is a mod
        seeifmod = db.session.query(Mods)
        seeifmod = seeifmod.filter(Mods.subcommon_id == subid)
        seeifmod = seeifmod.filter(Mods.user_id == current_user.id)
        seeifmod = seeifmod.first()
        if seeifmod is None:
            useramod = 0
        else:
            useramod = 1
        if current_user.id == thesub.creator_user_id:
            userowner = 1
        else:
            userowner = 0
    else:
        useramod = 0
        userowner = 0

    # see if user is invited
    if subtype == 1:
        if useramod or userowner == 1:
            pass
        else:
            if current_user.is_authenticated:
                seeifuserinvited = db.session.query(PrivateMembers)
                seeifuserinvited = seeifuserinvited.filter(current_user.id == PrivateMembers.user_id)
                seeifuserinvited = seeifuserinvited.filter(PrivateMembers.subcommon_id == subid)
                seeifuserinvited = seeifuserinvited.first()
                if seeifuserinvited is None:
                    return redirect(url_for('private', subname=subname))
            else:
                return redirect(url_for('private', subname=subname))

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

    if current_user.is_authenticated:
        # see if user is subscribed
        seeifsubbed = db.session.query(Subscribed)
        seeifsubbed = seeifsubbed.filter(current_user.id == Subscribed.user_id)
        seeifsubbed = seeifsubbed.filter(Subscribed.subcommon_id == subid)
        seeifsubbed = seeifsubbed.first()
        if seeifsubbed is None:
            seeifsubbed = 0
        else:
            seeifsubbed = 1
    else:
        seeifsubbed = 0

    # add a new page view
    currentviews = post.page_views
    if currentviews is None:
        currentviews = 0

    newviews = currentviews + 1
    post.page_views = newviews

    db.session.add(post)
    db.session.commit()

    # tips
    # tippers post
    top_tippers_post = db.session.query(RecentTips)
    top_tippers_post = top_tippers_post.filter(RecentTips.subcommon_id == subid)
    top_tippers_post = top_tippers_post.filter(RecentTips.post_id == post.id)
    top_tippers_post = top_tippers_post.filter(RecentTips.comment_id == 0)
    top_tippers_post = top_tippers_post.order_by(RecentTips.amount_usd.desc())
    top_tippers_post = top_tippers_post.limit(10)

    #  tippers comment
    top_tippers_comments = db.session.query(RecentTips)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.subcommon_id == subid)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.post_id == post.id)
    top_tippers_comments = top_tippers_comments.filter(RecentTips.comment_id != 0)
    top_tippers_comments = top_tippers_comments.order_by(RecentTips.amount_usd.desc())
    top_tippers_comments = top_tippers_comments.limit(10)

    # main query
    comments = db.session.query(Comments)
    comments = comments.filter(Comments.commons_post_id == post.id)
    comments = comments.order_by(Comments.thread_downvotes.desc(), Comments.path.asc())
    comments = comments.all()

    return render_template('layout/viewpost.html',
                           now=datetime.utcnow(),
                           # forms
                           form=form,
                           voteform=voteform,
                           reportform=reportform,
                           nsfwform=nsfwform,
                           thenotescount=thenotescount,
                           stickypostform=stickypostform,
                           unstickypostform=unstickypostform,
                           seeifsubbed=seeifsubbed,
                           reportcommentform=reportcommentform,
                           subform=subform,
                           usersubforums=usersubforums,
                           editposttextform=editposttextform,
                           editcommenttextform=editcommenttextform,
                           deleteposttextform=deleteposttextform,
                           deletecommenttextform=deletecommenttextform,
                           useramod=useramod,
                           userowner=userowner,
                           subname=subname,
                           thesub=thesub,
                           viewpost=viewpost,
                           subinfobox=subinfobox,
                           subcustom_stuff=subcustom_stuff,
                           guestsubforums=guestsubforums,
                           comments=comments,
                           post=post,
                           active=active,
                           getcurrentsub=thesub,
                           thenotes=thenotes,
                           top_tippers_comments=top_tippers_comments,
                           top_tippers_post=top_tippers_post,
                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )

