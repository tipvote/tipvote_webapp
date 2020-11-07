
import os
from datetime import datetime
# flask imports
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash
from flask import request
from flask_login import current_user
# common imports
from app.common.decorators import login_required
from werkzeug.utils import secure_filename
from app.common.functions import mkdir_p, id_generator_picture1
from app import db
# relative directory
from app.edit import edit
from app.edit.forms import\
    EditPostTextForm,\
    EditCommentForm,\
    DeleteCommentTextForm,\
    DeletePostTextForm
from app.vote.forms import VoteForm
from app.profile_edit.forms import \
    SaveForm
from app.create.forms import \
    CreateCommentForm
from app.subforum.forms import \
    SubscribeForm, \
    ReportForm

from app.classes.comment import Comments
from app.classes.post import CommonsPost
from app.classes.subforum import \
    PrivateMembers, \
    SubForums, \
    SubForumCustom, \
    Subscribed, \
    Mods
from app.classes.btc import BtcPrices
from app.classes.monero import MoneroPrices
from app.classes.bch import BchPrices
from app.classes.business import Business
from app.classes.ltc import LtcPrices

from app.create.get_image_resize import convertimage
from app import UPLOADED_FILES_DEST
from app.nodelocations import postnodelocation, current_disk
from app.create.geturlinfo import geturl
from app.create.get_image_fromurl import getimage
from app.create.convert_markdown import transform_image_links_markdown
from app.message.add_notification import add_new_notification


# View / Reply to a post
@edit.route('/post/<int:postid>', methods=['GET'])
@login_required
def viewpost_edit(postid):
    """
    View / Reply to a post
    """

    form = CreateCommentForm()
    saveform = SaveForm()
    reportform = ReportForm()
    reportcommentform = ReportForm()
    subform = SubscribeForm()
    editcommenttextform = EditCommentForm()
    deleteposttextform = DeletePostTextForm()
    deletecommenttextform = DeleteCommentTextForm()
    voteform = VoteForm()

    currentbtcprice = db.session.query(BtcPrices).get(1)
    currentxmrprice = db.session.query(MoneroPrices).get(1)
    currentbchprice = db.session.query(BchPrices).get(1)
    currentltcprice = db.session.query(LtcPrices).get(1)

    # get the sub
    thepost = db.session.query(CommonsPost).filter_by(id=postid).first_or_404()

    # security
    if thepost.business_id is None:
        if current_user.id != thepost.poster_user_id:
            flash("Not allowed to edit this post.", category="danger")
            return redirect((request.args.get('next', request.referrer)))
    else:
        thebiz = db.session.query(Business).filter(Business.id == thepost.business_id).first()
        if thebiz.user_id != current_user.id:
            return redirect(url_for('index'))

    editposttextform = EditPostTextForm(request.form, postmessage=thepost.post_text)

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == thepost.subcommon_name).first_or_404()
    # get sub customization
    subcustom_stuff = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
    # get id of the sub
    subid = int(thesub.id)
    subtype = thesub.type_of_subcommon
    subname = thepost.subcommon_name

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
        usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                               SubForums.room_deleted == 0,
                                               SubForums.room_suspended == 0
                                               )
        usersubforums = usersubforums.all()

    else:
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

    comments = db.session.query(Comments)
    comments = comments.filter(Comments.commons_post_id == thepost.id)
    comments = comments.order_by(Comments.path.asc())
    comments = comments.all()

    return render_template('create/edit/edit_post.html',
                           form=form,
                           saveform=saveform,
                           reportform=reportform,
                           reportcommentform=reportcommentform,
                           editposttextform=editposttextform,
                           editcommenttextform=editcommenttextform,
                           deleteposttextform=deleteposttextform,
                           deletecommenttextform=deletecommenttextform,
                           subform=subform,
                           voteform=voteform,

                           subname=subname,
                           seeifsubbed=-seeifsubbed,
                           comments=comments,
                           thesub=thesub,
                           post=thepost,
                           usersubforums=usersubforums,
                           getcurrentsub=thesub,
                           subcustom_stuff=subcustom_stuff,

                           currentbtcprice=currentbtcprice,
                           currentxmrprice=currentxmrprice,
                           currentbchprice=currentbchprice,
                           currentltcprice=currentltcprice,
                           )


def delete_image_server_one(user_id, postid):
    if current_user.id == user_id:
        post_image_one = CommonsPost.query.filter(CommonsPost.id == postid).first()
        file0 = os.path.join(UPLOADED_FILES_DEST, post_image_one.image_server_1)
        try:
            os.remove(file0)
        except:
            pass
        post_image_one.image_server_1 = ''
        db.session.add(post_image_one)
        db.session.commit()
    else:
        return redirect(url_for('index'))


def delete_image_url_server(user_id, postid):
    if current_user.id == user_id:
        post_url_image = CommonsPost.query.filter(CommonsPost.id == postid).first()
        file0 = os.path.join(UPLOADED_FILES_DEST, post_url_image.url_image_server)
        try:
            os.remove(file0)
        except:
            pass
        post_url_image.url_image_server = ''
        db.session.add(post_url_image)
        db.session.commit()

    else:
        return redirect(url_for('index'))


@edit.route('/post/text/edit/<int:postid>', methods=['POST'])
@login_required
def post_edit_text(postid):
    now = datetime.utcnow()
    editposttextform = EditPostTextForm()
    id_pic1 = id_generator_picture1()

    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == int(postid)).first()

    if request.method == 'POST':

        # security
        if thepost.business_id is None:
            if current_user.id != thepost.poster_user_id:

                flash("Not allowed to edit this post.", category="danger")
                return redirect((request.args.get('next', request.referrer)))

        else:
            thebiz = db.session.query(Business).filter(Business.id == thepost.business_id).first()
            if thebiz.user_id != current_user.id:
                return redirect((request.args.get('next', request.referrer)))

        if editposttextform.validate_on_submit():
            if editposttextform.delete.data:
                delete_image_server_one(user_id=current_user.id, postid=postid)
                return redirect((request.args.get('next', request.referrer)))

            if editposttextform.submit.data:
                urlfound, urltitlefound, urldescriptionfound, urlimagefound = geturl(editposttextform.postmessage.data)
                transformed_text, notifyuser = transform_image_links_markdown(str(editposttextform.postmessage.data))

                getpostnodelocation = postnodelocation(x=thepost.id)
                postlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, "post", getpostnodelocation, str(thepost.id))
                thepost.post_text = transformed_text

                if urlfound:
                    delete_image_url_server(user_id=current_user.id, postid=postid)
                    thepost.url_image = urlimagefound
                    thepost.url_title = urltitlefound
                    thepost.url_of_post = urlfound
                    thepost.url_description = urldescriptionfound
                    getimage(url=thepost.url_image, imagelocation=postlocation, thepost=thepost)

                if editposttextform.image_one.data:
                    mkdir_p(path=postlocation)
                    filename = secure_filename(editposttextform.image_one.data.filename)
                    postimagefilepath = os.path.join(postlocation, filename)
                    editposttextform.image_one.data.save(postimagefilepath)
                    filenamenew, file_extension = os.path.splitext(postimagefilepath)
                    newfilename = id_pic1 + file_extension
                    filenamenewfull = filenamenew + file_extension
                    newfilenamedestination = os.path.join(postlocation, newfilename)
                    os.rename(filenamenewfull, newfilenamedestination)
                    convertimage(imagelocation=postlocation, imagename=newfilename, thepost=thepost)

                if notifyuser is not None:
                    # add info
                    add_new_notification(user_id=notifyuser.id,
                                         subid=thepost.subcommon_id,
                                         subname=thepost.subcommon_name,
                                         postid=thepost.id,
                                         commentid=0,
                                         msg=32
                                         )
            thepost.edited = now
            db.session.commit()

            flash("Post edited", category="success")
            return redirect(url_for('subforum.viewpost', subname=thepost.subcommon_name, postid=thepost.id))
        else:
            flash("form error")
            for errors in editposttextform.postmessage.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))


@edit.route('/comment/<int:commentid>', methods=['GET'])
@login_required
def comment_edit(commentid):
    thecomment = db.session.query(Comments).filter(Comments.id == commentid).first()

    editcommenttextform = EditCommentForm(
        request.form,
        postmessage=thecomment.body
    )

    # see if user is a creator
    if thecomment.user_id != current_user.id:
        flash("You are not the creator of this comment.", category="danger")
        return redirect((request.args.get('next', request.referrer)))

    return render_template('create/edit/commentedit.html',
                           editcommenttextform=editcommenttextform,
                           thecomment=thecomment)


@edit.route('/comment/text/edit/<int:commentid>', methods=['POST'])
@login_required
def comment_edit_text(commentid):
    editcommenttextform = EditCommentForm()
    if request.method == 'POST':
        if editcommenttextform.validate_on_submit():

            thecomment = db.session.query(Comments).filter(Comments.id == int(commentid)).first()
            thesub = db.session.query(SubForums).filter(thecomment.subcommon_id == SubForums.id).first()
            transformed_text, notifyuser = transform_image_links_markdown(str(editcommenttextform.postmessage.data))

            if notifyuser is not None:
                # add info
                add_new_notification(user_id=notifyuser.id,
                                     subid=thesub.id,
                                     subname=thesub.subcommon_name,
                                     postid=thecomment.commons_post_id,
                                     commentid=0,
                                     msg=32
                                     )
            # see if user is a creator
            if thecomment.user_id == current_user.id:
                thecomment.body = transformed_text
                db.session.add(thecomment)
                db.session.commit()
                flash("Updated Comment.", category="success")
                return redirect(url_for('subforum.viewpost',
                                        subname=thesub.subcommon_name,
                                        postid=thecomment.commons_post_id))
            else:
                flash("You are not the creator of this post.", category="danger")
                return redirect(url_for('subforum.viewpost',
                                        subname=thesub.subcommon_name,
                                        postid=thecomment.commons_post_id))
        else:
            for errors in editcommenttextform.postmessage.errors:
                flash(errors, category="danger")
            return redirect((request.args.get('next', request.referrer)))













# --------------------------------------------------------------------------------------
# deletion

@edit.route('/post/text/delete/<int:postid>', methods=['POST'])
@login_required
def post_delete_text(postid):
    if request.method == 'POST':

        thepost = db.session.query(CommonsPost).filter(CommonsPost.id == int(postid)).first()
        # see if user is a creator

        # security
        if thepost.business_id is None:

            if current_user.id != thepost.poster_user_id:
                flash("Not allowed to delete this post.", category="danger")
                return redirect((request.args.get('next', request.referrer)))

        else:
            thebiz = db.session.query(Business).filter(Business.id == thepost.business_id).first()
            if thebiz.user_id != current_user.id:
                flash("Not allowed to delete this post.", category="danger")
                return redirect((request.args.get('next', request.referrer)))

        thepost.hidden = 1
        db.session.add(thepost)
        db.session.commit()
        flash("Deleted Post.", category="danger")
        return redirect((request.args.get('next', request.referrer)))

    if request.method == 'GET':
        flash("Error", category="danger")
        return redirect((request.args.get('next', request.referrer)))


@edit.route('/comment/text/delete/<int:commentid>', methods=['POST', 'GET'])
@login_required
def comment_delete_text(commentid):
    thecomment = db.session.query(Comments).filter(Comments.id == int(commentid)).first()
    if request.method == 'POST':

        # see if user is a creator
        if thecomment.user_id == current_user.id:

            thecomment.hidden = 1
            db.session.add(thecomment)
            db.session.commit()
            flash("Deleted Comment.", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        else:
            flash("You are not the creator of this comment.", category="danger")
            return redirect((request.args.get('next', request.referrer)))

    if request.method == 'GET':
        # see if user is a creator
        if thecomment.user_id == current_user.id:

            thecomment.hidden = 1
            db.session.add(thecomment)
            db.session.commit()
            flash("Deleted Comment.", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        else:
            flash("You are not the creator of this comment.", category="danger")
            return redirect((request.args.get('next', request.referrer)))
