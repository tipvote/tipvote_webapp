# flask imports
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash
from flask import request
from flask_login import current_user
from werkzeug.utils import secure_filename

from datetime import datetime
import os
from app.create.create_id import id_generator
from sqlalchemy import func
from app.create.get_image_resize import convertimage
from app.create.get_image_fromurl import getimage

# common imports
from app import db
from app import UPLOADED_FILES_DEST
from app.vote.forms import VoteForm
from app.nodelocations import postnodelocation, current_disk
from app.common.decorators import login_required
from app.common.timers import lastcommoncreation, lastposted, lastcommont
from app.common.functions import mkdir_p, id_generator_picture1
from app.common.lvl_required import lvl_req
from app.common.exp_calc import exppoint
from app.message.add_notification import add_new_notification

# relative directory
from app.create import create

from app.create.forms import \
    CreateSubcommonForm, \
    CreateCommentForm, \
    MainPostForm, \
    RoomPostForm, \
    CreateShareTextForm, \
    CreateBusinessForm, \
    BusinessPostForm

from app.models import \
    Subscribed, \
    SubForums, \
    CommonsPost, \
    SubForumStats, \
    PrivateMembers, \
    Comments, \
    SubForumCustom, \
    UserStats, \
    UserTimers, \
    Banned, \
    Muted, \
    BtcPrices, \
    MoneroPrices, \
    BchPrices, \
    LtcPrices, \
    User, \
    Business, \
    BusinessInfo, \
    BusinessStats, \
    BusinessLocation, \
    BusinessServices, \
    BlockedUser


from app.create.geturlinfo import geturl
from app.create.convert_markdown import transform_image_links_markdown


@create.route('/createsub', methods=['GET', 'POST'])
@login_required
def createsubforum():
    """
    Creates a subcommon
    """
    form = CreateSubcommonForm()
    now = datetime.utcnow()

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()

    # get how many subs user owns
    usersubcount = db.session.query(SubForums)
    usersubcount = usersubcount.filter(SubForums.creator_user_id == current_user.id)
    usersubcount = usersubcount.filter(SubForums.id != 1)
    usersubcount = usersubcount.filter(SubForums.room_banned == 0,
                                       SubForums.room_deleted == 0,
                                       SubForums.room_suspended == 0
                                       )
    usersubcount = usersubcount.count()

    roomsowned = db.session.query(SubForums)
    roomsowned = roomsowned.filter(SubForums.creator_user_id == current_user.id)
    roomsowned = roomsowned.filter(SubForums.id != 1)
    roomsowned = roomsowned.filter(SubForums.room_banned == 0,
                                   SubForums.room_deleted == 0,
                                   SubForums.room_suspended == 0
                                   )
    roomsowned = roomsowned.all()

    userstats = UserStats.query.filter(UserStats.user_id == current_user.id).first()
    userlevel = userstats.user_level

    # redirect for security incase bypass button
    if userlevel == 1:
        flash("You need to be level 2 in order to create a room.  "
              "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
        return redirect(url_for('index'))

    # determine how many subs a user can have and show them
    if 2 <= userlevel <= 9:
        maxsubcount = 1 - usersubcount
    elif 10 <= userlevel <= 19:
        maxsubcount = 5 - usersubcount
    elif 20 <= userlevel <= 29:
        maxsubcount = 10 - usersubcount
    elif 30 <= userlevel <= 39:
        maxsubcount = 15 - usersubcount
    else:
        maxsubcount = 15 - usersubcount

    if request.method == 'GET':

        return render_template('create/subforum/create_subforum.html',
                               form=form,
                               maxsubcount=maxsubcount,
                               roomsowned=roomsowned,
                               usersubforums=usersubforums,
                               currentbtcprice=currentbtcprice,
                               currentxmrprice=currentxmrprice,
                               currentbchprice=currentbchprice,
                               currentltcprice=currentltcprice,
                               )

    if request.method == 'POST':

        # security for timer
        seeiftimerallowed, timeleft = lastcommoncreation(user_id=current_user.id)
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " minutes before creating another Room", category="info")
            return redirect((request.args.get('next', request.referrer)))

        # security for level
        if 2 <= userlevel <= 9:
            if usersubcount >= 1:
                flash("You need to be level 10 in order to create more rooms.  "
                      "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
                return redirect(url_for('index'))

        elif 10 <= userlevel <= 19:
            if usersubcount >= 3:
                flash("You need to be level 20 in order to create more rooms.  "
                      "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
                return redirect(url_for('index'))
        elif 20 <= userlevel <= 29:
            if usersubcount >= 5:
                flash("You need to be level 30 in order to create more rooms.  "
                      "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
                return redirect(url_for('index'))
        elif 30 <= userlevel <= 39:
            if usersubcount >= 10:
                flash("You are at max level of rooms.  "
                      "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
                return redirect(url_for('index'))
        else:
            if usersubcount >= 10:
                flash("You are at max level of rooms.  "
                      "This is to prevent bots, spammers, and oversaturation of rooms.", category="danger")
                return redirect(url_for('index'))

        if form.validate_on_submit():
            try:
                name_of_subcommon = form.subcommonname.data

                description_of_subcommon = form.subcommondescription.data
                exp_req = 0
                subtype = form.typeofsub.data

                if subtype == '0':
                    subtype = 0
                elif subtype == '1':
                    subtype = 1
                elif subtype == '2':
                    subtype = 2
                elif subtype == '3':
                    subtype = 3
                else:
                    subtype = 10

                agereq = form.age.data
                if agereq is False:
                    theage = 0
                else:
                    theage = 1

                # create subcommon
                newcommon = SubForums(subcommon_name=str(name_of_subcommon),
                                      creator_user_id=current_user.id,
                                      creator_user_name=current_user.user_name,
                                      created=now,
                                      description=str(description_of_subcommon),
                                      type_of_subcommon=subtype,
                                      exp_required=int(exp_req),
                                      age_required=theage,
                                      allow_text_posts=1,
                                      allow_url_posts=1,
                                      allow_image_posts=1,
                                      total_exp_subcommon=0,
                                      members=1,
                                      mini_image='',
                                      room_banned=0,
                                      room_suspended=0,
                                      room_deleted=0,
                                      )

                db.session.add(newcommon)
                db.session.commit()
                # create Sub Stats
                substats = SubForumStats(
                    subcommon_name=str(name_of_subcommon),
                    subcommon_id=newcommon.id,
                    total_posts=0,
                    total_exp_subcommon=0,
                    members=1,
                )

                # sub customization ie banner
                newsubcustom = SubForumCustom(
                    subcommon_name=str(name_of_subcommon),
                    subcommon_id=newcommon.id,
                    banner_image='',
                    mini_image='',
                )

                # subscribe user to that forum
                newsubscription = Subscribed(user_id=current_user.id,
                                             subcommon_id=newcommon.id,
                                             )

                # reset users timer
                getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
                getuser_timers.last_common_creation = now

                # add exp points
                exppoint(user_id=current_user.id, category=7)
                db.session.add(newsubcustom)
                db.session.add(substats)
                db.session.add(getuser_timers)
                db.session.add(newsubscription)
                db.session.commit()
                flash("Room created.", category="success")
                flash("Welcome to your room.  You are the boss of this room. "
                      " You can add a banner, mini-image, and manage your sub now."
                      "  Try adding a post to make your sub more interesting.", category="success")
                return redirect(url_for('subforum.sub', subname=newcommon.subcommon_name))
            except Exception as e:

                flash("Room Creation Failure.", category="success")
                return redirect(url_for('create.createsubforum'))
        else:
            for errors in form.subcommonname.errors:
                flash(errors, category="danger")
            for errors in form.subcommondescription.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@create.route('/createbusiness', methods=['GET', 'POST'])
@login_required
def createbusinesspage():
    """
    Creates a business page
    """
    form = CreateBusinessForm()
    now = datetime.utcnow()

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.all()

    form.type_of_business.choices = [
        ('0', 'Local Business'),
        ('1', 'Company, Organization, or Institution'),
        ('2', 'Brand or Product'),
        ('3', 'Crypto Trader'),
    ]
    # security
    lvlneeded = lvl_req(userid=current_user.id, lvlnumber=2)
    if lvlneeded is False:
        flash("You need to be level 2 in order to create a business page.  "
              "This is to prevent bots, spammers from taking over the site.",
              category="success")
        return redirect(url_for('index'))

    if request.method == 'GET':

        return render_template('create/business/business_start.html',
                               form=form,
                               usersubforums=usersubforums,
                               currentbtcprice=currentbtcprice,
                               currentxmrprice=currentxmrprice,
                               currentbchprice=currentbchprice,
                               currentltcprice=currentltcprice,
                               )

    if request.method == 'POST':

        # TIMERS
        seeiftimerallowed, timeleft = lastcommoncreation(user_id=current_user.id)
        # if there is enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " minutes before creating another Page", category="info")
            return redirect((request.args.get('next', request.referrer)))

        if form.validate_on_submit():
            try:
                name_of_business = form.business_name.data
                type_of_business_response = form.type_of_business.data

                if type_of_business_response == '0':
                    subtype = 0
                    thetag = 'Local Business or Place'
                elif type_of_business_response == '1':
                    subtype = 1
                    thetag = 'Company, Organization, or Institution'
                elif type_of_business_response == '2':
                    subtype = 2
                    thetag = 'Brand or Product'
                elif type_of_business_response == '3':
                    subtype = 3
                    thetag = 'Crypto Trader'
                else:
                    subtype = 0
                    thetag = 'Local Business'

                agereq = form.age.data
                if agereq is False:
                    theage = 0
                else:
                    theage = 1

                # create subcommon
                new_biz = Business(
                    user_name=current_user.user_name,
                    user_id=current_user.id,
                    business_name=name_of_business,
                    business_tag=thetag,
                    business_id=subtype,
                    age=theage,
                    created=now,
                    profileimage='',
                    bannerimage='',
                    official_business_name=''
                )

                db.session.add(new_biz)
                db.session.commit()

                # create Sub Stats
                biz_stats = BusinessStats(
                    business_id=new_biz.id,
                    total_upvotes=0,
                    total_downvotes=0,
                    total_followers=0,
                    total_reviews=0,
                    page_views=0,
                )

                # sub customization ie banner
                biz_info = BusinessInfo(
                    business_id=new_biz.id,
                    phone_number='',
                    email='',
                    about='',
                    website='',
                    facebook='',
                    twitter='',
                )
                # sub customization ie banner
                biz_services = BusinessServices(
                    business_id=new_biz.id,
                    one_enabled=0,
                    info_one='',
                    two_enabled=0,
                    info_two='',
                )
                # sub customization ie banner
                biz_location = BusinessLocation(
                    business_id=new_biz.id,
                    address='',
                    town='',
                    state_or_province='',
                    country='',
                    zipcode='',
                )

                # reset users timer
                getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
                getuser_timers.last_common_creation = now

                # add exp points
                exppoint(user_id=current_user.id, category=7)

                db.session.add(biz_stats)
                db.session.add(biz_info)
                db.session.add(biz_services)
                db.session.add(biz_location)
                db.session.commit()

                flash("Business Page created.", category="success")
                flash("Welcome to your Page.  You are the boss! "
                      " You can add a banner, mini-image, and manage your sub now."
                      "  Try adding a post to make your sub more interesting.", category="success")
                return redirect(url_for('business.main', business_name=name_of_business))
            except:
                flash("Page Creation Failure.", category="success")
                return redirect(url_for('create.createbusinesspage'))
        else:
            for errors in form.business_name.errors:
                flash(errors, category="danger")
            for errors in form.type_of_business.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


# View / Reply to a post
@create.route('/comment/create/<string:subname>/<int:postid>/<int:parentid>', methods=['POST'])
@login_required
def createcomment(subname, postid, parentid):
    """
    View / Reply to a post
    """

    if request.method == 'POST':

        now = datetime.utcnow()
        form = CreateCommentForm()

        # # TIMERS
        # seeiftimerallowed, timeleft = lastcommont(user_id=current_user.id)
        # # if there is enough time
        # if seeiftimerallowed == 0:
        #     flash("Please wait " + str(timeleft) + " minutes before creating another comment.", category="info")
        #     return redirect((request.args.get('next', request.referrer)))

        thepost = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()

        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == thepost.user_id,
                                                 BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash("Your Comment can not be added.", category="danger")
            return redirect(url_for('index'))
        if thepost is None:
            flash("Post doesnt exist or has been removed", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        if thepost.hidden == 1:
            flash("Post has been removed", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        if thepost.locked == 1:
            flash("Post has been locked", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        getcurrentsub = db.session.query(SubForums) \
            .filter(SubForums.subcommon_name == subname) \
            .first_or_404()
        if getcurrentsub is None:
            return redirect((request.args.get('next', request.referrer)))

        if parentid is 0:
            getsubcomment = None
            figured_thread_timestamp = datetime.utcnow()
            figured_thread_upvotes = 0
            figured_thread_downvotes = 0
        else:
            getsubcomment = db.session.query(Comments) \
                .filter(Comments.id == parentid) \
                .first()

            figured_thread_timestamp = getsubcomment.thread_timestamp
            figured_thread_upvotes = getsubcomment.thread_upvotes
            figured_thread_downvotes = getsubcomment.thread_downvotes

        subid = getcurrentsub.id
        subtype = getcurrentsub.type_of_subcommon

        if form.validate_on_submit():
            if current_user.is_authenticated:

                # see if banned
                seeifbanned = db.session.query(Banned)
                seeifbanned = seeifbanned.filter(current_user.id == Banned.user_id,
                                                 Banned.subcommon_id == subid)
                seeifbanned = seeifbanned.first()
                # if user on banned list turn him away
                if seeifbanned is not None:
                    flash("You were banned from this sub.", category="success")
                    return redirect(url_for('banned', subname=subname))
                # see if muted
                seeifusermuted = db.session.query(Muted)
                seeifusermuted = seeifusermuted.filter(Muted.user_id == current_user.id)
                seeifusermuted = seeifusermuted.filter(Muted.subcommon_id == subid)
                seeifusermuted = seeifusermuted.first()
                if seeifusermuted is not None:
                    flash("You were muted for 24 hours.", category="danger")
                    return redirect(url_for('subforum.sub', subname=subname))

                # see if private
                if subtype == 1:
                    seeifuserinvited = db.session.query(PrivateMembers) \
                        .filter(current_user.id == PrivateMembers.user_id, PrivateMembers.subcommon_id == subid) \
                        .first()
                    if seeifuserinvited is None:
                        flash("Sub Is a private Community.", category="success")
                        return redirect(url_for('private', subname=subname))

                posttxt = form.postmessage.data

                if current_user.anon_mode == 0:
                    visible_user_id = current_user.id
                    visible_user_name = current_user.user_name
                    userhidden = 0
                else:
                    visible_user_id = 0
                    visible_user_name = "Anonymous"
                    userhidden = 1

                uniqueid = id_generator(size=15)

                # finds the last comment relating to a post
                latest_index_id_post = db.session.query(Comments) \
                    .filter(Comments.commons_post_id == thepost.id) \
                    .order_by(Comments.id.desc()) \
                    .first()

                # check to see if its first comment
                if latest_index_id_post is None:
                    # if first comment id is 0
                    new_index_id = 0
                else:
                    if latest_index_id_post.index_id is None:
                        # if replying to an old comment below id#1641
                        comment_count_on_post = db.session.query(Comments) \
                            .filter(Comments.commons_post_id == thepost.id) \
                            .order_by(Comments.id.desc()) \
                            .count()

                        new_index_id = comment_count_on_post
                    else:
                        latest_index_id = latest_index_id_post.index_id
                        new_index_id = latest_index_id + 1

                create_new_comment = Comments(
                    index_id=new_index_id,
                    user_id=current_user.id,
                    user_name=current_user.user_name,
                    subcommon_id=thepost.subcommon_id,
                    commons_post_id=thepost.id,
                    realid=uniqueid,
                    body=posttxt,
                    created=now,
                    total_exp_commons=0,
                    downvotes_on_comment=0,
                    upvotes_on_comment=0,
                    total_recieved_btc=0,
                    total_recieved_xmr=0,
                    total_recieved_bch=0,
                    total_recieved_btc_usd=0,
                    total_recieved_xmr_usd=0,
                    total_recieved_bch_usd=0,
                    visible_user_id=visible_user_id,
                    visible_user_name=visible_user_name,
                    userhidden=userhidden,
                    parent=getsubcomment,
                    hidden=0,
                    active=1,
                    thread_timestamp=figured_thread_timestamp,
                    thread_upvotes=figured_thread_upvotes,
                    thread_downvotes=figured_thread_downvotes,
                    deleted=0,

                )
                create_new_comment.save()

                # add exp points
                exppoint(user_id=current_user.id, category=2)

                # add comment count to the post
                currentcommentcount = thepost.comment_count
                newcount = currentcommentcount + 1
                thepost.comment_count = newcount

                if current_user.anon_mode == 0:
                    # add comment count to the user stats
                    getuser_stats = db.session.query(UserStats).filter_by(user_id=current_user.id).first()
                    current_user_comments = getuser_stats.total_comments
                    getuser_stats.total_comments = current_user_comments + 1
                    db.session.add(getuser_stats)

                # reset users timer
                getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
                getuser_timers.last_comment = now

                # update post to active
                thepost.last_active = now
                thepost.active = 1

                # if the commenter doesnt equal the poster
                if thepost.user_id != current_user.id:
                    # add notification for poster about new comment
                    add_new_notification(user_id=thepost.user_id,
                                         subid=subid,
                                         subname=subname,
                                         postid=thepost.id,
                                         commentid=0,
                                         msg=1,
                                         )
                if parentid is not 0:
                    add_new_notification(user_id=getsubcomment.user_id,
                                         subid=subid,
                                         subname=subname,
                                         postid=thepost.id,
                                         commentid=0,
                                         msg=1,
                                         )

                # add to db
                db.session.add(thepost)
                db.session.add(getuser_timers)
                db.session.commit()

                comment_start_path = create_new_comment.path[:5]



                flash("Comment Added.", category="success")
                return redirect(url_for('subforum.viewpost',
                                        subname=thepost.subcommon_name,
                                        postid=thepost.id))

            else:
                flash("User must be logged in", category='danger')
                return redirect((request.args.get('next', request.referrer)))
        else:
            for errors in form.postmessage.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


def notify_commenters(subid, subname, thepost, commentpathstart):
    # need to loop through the path splitting at . find the comment id.  Then add a notification.
    list_user_ids = []

    getsubcomments = db.session.query(Comments)\
        .filter(Comments.commons_post_id == thepost.id)\
        .all()

    for f in getsubcomments:
        if f.path[:5] == commentpathstart:
            flash(f.path[:5])
            flash(commentpathstart)
            if f.user_id not in list_user_ids:
                if f.user_id != thepost.user_id:
                    if f.user_id != current_user.id:
                        list_user_ids.append(f.user_id)

    for g in list_user_ids:
        add_new_notification(user_id=g,
                             subid=subid,
                             subname=subname,
                             postid=thepost.id,
                             commentid=0,
                             msg=30,
                             )
    db.session.commit()


@create.route('/share/text/<int:postid>/', methods=['GET', 'POST'])
@login_required
def share_post_text(postid):

    form = CreateShareTextForm()
    voteform = VoteForm()
    now = datetime.utcnow()
    uniqueid = id_generator(size=15)

    user_stats = db.session.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    post = CommonsPost.query.filter(CommonsPost.id == postid).first()

    currentbtcprice = BtcPrices.query.get(1)
    currentxmrprice = MoneroPrices.query.get(1)
    currentbchprice = BchPrices.query.get(1)
    currentltcprice = LtcPrices.query.get(1)

    if request.method == 'GET':

        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == post.user_id,
                                                 BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash("Your Post can not be added.", category="danger")
            return redirect(url_for('index'))

        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                             SubForums.room_deleted == 0,
                                             SubForums.room_suspended == 0
                                             )
        usersubforums = usersubforums.all()

        return render_template('create/posts/share/share_text.html',
                               form=form,
                               post=post,
                               voteform=voteform,
                               usersubforums=usersubforums,
                               currentbtcprice=currentbtcprice,
                               currentxmrprice=currentxmrprice,
                               currentbchprice=currentbchprice,
                               currentltcprice=currentltcprice,
                               )

    elif request.method == 'POST':
        # Timer
        seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # if there is enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
            return redirect((request.args.get('next', request.referrer)))
        if form.validate_on_submit():
            if current_user.is_authenticated:
                if post.shared_post == 0:
                    sharedthoughtstext = post.post_text
                    sharedid = post.id
                else:
                    sharedthoughtstext = post.shared_thoughts
                    sharedid = post.shared_post

                if current_user.anon_mode == 1:
                    p_user_hidden = 1
                    p_user_name = 'anonymous'
                    p_user_id = 0
                else:
                    p_user_hidden = 0
                    p_user_name = current_user.user_name
                    p_user_id = current_user.id

                newpostnumber = user_stats.total_posts + 1

                user_stats.total_posts = newpostnumber

                newpost = CommonsPost(

                    # creator
                    user_id=current_user.id,
                    user_name=current_user.user_name,
                    visible_user_id=current_user.id,
                    visible_user_name=current_user.user_name,
                    userhidden=0,
                    poster_user_name=current_user.user_name,
                    poster_user_id=current_user.id,
                    poster_visible_user_id=p_user_id,
                    poster_visible_user_name=p_user_name,
                    poster_userhidden=p_user_hidden,
                    creator_anon=post.creator_anon,
                    content_user_name=post.content_user_name,
                    content_user_id=post.content_user_id,
                    realid=uniqueid,
                    subcommon_id=1,
                    subcommon_name='wall',
                    type_of_post=post.type_of_post,
                    url_of_post=post.url_of_post,
                    url_description=post.url_description,
                    url_image=post.url_image,
                    url_title=post.url_title,
                    url_image_server=post.url_image_server,
                    image_server_1=post.image_server_1,
                    total_exp_commons=0,
                    highest_exp_reached=0,
                    downvotes_on_post=0,
                    upvotes_on_post=0,
                    comment_count=0,
                    vote_timestamp=now,
                    last_active=now,
                    hotness_rating_now=0,
                    page_views=0,
                    sticky=0,
                    active=1,
                    locked=0,
                    hidden=0,
                    muted=0,
                    crawlneed=0,
                    created=now,
                    edited=now,
                    post_text=form.postmessage.data,
                    decay_rate='1',
                    shared_post=sharedid,
                    shared_time=post.created,
                    shared_thoughts=sharedthoughtstext,
                    age=post.age,
                    business_id=post.business_id
                )

                # commit
                db.session.add(user_stats)
                db.session.add(newpost)

                db.session.commit()

                flash("Shared!", category="success")
                return redirect(url_for('profile.main', user_name=current_user.user_name))
            else:
                flash("User not authenticated.", category="danger")
                return redirect((request.args.get('next', request.referrer)))

        else:
            flash("Post Creation Failure.", category="danger")
            for errors in form.postmessage.errors:
                flash(errors, category="danger")

            return redirect((request.args.get('next', request.referrer)))
    else:
        flash("Post Creation Failure.", category="danger")
        return redirect((request.args.get('next', request.referrer)))


@create.route('/share/quick/<int:postid>', methods=['GET', 'POST'])
@login_required
def share_post(postid):

    if request.method == 'POST':
        flash("Your Post can not be added.", category="danger")
        return redirect(url_for('index'))

    if request.method == 'GET':
        try:
            now = datetime.utcnow()
            uniqueid = id_generator(size=15)
            # TIMERS
            seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
            # if there is enough time
            if seeiftimerallowed == 0:
                flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
                return redirect((request.args.get('next', request.referrer)))

            post = CommonsPost.query.filter(CommonsPost.id == postid).first()

            user_stats = db.session.query(UserStats).filter(UserStats.user_id == current_user.id).first()
            # see if blocked
            isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == post.user_id,
                                                     BlockedUser.blocked_user == current_user.id).first()
            if isuserblocked:
                flash("Your Post can not be added.", category="danger")
                return redirect(url_for('index'))
            if post.shared_post == 0:
                sharedthoughtstext = post.post_text
                sharedid = post.id
            else:
                sharedthoughtstext = post.shared_thoughts
                sharedid = post.shared_post

            if current_user.anon_mode == 1:
                p_user_hidden = 1
                p_user_name = 'anonymous'
                p_user_id = 0
            else:
                p_user_hidden = 0
                p_user_name = current_user.user_name
                p_user_id = current_user.id

            newpostnumber = user_stats.total_posts + 1

            newpost = CommonsPost(
                user_id=current_user.id,
                user_name=current_user.user_name,
                visible_user_id=current_user.id,
                visible_user_name=current_user.user_name,
                userhidden=0,
                poster_user_name=current_user.user_name,
                poster_user_id=current_user.id,
                poster_visible_user_id=p_user_id,
                poster_visible_user_name=p_user_name,
                poster_userhidden=p_user_hidden,
                creator_anon=post.creator_anon,
                content_user_name=post.content_user_name,
                content_user_id=post.content_user_id,
                created=now,
                edited=now,
                realid=uniqueid,
                subcommon_id=1,
                subcommon_name='wall',
                type_of_post=post.type_of_post,
                post_text='',
                url_of_post=post.url_of_post,
                url_description=post.url_description,
                url_image=post.url_image,
                url_title=post.url_title,
                url_image_server=post.url_image_server,
                image_server_1=post.image_server_1,
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,
                decay_rate='1',
                shared_post=sharedid,
                shared_time=post.created,
                shared_thoughts=sharedthoughtstext,
                age=post.age,
                business_id=post.business_id
            )
            user_stats.total_posts = newpostnumber

            # commit
            db.session.add(user_stats)

            db.session.add(newpost)
            db.session.commit()

            flash("Shared!", category="success")
            return redirect(url_for('profile.main', user_name=current_user.user_name))
        except Exception as e:
            flash(str(e))
            return redirect((request.args.get('next', request.referrer)))


@create.route('/wallpost/<int:userid>', methods=['POST'])
@login_required
def create_post_wall(userid):

    now = datetime.utcnow()
    id_pic1 = id_generator_picture1()
    wall_post_form = RoomPostForm()
    uniqueid = id_generator(size=15)

    chosen_subcommon_id = 1
    chosen_subcommon_name = 'wall'

    if request.method == 'POST':
        theuser = User.query.filter(User.id == userid).first()

        # # TIMERS
        # seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # # if there is enough time
        # if seeiftimerallowed == 0:
        #     flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
        #     return redirect((request.args.get('next', request.referrer)))

        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == theuser.id,
                                                 BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash("Your Post can not be added.", category="danger")
            return redirect(url_for('index'))


        if wall_post_form.validate_on_submit():

            getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
            user_stats = db.session.query(UserStats).filter(UserStats.user_id == current_user.id).first()

            # see if user posted comment
            if wall_post_form.post_message.data == '':
                score_1 = 0
            else:
                score_1 = 1
            if wall_post_form.image_one.data:
                score_2 = 1
            else:
                score_2 = 0
            total_score = score_1 + score_2
            if total_score == 0:
                flash("You need to post some content", category="success")
                return redirect((request.args.get('next', request.referrer)))

            agereq = wall_post_form.age.data
            if agereq is True:
                post_age = 1
            else:
                post_age = 0

            if current_user.anon_mode == 1:
                p_user_hidden = 1
                p_user_name = 'anonymous'
                p_user_id = 0
            else:
                p_user_hidden = 0
                p_user_name = current_user.user_name
                p_user_id = current_user.id

            newpostnumber = user_stats.total_posts + 1

            urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(wall_post_form.post_message.data)
            transformed_text = transform_image_links_markdown(wall_post_form.post_message.data)

            # add post to db
            newpost = CommonsPost(

                user_id=theuser.id,
                user_name=theuser.user_name,
                visible_user_id=theuser.id,
                visible_user_name=theuser.user_name,
                userhidden=0,


                poster_user_name=current_user.user_name,
                poster_user_id=current_user.id,
                poster_visible_user_id=p_user_id,
                poster_visible_user_name=p_user_name,
                poster_userhidden=p_user_hidden,

                content_user_name=current_user.user_name,
                content_user_id=current_user.id,

                # location
                realid=uniqueid,
                subcommon_id=chosen_subcommon_id,
                subcommon_name=chosen_subcommon_name,
                type_of_post=0,

                # text
                post_text=transformed_text,

                # url
                url_of_post=urlfound,
                url_description=urldescriptionfound,
                url_image=urlimagefound,
                url_title=urltitlefound,
                url_image_server='',

                # images
                image_server_1='',

                # stats
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,
                decay_rate='1',

                # admin
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,
                creator_anon=0,
                shared_post=0,
                shared_time=now,
                created=now,
                edited=now,
                shared_thoughts='',
                age=post_age,
                business_id=None
            )

            getuser_timers.last_post = now
            user_stats.total_posts = newpostnumber

            # commit
            db.session.add(user_stats)
            db.session.add(getuser_timers)
            db.session.add(newpost)
            db.session.commit()

            if current_user.id != theuser.id:
                # add notification for poster about new post
                add_new_notification(user_id=theuser.id,
                                     subid=chosen_subcommon_id,
                                     subname=chosen_subcommon_name,
                                     postid=newpost.id,
                                     commentid=0,
                                     msg=16,
                                     )

            getusernodelocation = postnodelocation(x=newpost.id)
            postlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, "post", getusernodelocation, str(newpost.id))

            # image from url
            if urlfound != '':
                getimage(url=newpost.url_image, imagelocation=postlocation, thepost=newpost)

            # image From User
            if wall_post_form.image_one.data:
                mkdir_p(path=postlocation)
                filename = secure_filename(wall_post_form.image_one.data.filename)
                postimagefilepath = os.path.join(postlocation, filename)
                wall_post_form.image_one.data.save(postimagefilepath)
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(postimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(postlocation, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)
                convertimage(imagelocation=postlocation, imagename=newfilename, thepost=newpost)

            if wall_post_form.image_one.data or (urlimagefound is not None and urlfound is not None):
                db.session.commit()

            # add exp points
            exppoint(user_id=current_user.id, category=1)

            if current_user.id != theuser.id:
                add_new_notification(user_id=theuser.id,
                                     subid=chosen_subcommon_id,
                                     subname=chosen_subcommon_name,
                                     postid=newpost.id,
                                     commentid=0,
                                     msg=14
                                     )

            if current_user.id == theuser.id:
                flash("Post Created!", category="success")
                return redirect((url_for('profile.main', user_name=theuser.user_name)))
            else:
                flash("Post Created!", category="success")
                return redirect((url_for('profile.profile_other_posts_all', user_name=theuser.user_name)))
        else:

            flash("Post Creation Failure.", category="danger")

            for errors in wall_post_form.post_message.errors:
                flash("Message Failure...a message is required and 3- 5000 characters", category="danger")
                flash(errors, category="danger")
            for errors in wall_post_form.image_one.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@create.route('/roompost/<string:subname>', methods=['POST'])
@login_required
def create_post_room(subname):

    now = datetime.utcnow()
    id_pic1 = id_generator_picture1()
    wall_post_form = RoomPostForm()
    uniqueid = id_generator(size=15)

    if request.method == 'POST':

        # # TIMERS
        # seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # # if there is enough time
        # if seeiftimerallowed == 0:
        #     flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
        #     return redirect((request.args.get('next', request.referrer)))

        getcurrentsub = db.session.query(SubForums)
        getcurrentsub = getcurrentsub.filter(SubForums.subcommon_name == subname)
        getcurrentsub = getcurrentsub.first()

        getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()

        user_stats = db.session.query(UserStats).filter(UserStats.user_id == current_user.id).first()

        if wall_post_form.validate_on_submit():
            # see if user posted comment
            if wall_post_form.post_message.data == '':
                score_1 = 0
            else:
                score_1 = 1
            if wall_post_form.image_one.data:
                score_2 = 1
            else:
                score_2 = 0
            total_score = score_1 + score_2
            if total_score == 0:
                flash("You need to post some content", category="success")
                return redirect((request.args.get('next', request.referrer)))

            seeifsubscribed = Subscribed.query.filter(current_user.id == Subscribed.user_id).first()
            if seeifsubscribed:
                chosen_subcommon_id = getcurrentsub.id
                chosen_subcommon_name = getcurrentsub.subcommon_name
            else:
                flash("You are not subscribed to this room", category="success")
                return redirect((request.args.get('next', request.referrer)))

            agereq = wall_post_form.age.data
            if agereq is True:
                post_age = 1
            else:
                post_age = 0

            if current_user.anon_mode == 0:
                visible_user_id = current_user.id
                visible_user_name = current_user.user_name
                userhidden = 0
            else:
                visible_user_id = 0
                visible_user_name = "Anonymous"
                userhidden = 1

            if current_user.anon_mode == 1:
                p_user_hidden = 1
                p_user_name = 'anonymous'
                p_user_id = 0
            else:
                p_user_hidden = 0
                p_user_name = current_user.user_name
                p_user_id = current_user.id

            newpostnumber = user_stats.total_posts + 1

            urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(wall_post_form.post_message.data)
            transformed_text = transform_image_links_markdown(wall_post_form.post_message.data)
            # add post to db
            newpost = CommonsPost(
                # creator
                created=now,
                edited=now,
                shared_post=0,

                user_id=current_user.id,
                user_name=current_user.user_name,
                visible_user_id=visible_user_id,
                visible_user_name=visible_user_name,
                userhidden=userhidden,

                poster_user_name=current_user.user_name,
                poster_user_id=current_user.id,
                poster_visible_user_id=p_user_id,
                poster_visible_user_name=p_user_name,
                poster_userhidden=p_user_hidden,

                content_user_name=current_user.user_name,
                content_user_id=current_user.id,
                creator_anon=userhidden,

                # location
                realid=uniqueid,
                subcommon_id=chosen_subcommon_id,
                subcommon_name=chosen_subcommon_name,
                type_of_post=0,

                # text
                post_text=transformed_text,

                # url
                url_of_post=urlfound,
                url_description=urldescriptionfound,
                url_image=urlimagefound,
                url_title=urltitlefound,
                url_image_server='',
                decay_rate='1',

                # images
                image_server_1='',

                # stats
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,

                # admin
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,

                shared_time=now,
                shared_thoughts='',
                age=post_age,
                business_id=None
            )

            getuser_timers.last_post = now
            user_stats.total_posts = newpostnumber

            db.session.add(user_stats)
            db.session.add(getuser_timers)
            db.session.add(newpost)
            db.session.commit()

            getusernodelocation = postnodelocation(x=newpost.id)
            postlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, "post", getusernodelocation, str(newpost.id))

            # image from url
            if urlfound:
                getimage(url=newpost.url_image, imagelocation=postlocation, thepost=newpost)

            # image From User
            if wall_post_form.image_one.data:
                mkdir_p(path=postlocation)
                filename = secure_filename(wall_post_form.image_one.data.filename)
                postimagefilepath = os.path.join(postlocation, filename)
                wall_post_form.image_one.data.save(postimagefilepath)
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(postimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(postlocation, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)
                convertimage(imagelocation=postlocation, imagename=newfilename, thepost=newpost)

            if wall_post_form.image_one.data or (urlimagefound is not None and urlfound is not None):
                db.session.commit()

            # add exp points
            exppoint(user_id=current_user.id, category=1)

            flash("Post Created!", category="success")
            return redirect((url_for('subforum.viewpost',subname=newpost.subcommon_name, postid=newpost.id)))
        else:

            flash("Post Creation Failure.", category="danger")

            for errors in wall_post_form.image_one.errors:
                flash(errors, category="danger")
            for errors in wall_post_form.post_message.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@create.route('/roompost/<int:userid>', methods=['POST'])
@login_required
def create_post_room_all(userid):

    now = datetime.utcnow()
    id_pic1 = id_generator_picture1()
    wall_post_form = MainPostForm()
    uniqueid = id_generator(size=15)

    if request.method == 'POST':

        # # TIMERS
        # seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # # if there is enough time
        # if seeiftimerallowed == 0:
        #     flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
        #     return redirect((request.args.get('next', request.referrer)))

        usersubforums = db.session.query(Subscribed)
        usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
        usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
        usersubforums = usersubforums.filter(SubForums.id != 1)
        usersubforums = usersubforums.all()

        wall_post_form.roomname.choices = [(str(row.subscriber.id), str(row.subscriber.subcommon_name)) for row in usersubforums]

        theuser = User.query.filter(User.id == userid).first()
        getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()

        user_stats = db.session.query(UserStats).filter(UserStats.user_id == current_user.id).first()

        if wall_post_form.validate_on_submit():

            # see if user posted comment
            if wall_post_form.post_message.data == '':
                score_1 = 0
            else:
                score_1 = 1
            if wall_post_form.image_one.data:
                score_2 = 1
            else:
                score_2 = 0
            total_score = score_1 + score_2
            if total_score == 0:
                flash("You need to post some content", category="success")
                return redirect((request.args.get('next', request.referrer)))

            getmatchingsubcommon = SubForums.query.filter(SubForums.id == int(wall_post_form.roomname.data)).first()
            seeifsubscribed = Subscribed.query.filter(current_user.id == Subscribed.user_id).first()
            if seeifsubscribed:
                chosen_subcommon_id = getmatchingsubcommon.id
                chosen_subcommon_name = getmatchingsubcommon.subcommon_name
            else:
                flash("You are not subscribed to this room", category="success")
                return redirect((request.args.get('next', request.referrer)))
            agereq = wall_post_form.age.data
            if agereq is True:
                post_age = 1
            else:
                post_age = 0

            if current_user.anon_mode == 0:
                visible_user_id = current_user.id
                visible_user_name = current_user.user_name
                userhidden = 0
            else:
                visible_user_id = 0
                visible_user_name = "Anonymous"
                userhidden = 1

            if current_user.anon_mode == 1:
                p_user_hidden = 1
                p_user_name = 'anonymous'
                p_user_id = 0
            else:
                p_user_hidden = 0
                p_user_name = current_user.user_name
                p_user_id = current_user.id

            newpostnumber = user_stats.total_posts + 1

            urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(wall_post_form.post_message.data)
            transformed_text = transform_image_links_markdown(wall_post_form.post_message.data)
            # add post to db
            newpost = CommonsPost(

                user_id=theuser.id,
                user_name=theuser.user_name,
                visible_user_id=visible_user_id,
                visible_user_name=visible_user_name,
                userhidden=userhidden,

                poster_user_name=current_user.user_name,
                poster_user_id=current_user.id,
                poster_visible_user_id=p_user_id,
                poster_visible_user_name=p_user_name,
                poster_userhidden=p_user_hidden,

                content_user_name=current_user.user_name,
                content_user_id=current_user.id,
                creator_anon=userhidden,

                # location
                realid=uniqueid,
                subcommon_id=chosen_subcommon_id,
                subcommon_name=chosen_subcommon_name,
                type_of_post=0,

                # text
                post_text=transformed_text,

                # url
                url_of_post=urlfound,
                url_description=urldescriptionfound,
                url_image=urlimagefound,
                url_title=urltitlefound,
                url_image_server='',

                # images
                image_server_1='',

                # stats
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,

                # admin
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,

                created=now,
                edited=now,
                shared_post=0,

                shared_time=now,
                shared_thoughts='',

                age=post_age,
                business_id=None

            )

            getuser_timers.last_post = now
            user_stats.total_posts = newpostnumber

            db.session.add(user_stats)
            db.session.add(getuser_timers)
            db.session.add(newpost)
            db.session.commit()

            getusernodelocation = postnodelocation(x=newpost.id)
            postlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, "post", getusernodelocation, str(newpost.id))

            # image from url
            if urlfound:
                getimage(url=newpost.url_image, imagelocation=postlocation, thepost=newpost)

            # image From User
            if wall_post_form.image_one.data:
                mkdir_p(path=postlocation)
                filename = secure_filename(wall_post_form.image_one.data.filename)
                postimagefilepath = os.path.join(postlocation, filename)
                wall_post_form.image_one.data.save(postimagefilepath)
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(postimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(postlocation, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)
                convertimage(imagelocation=postlocation, imagename=newfilename, thepost=newpost)

            if wall_post_form.image_one.data or (urlimagefound is not None and urlfound is not None):
                db.session.commit()

            # add exp points
            exppoint(user_id=current_user.id, category=1)

            flash("Post Created!", category="success")
            return redirect((url_for('subforum.viewpost',subname=newpost.subcommon_name, postid=newpost.id)))
        else:

            flash("Post Creation Failure.", category="danger")
            for errors in wall_post_form.roomname.errors:
                flash(errors, category="danger")
            for errors in wall_post_form.post_message.errors:
                flash("Message Failure...a message is required and 3- 5000 characters", category="danger")
                flash(errors, category="danger")
            for errors in wall_post_form.image_one.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@create.route('/businesspost/<int:businessid>', methods=['POST'])
@login_required
def create_post_business_wall(businessid):
    business_post_form = BusinessPostForm()

    chosen_subcommon_id = 13
    chosen_subcommon_name = 'Business'

    thebiz = Business.query.filter(Business.id == businessid).first()

    if request.method == 'POST':

        # TIMERS
        seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # if there is enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
            return redirect((request.args.get('next', request.referrer)))

        now = datetime.utcnow()
        id_pic1 = id_generator_picture1()

        uniqueid = id_generator(size=15)

        if current_user.id != thebiz.user_id:
            return redirect(url_for('index'))
        # validation
        if business_post_form.validate_on_submit():

            # see if user posted comment
            if business_post_form.post_message.data == '':
                score_1 = 0
            else:
                score_1 = 1

            if business_post_form.image_one.data:
                score_2 = 1
            else:
                score_2 = 0

            total_score = score_1 + score_2

            if total_score == 0:
                flash("You need to post some content", category="success")
                return redirect((request.args.get('next', request.referrer)))

            # transform text
            urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(business_post_form.post_message.data)
            transformed_text = transform_image_links_markdown(business_post_form.post_message.data)

            newpost = CommonsPost(
                user_id=current_user.id,
                user_name=current_user.user_name,
                visible_user_id=current_user.id,
                visible_user_name=current_user.user_name,
                userhidden=0,
                poster_user_name=thebiz.business_name,
                poster_user_id=thebiz.id,
                poster_visible_user_id=thebiz.id,
                poster_visible_user_name=thebiz.business_name,
                poster_userhidden=0,
                content_user_name=thebiz.business_name,
                content_user_id=thebiz.id,
                realid=uniqueid,
                subcommon_id=chosen_subcommon_id,
                subcommon_name=chosen_subcommon_name,
                type_of_post=1,
                post_text=transformed_text,
                url_of_post=urlfound,
                url_description=urldescriptionfound,
                url_image=urlimagefound,
                url_title=urltitlefound,
                url_image_server='',
                image_server_1='',
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,
                decay_rate='1',
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,
                creator_anon=0,
                shared_post=0,
                shared_time=now,
                created=now,
                edited=now,
                shared_thoughts='',
                age=0,
                business_id=thebiz.id
            )

            db.session.add(newpost)
            db.session.commit()

            getusernodelocation = postnodelocation(x=newpost.id)
            postlocation = os.path.join(UPLOADED_FILES_DEST,  getusernodelocation, "post", getusernodelocation, str(newpost.id))

            # image from url
            if urlfound != '':
                getimage(url=newpost.url_image, imagelocation=postlocation, thepost=newpost)

            # image From User
            if business_post_form.image_one.data:
                mkdir_p(path=postlocation)
                filename = secure_filename(business_post_form.image_one.data.filename)
                postimagefilepath = os.path.join(postlocation, filename)
                business_post_form.image_one.data.save(postimagefilepath)
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(postimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(postlocation, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)
                convertimage(imagelocation=postlocation, imagename=newfilename, thepost=newpost)

            if business_post_form.image_one.data or (urlimagefound is not None and urlfound is not None):
                db.session.commit()

            # add exp points
            exppoint(user_id=current_user.id, category=1)

            flash("Post Created!", category="success")
            return redirect((url_for('business.main', business_name=thebiz.business_name)))
        else:

            flash("Post Creation Failure.", category="danger")

            for errors in business_post_form.post_message.errors:
                flash("Message Failure...a message is required and 3- 5000 characters", category="danger")
                flash(errors, category="danger")
            for errors in business_post_form.image_one.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@create.route('/businesspost/other/<int:businessid>', methods=['POST'])
@login_required
def create_post_business_wall_other(businessid):
    business_post_form = BusinessPostForm()
    now = datetime.utcnow()
    id_pic1 = id_generator_picture1()
    uniqueid = id_generator(size=15)
    chosen_subcommon_id = 13
    chosen_subcommon_name = 'Business'

    thebiz = Business.query.filter(Business.id == businessid).first()

    if request.method == 'POST':

        # TIMERS
        seeiftimerallowed, timeleft = lastposted(user_id=current_user.id)
        # if there is enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " seconds before creating another post", category="info")
            return redirect((request.args.get('next', request.referrer)))

        # see if user posted comment
        if business_post_form.post_message.data == '':
            score_1 = 0
        else:
            score_1 = 1
        if business_post_form.image_one.data:
            score_2 = 1
        else:
            score_2 = 0
        total_score = score_1 + score_2
        if total_score == 0:
            flash("You need to post some content", category="success")
            return redirect((request.args.get('next', request.referrer)))

        if business_post_form.validate_on_submit():

            urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(business_post_form.post_message.data)
            transformed_text = transform_image_links_markdown(business_post_form.post_message.data)
            # add post to db
            newpost = CommonsPost(

                user_id=current_user.id,
                user_name=current_user.user_name,
                visible_user_id=current_user.id,
                visible_user_name=current_user.user_name,
                userhidden=0,


                poster_user_name=current_user.user_name,
                poster_user_id=current_user.id,
                poster_visible_user_id=current_user.id,
                poster_visible_user_name=current_user.user_name,
                poster_userhidden=0,

                content_user_name=current_user.user_name,
                content_user_id=current_user.id,

                # location
                realid=uniqueid,
                subcommon_id=chosen_subcommon_id,
                subcommon_name=chosen_subcommon_name,
                type_of_post=0,

                # text
                post_text=transformed_text,

                # url
                url_of_post=urlfound,
                url_description=urldescriptionfound,
                url_image=urlimagefound,
                url_title=urltitlefound,
                url_image_server='',

                # images
                image_server_1='',

                # stats
                total_exp_commons=0,
                highest_exp_reached=0,
                downvotes_on_post=0,
                upvotes_on_post=0,
                comment_count=0,
                vote_timestamp=now,
                last_active=now,
                hotness_rating_now=0,
                page_views=0,
                decay_rate='1',

                # admin
                sticky=0,
                active=1,
                locked=0,
                hidden=0,
                muted=0,
                crawlneed=0,
                creator_anon=0,
                shared_post=0,
                shared_time=now,
                created=now,
                edited=now,
                shared_thoughts='',
                age=0,
                business_id=thebiz.id
            )

            db.session.add(newpost)
            db.session.commit()

            getusernodelocation = postnodelocation(x=newpost.id)
            postlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, "post", getusernodelocation, str(newpost.id))

            # image from url
            if urlfound != '':
                getimage(url=newpost.url_image, imagelocation=postlocation, thepost=newpost)

            # image From User
            if business_post_form.image_one.data:
                mkdir_p(path=postlocation)
                filename = secure_filename(business_post_form.image_one.data.filename)
                postimagefilepath = os.path.join(postlocation, filename)
                business_post_form.image_one.data.save(postimagefilepath)
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(postimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(postlocation, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)
                convertimage(imagelocation=postlocation, imagename=newfilename, thepost=newpost)

            if business_post_form.image_one.data or (urlimagefound is not None and urlfound is not None):
                db.session.commit()

            # add exp points
            exppoint(user_id=current_user.id, category=1)

            flash("Post Created!", category="success")
            return redirect((url_for('business.main_post_to_another_wall', business_name=thebiz.business_name)))
        else:
            flash("Post Creation Failure.", category="danger")
            for errors in business_post_form.roomname.errors:
                flash(errors, category="danger")
            for errors in business_post_form.post_message.errors:
                flash("Message Failure...a message is required and 3- 5000 characters", category="danger")
                flash(errors, category="danger")
            for errors in business_post_form.image_one.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))
