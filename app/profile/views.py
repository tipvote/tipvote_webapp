from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, request
from flask_login import current_user
from app import db, app
from werkzeug.datastructures import CombinedMultiDict
from app.common.decorators import login_required

from app.profile.forms import FriendForm
from app.create.forms import MainPostForm
from app.edit.forms import DeletePostTextForm
from app.profile import profile
from app.vote.forms import VoteForm
from app.models import \
    User, \
    Followers, \
    CommonsPost, \
    UserLargePublicInfo, \
    BlockedUser,\
    Mods,\
    SubForums, Subscribed

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute


@profile.route('/<string:user_name>', methods=['GET'])
def main(user_name):
    # forms
    friendform = FriendForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    navlink = 1
    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))
    if user_name == 'Tipvote_Bot':
        user_name = "tipvote"
    theuser = db.session.query(User).filter(User.user_name == user_name).first()

    if theuser is None:
        flash('User does not exist', category='warning')
        return redirect(url_for('profile.main', user_name=current_user.user_name))

    if current_user.is_authenticated:
        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == theuser.id, BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash('User does not exist', category='warning')
            return redirect(url_for('index'))

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(theuser.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.age_required == 0)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.filter(SubForums.room_suspended != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned != 1)
    usersubforums = usersubforums.all()
    guestsubforums = None

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == theuser.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == theuser.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    # get followers
    get_followers = db.session.query(User)
    get_followers = get_followers.join(Followers, (User.id == Followers.followed_id))
    get_followers = get_followers.filter(Followers.follower_id == theuser.id)
    get_followers = get_followers.limit(9)

    # get users posts
    userposts = db.session.query(CommonsPost)
    userposts = userposts.filter(theuser.id == CommonsPost.user_id)
    userposts = userposts.filter(theuser.id == CommonsPost.poster_user_id)

    userposts = userposts.filter(CommonsPost.userhidden == 0)
    userposts = userposts.filter(CommonsPost.hidden == 0)
    userposts = userposts.filter(CommonsPost.muted == 0)
    userposts = userposts.order_by(CommonsPost.created.desc())
    posts = userposts.limit(50)
    postcount = userposts.count()

    follower_count = Followers.query.filter(Followers.follower_id == theuser.id).count()
    followed_count = Followers.query.filter(Followers.followed_id == theuser.id).count()
    return render_template('users/profile/profile.html',
                           seeifmod=seeifmod,
                           postcount=postcount,
                           moddingcount=moddingcount,
                           voteform=voteform,
                           ownercount=ownercount,
                           usersubforums=usersubforums,
                           guestsubforums=guestsubforums,
                           seeifowner=seeifowner,
                           wall_post_form=wall_post_form,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           friendform=friendform,
                           deleteposttextform=deleteposttextform,
                           posts=posts,
                           theuser=theuser,
                           user_name=user_name,
                           navlink=navlink,
                           get_followers=get_followers,
                           follower_count=follower_count,
                           followed_count=followed_count
                           )


@profile.route('/<string:user_name>/others', methods=['GET'])
def profile_other_posts_all(user_name):
    # forms
    friendform = FriendForm()
    voteform = VoteForm()
    deleteposttextform = DeletePostTextForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()
    navlink = 2
    wall_post_form = MainPostForm(CombinedMultiDict((request.files, request.form)))

    theuser = db.session.query(User).filter(User.user_name == user_name).first()
    if theuser is None:
        flash('User does not exist', category='warning')
        return redirect(url_for('profile.main', user_name=current_user.user_name))

    # see if blocked
    if current_user.is_authenticated:
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == theuser.id, BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash('User does not exist', category='warning')
            return redirect(url_for('index'))

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(theuser.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.filter(SubForums.age_required == 0)
    usersubforums = usersubforums.filter(SubForums.room_deleted != 1)
    usersubforums = usersubforums.filter(SubForums.room_suspended != 1)
    usersubforums = usersubforums.filter(SubForums.room_banned != 1)
    usersubforums = usersubforums.all()

    seeifmodding = db.session.query(Mods)
    seeifmodding = seeifmodding.filter(Mods.user_id == theuser.id)
    seeifmod = seeifmodding.all()
    moddingcount = seeifmodding.count()

    seeifownering = db.session.query(SubForums)
    seeifownering = seeifownering.filter(SubForums.creator_user_id == theuser.id)
    seeifownering = seeifownering.filter(SubForums.room_deleted != 1)
    seeifowner = seeifownering.all()
    ownercount = seeifownering.count()

    # get followers
    get_followers = db.session.query(User)
    get_followers = get_followers.join(Followers, (User.id == Followers.followed_id))
    get_followers = get_followers.filter(Followers.follower_id == theuser.id)
    get_followers = get_followers.limit(9)

    # get users posts
    userposts = db.session.query(CommonsPost)
    userposts = userposts.filter(CommonsPost.subcommon_id == 1)
    userposts = userposts.filter(CommonsPost.user_name == theuser.user_name)
    userposts = userposts.filter(CommonsPost.poster_user_id != theuser.id)
    userposts = userposts.filter(CommonsPost.hidden == 0)
    userposts = userposts.order_by(CommonsPost.created.desc())
    posts = userposts.limit(50)
    postcount = userposts.count()

    return render_template('users/profile/profile_other.html',
                           wall_post_form=wall_post_form,
                           postcount=postcount,
                           voteform=voteform,
                           usersubforums=usersubforums,
                           seeifmod=seeifmod,
                           ownercount=ownercount,
                           seeifowner=seeifowner,
                           moddingcount=moddingcount,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           friendform=friendform,
                           deleteposttextform=deleteposttextform,
                           posts=posts,
                           navlink=navlink,
                           theuser=theuser,
                           user_name=user_name,
                           get_followers=get_followers,
                           )


@profile.route('/<user_name>/follow')
@login_required
def follow(user_name):
    user = User.query.filter_by(user_name=user_name).first()

    # see if blocked
    isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == user.id,
                                             BlockedUser.blocked_user == current_user.id).first()
    if isuserblocked:
        flash('User does not exist', category='warning')
        return redirect(url_for('index'))

    if user is None:
        flash('User {} not found.'.format(user_name), category="danger")
        return redirect(url_for('profile.main', user_name=current_user.user_name))
    if user == current_user:
        flash('You cannot follow yourself!', category="danger")
        return redirect(url_for('profile.main', user_name=user_name))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(user_name), category="success")
    return redirect(url_for('profile.main', user_name=user_name))


@profile.route('/<user_name>/unfollow')
@login_required
def unfollow(user_name):
    user = User.query.filter_by(user_name=user_name).first()

    # see if blocked
    isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == user.id,
                                             BlockedUser.blocked_user == current_user.id).first()
    if isuserblocked:
        flash('User does not exist', category='warning')
        return redirect(url_for('index'))

    if user is None:
        flash('User {} not found.'.format(user_name), category="danger")
        return redirect(url_for('profile.main', user_name=current_user.user_name))
    if user == current_user:
        flash('You cannot unfollow yourself!', category="danger")
        return redirect(url_for('profile.main', user_name=user_name))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(user_name), category="danger")
    return redirect(url_for('profile.main', user_name=user_name))


@profile.route('/<userid>/idunfollow')
@login_required
def unfollow_by_id(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('User not found.', category="danger")
        return redirect(url_for('profile.main', user_name=current_user.user_name))
    if user == current_user:
        flash('You cannot unfollow yourself!', category="danger")
        return redirect(url_for('profile.main', user_name=user.user_name))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following', category="danger")
    return redirect(url_for('profile.profile_following_user', user_name=user.user_name))


@profile.route('/following/<string:user_name>', methods=['GET'])
@login_required
def profile_following_user(user_name):
    # forms

    theuser = db.session.query(User).filter(User.user_name == user_name).first()
    if theuser is None:
        flash('User does not exist', category='warning')
        return redirect(url_for('profile.main', user_name=current_user.user_name))

    # see if blocked
    isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == theuser.id,
                                             BlockedUser.blocked_user == current_user.id).first()
    if isuserblocked:
        flash('User does not exist', category='warning')
        return redirect(url_for('index'))

    # get followers
    page = request.args.get('page', 1, type=int)
    get_followers = db.session.query(User)
    get_followers = get_followers.join(Followers, (User.id == Followers.followed_id))
    get_followers = get_followers.filter(Followers.follower_id == theuser.id)
    posts = get_followers.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('users/profile/profile_subpages/profile_viewallfollowers.html',

                           theuser=theuser,
                           user_name=user_name,
                           get_followers=get_followers,
                           next_url=next_url,
                           prev_url=prev_url

                           )


@profile.route('/<string:user_name>/about', methods=['GET'])
def user_about(user_name):
    # forms
    theuser = db.session.query(User).filter(User.user_name == user_name).first()

    if current_user.is_authenticated:
        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == theuser.id,
                                                 BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash('User does not exist', category='warning')
            return redirect(url_for('index'))

    if theuser is None:
        flash('User does not exist', category='warning')
        return redirect(url_for('profile.main', user_name=current_user.user_name))
    aboutuser = UserLargePublicInfo.query.filter(UserLargePublicInfo.user_id == theuser.id).first()

    return render_template('users/profile/profile_subpages/about.html',
                           user_name=user_name,
                           theuser=theuser,
                           aboutuser=aboutuser
                           )


@profile.route('/<user_name>/block')
@login_required
def blockuser(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    # see if blocked
    if current_user.is_authenticated:
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == user.id,
                                                 BlockedUser.blocked_user == current_user.id).first()
        if isuserblocked:
            flash('User does not exist', category='warning')
            return redirect(url_for('index'))

    if user is None:
        flash('User {} not found.'.format(user_name), category="danger")
        return redirect(url_for('profile.main', user_name=current_user.user_name))
    if user == current_user:
        flash('You cannot block yourself!', category="danger")
        return redirect(url_for('profile.main', user_name=user_name))

    newblock = BlockedUser(
        user_id=current_user.id,
        blocked_user=user.id,
        blocked_user_name=user.user_name
    )
    db.session.add(newblock)
    db.session.commit()
    flash('You are blocking {}!'.format(user_name), category="success")
    return redirect(url_for('profile.main', user_name=current_user.user_name))


