from flask import \
    render_template, \
    redirect, \
    url_for,\
    request, \
    flash
from flask_login import current_user
from app import db, app

from app.common.decorators import login_required

from app.profile_edit import profileedit
from app.profile_edit.forms import\
    DeleteSaveForm,\
    DeleteSaveAllForm,\
    MyAccountForm,\
    UserBioForm, UnblockForm
from app.vote.forms import VoteForm
from app.models import \
    User,\
    CommonsPost, \
    SavedPost, \
    UserPublicInfo,\
    UserLargePublicInfo, BlockedUser


@profileedit.route('/save/<int:postid>', methods=['POST'])
@login_required
def savepost(postid):

    if request.method == 'POST':

        thepost = db.session.query(CommonsPost)
        thepost = thepost.filter(CommonsPost.id == postid)
        thepost = thepost.first()

        createnewsave = SavedPost(
            user_id=current_user.id,
            post_id=thepost.id
        )

        db.session.add(createnewsave)
        db.session.commit()

        flash("Post has been saved", category="success")
        return redirect((request.args.get('next', request.referrer)))


@profileedit.route('/savepost/<int:postid>')
@login_required
def savepostnoform(postid):

    thepost = db.session.query(CommonsPost)
    thepost = thepost.filter(CommonsPost.id == postid)
    thepost = thepost.first()

    createnewsave = SavedPost(
        user_id=current_user.id,
        post_id=thepost.id
    )

    db.session.add(createnewsave)
    db.session.commit()

    flash("Post has been saved", category="success")
    return redirect((request.args.get('next', request.referrer)))


@profileedit.route('/viewsaved', methods=['GET'])
@login_required
def viewsavedposts():
    form = DeleteSaveForm()
    deleteallform = DeleteSaveAllForm()
    page = request.args.get('page', 1, type=int)

    savedposts = db.session.query(CommonsPost)
    savedposts = savedposts.join(SavedPost, (CommonsPost.id == SavedPost.post_id))
    savedposts = savedposts.filter(SavedPost.user_id == current_user.id)
    savedposts = savedposts.order_by(SavedPost.created.desc())
    savedposts = savedposts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('profileedit.viewsavedposts', page=savedposts.next_num) \
        if savedposts.has_next else None
    prev_url = url_for('profileedit.viewsavedposts', page=savedposts.prev_num) \
        if savedposts.has_prev else None
    return render_template('users/profile/profile_subpages/profile_viewsaved.html',
                           form=form,
                           deleteallform=deleteallform,
                           savedposts=savedposts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@profileedit.route('/deletesaved/<string:postid>', methods=['POST'])
@login_required
def deletesavedpost(postid):

    if request.method == 'POST':

        savedposts = db.session.query(SavedPost)
        savedposts = savedposts.filter(SavedPost.post_id == postid)
        savedposts = savedposts.filter(SavedPost.user_id == current_user.id)
        savedposts = savedposts.first_or_404()

        db.session.delete(savedposts)
        db.session.commit()
        flash("Post has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))


@profileedit.route('/deleteallsaved', methods=['POST'])
@login_required
def deleteallsavedposts():

    if request.method == 'POST':

        savedposts = db.session.query(SavedPost)
        savedposts = savedposts.filter(SavedPost.user_id == current_user.id)
        savedposts = savedposts.all()
        for s in savedposts:
            db.session.delete(s)
        db.session.commit()
        flash("All saved posts have been deleted", category="success")
        return redirect(url_for('profileedit.viewsavedposts'))


@profileedit.route('/view', methods=['GET'])
@login_required
def view_bio():
    user = User.query.filter_by(id=current_user.id).first()
    if user.userpublicinfo is None:

        userbio = UserPublicInfo(
            user_id=user.id,
            bio='',
            short_bio=''
        )
        db.session.add(userbio)
        db.session.commit()
    form = MyAccountForm(Bio=user.userpublicinfo.bio,
                         Shortbio=user.userpublicinfo.short_bio
                         )

    return render_template('users/profile/profile_forms/profile_bio.html',
                           form=form,
                           )


@profileedit.route('/edit/basic', methods=['POST'])
@login_required
def edit_bio():

    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        form = MyAccountForm(Bio=user.userpublicinfo.bio,
                             Shortbio=user.userpublicinfo.short_bio
                             )
        if form.validate_on_submit():

            user.userpublicinfo.short_bio = form.Shortbio.data
            user.userpublicinfo.bio = form.Bio.data
            db.session.add(user.userpublicinfo)
            db.session.commit()

            flash('Profile has been changed', category="success")
            return redirect(url_for('profile.main', user_name=user.user_name))
        else:
            flash("Form error", category="danger")
            return redirect(url_for('profileedit.view_bio'))


@profileedit.route('/aboutme', methods=['GET'])
@login_required
def view_large_bio():
    user = User.query.filter_by(id=current_user.id).first()
    userlargeinfo = UserLargePublicInfo.query.filter(UserLargePublicInfo.user_id == current_user.id).first()
    if userlargeinfo is None:

        userbio = UserLargePublicInfo(
            user_id=user.id,
            bio='',

        )
        db.session.add(userbio)
        db.session.commit()
        return redirect(url_for('profileedit.view_large_bio'))
    form = UserBioForm(bio=userlargeinfo.bio)

    return render_template('users/profile/profile_forms/profile_about.html',
                           form=form,
                           )


@profileedit.route('/edit/aboutme', methods=['POST'])
@login_required
def edit_large_bio():

    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        userlargeinfo = UserLargePublicInfo.query.filter(UserLargePublicInfo.user_id == current_user.id).first()
        form = UserBioForm(bio=userlargeinfo.bio)
        if form.validate_on_submit():

            userlargeinfo.bio = form.bio.data
            db.session.add(user.userpublicinfo)
            db.session.commit()

            flash('Profile has been changed', category="success")
            return redirect(url_for('profileedit.view_large_bio'))
        else:
            flash("Form error", category="danger")
            return redirect(url_for('profileedit.view_large_bio'))


@profileedit.route('/unblocklist', methods=['GET'])
@login_required
def unblock_users():
    if request.method == 'GET':
        blocked_users = BlockedUser.query.filter(BlockedUser.user_id == current_user.id).all()
        return render_template('users/profile/profile_forms/profile_unblock.html',
                               blocked_users=blocked_users
                               )
    if request.method == 'POST':
        return redirect(url_for('index'))


@profileedit.route('/unblock/<user_name>', methods=['GET'])
@login_required
def unblockuser(user_name):
    if request.method == 'GET':
        user = User.query.filter_by(user_name=user_name).first()
        if user is None:
            flash('User {} not found.'.format(user_name), category="danger")
            return redirect(url_for('profile.main', user_name=current_user.user_name))
        if user == current_user:
            flash('You cannot block yourself!', category="danger")
            return redirect(url_for('profile.main', user_name=user_name))

        gettheblock = BlockedUser.query.filter(BlockedUser.user_id == current_user.id,
                                               BlockedUser.blocked_user == user.id).first()
        db.session.delete(gettheblock)
        db.session.commit()
        flash('You are not blocking {}!'.format(user_name), category="success")
        return redirect(url_for('profileedit.unblock_users'))

    if request.method == 'POST':
        return redirect(url_for('index'))