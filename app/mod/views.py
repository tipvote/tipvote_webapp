# flask imports
import os
from datetime import datetime, timedelta
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash
from flask import request
from flask_login import current_user
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from app import db, app, UPLOADED_FILES_DEST
from app.nodelocations import subforumnodelocation, current_disk
from app.common.decorators import login_required
from app.common.timers import lastreport
from app.common.functions import id_generator_picture1, mkdir_p
from app.message.add_notification import add_new_notification


from app.subforum.image_resizer import convertimage


from app.mod import mod
from app.vote.forms import VoteForm
from app.mod.forms import\
    AddModForm, \
    RemoveModForm, \
    BanUserModForm, \
    UnBanUserModForm, \
    RemoveUserForm, \
    ChangeSubInfo, \
    AcceptUserForm, \
    AcceptSpecificUserForm, \
    QuickDelete, \
    QuickBanDelete, \
    UnReport, \
    SubCustomForm, \
    SubCustomThumbnailForm, \
    ChangeSubInfoBoxOne,\
    DeleteRoomForm,\
    NSFWForm

from app.models import \
    SubForums, \
    PrivateMembers, \
    SubForumStats, \
    PrivateApplications, \
    SubForumCustomInfoOne,\
    CommonsPost, \
    Comments,\
    SubForumCustom,\
    UserTimers, \
    User, \
    Mods, \
    Banned, \
    Muted, \
    ReportedComments, \
    ReportedPosts,\
    Subscribed

from app.mod.security import modcheck


@mod.route('/customize/<string:subname>', methods=['GET'])
@login_required
def customsub_looks(subname):
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    seeifstats = SubForumStats.query.filter(thesub.id == SubForumStats.subcommon_id).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    if seeifstats is None:
        substats = SubForumStats(
            subcommon_name=thesub.subcommon_name,
            subcommon_id=thesub.id,
            total_posts=0,
            total_exp_subcommon=0,
            members=1,
        )

        # sub customization ie banner
        newsubcustom = SubForumCustom(
            subcommon_name=thesub.subcommon_name,
            subcommon_id=thesub.id,
            banner_image='',
            mini_image='',
        )
        db.session.add(newsubcustom)
        db.session.add(substats)
        db.session.commit()
    # form
    subcustomform = SubCustomForm(
        CombinedMultiDict((request.files, request.form)),
    )
    # form
    subcustomform_thumbnail = SubCustomThumbnailForm(
        CombinedMultiDict((request.files, request.form)),
    )
    # mod customization

    subcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()

    return render_template('mod/main_custom_home.html',
                           thesub=thesub,
                           subcustomform=subcustomform,
                           subcustomform_thumbnail=subcustomform_thumbnail,
                           subcustom=subcustom
                           )


@mod.route('/customize/banner/<string:subname>', methods=['POST'])
@login_required
def customsub_bannerimage(subname):
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    subcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # custom header
        id_pic1 = id_generator_picture1()
        # mod customization

        if subcustom is None:
            newsubcustom = SubForumCustom(
                subcommon_name=thesub.subcommon_name,
                subcommon_id=thesub.id,
                banner_image='',
                mini_image='',
            )
            db.session.add(newsubcustom)
            db.session.commit()
            return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
        # form
        subcustomform = SubCustomForm(
            CombinedMultiDict((request.files, request.form)),
        )

        if subcustomform.delete.data and subcustomform.validate_on_submit():
            deletebannerimage(user_id=current_user.id, subid=thesub.id, image=subcustom.banner_image)
            subcustom.banner_image = ''
            db.session.add(subcustom)
            db.session.commit()
            flash("Banner Deleted", category="success")
            return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))

        elif subcustomform.submit.data and subcustomform.validate_on_submit():
            getsubnodelocation = subforumnodelocation(x=thesub.id)
            sub_location = os.path.join(UPLOADED_FILES_DEST, current_disk, 'subforum', getsubnodelocation, str(thesub.id))

            if subcustomform.subbannerimage.data:
                # make a usr a directory
                mkdir_p(path=sub_location)
                try:
                    deletebannerimage(user_id=current_user.id, subid=thesub.id, image=subcustom.banner_image)
                except:
                    pass
                subcustom.banner_image = ''
                db.session.add(subcustom)
                db.session.commit()
                filename = secure_filename(subcustomform.subbannerimage.data.filename)
                # makes directory (generic location + auction number id as folder)
                # saves it to location
                subimagefilepath = os.path.join(sub_location, filename)
                subcustomform.subbannerimage.data.save(subimagefilepath)
                # RENAMING FILE
                # split file name and ending
                filenamenew, file_extension = os.path.splitext(subimagefilepath)
                # gets new 64 digit filename
                newfilename = id_pic1 + file_extension
                # puts new name with ending
                filenamenewfull = filenamenew + file_extension
                # gets aboslute path of new file
                newfilenamedestination = os.path.join(sub_location, newfilename)
                # renames file
                os.rename(filenamenewfull, newfilenamedestination)

                if subcustomform.subbannerimage.data.filename:
                    imagelocation = newfilenamedestination[5:]
                    # add profile to db
                    subcustom.banner_image = imagelocation
                else:
                    subcustom.banner_image = ""

                db.session.add(subcustom)
                db.session.commit()
                flash("Banner has been changed", category="success")
                return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
            else:
                flash("No Image uploaded", category="danger")
                return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
        else:
            flash("No Image uploaded", category="danger")
            return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))


@mod.route('/customize/thumbnail/<string:subname>', methods=['POST'])
@login_required
def customsub_thumbnail_image(subname):
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    subcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()

    # remove mod status
    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # custom header
        id_pic1 = id_generator_picture1()
        # mod customization

        if subcustom is None:
            newsubcustom = SubForumCustom(
                subcommon_name=thesub.subcommon_name,
                subcommon_id=thesub.id,
                banner_image='',
                mini_image='',
            )
            db.session.add(newsubcustom)
            db.session.commit()
            return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
        # form
        subcustomform_thumbnail = SubCustomThumbnailForm(
            CombinedMultiDict((request.files, request.form)),
        )

        if request.method == 'POST':

            if subcustomform_thumbnail.delete.data and subcustomform_thumbnail.validate_on_submit():
                deletethumbnailimage(user_id=current_user.id, subid=thesub.id, image=subcustom.mini_image)
                subcustom.mini_image = ''
                thesub.mini_image = ''

                db.session.add(subcustom)
                db.session.commit()
                flash("Deleted image", category="success")
                return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
            elif subcustomform_thumbnail.submit.data and subcustomform_thumbnail.validate_on_submit():
                getsubnodelocation = subforumnodelocation(x=thesub.id)
                sub_location = os.path.join(UPLOADED_FILES_DEST, current_disk, 'subforum', getsubnodelocation, str(thesub.id))
                if subcustomform_thumbnail.subthumbnailimage.data:

                    # make a user a directory
                    mkdir_p(path=sub_location)
                    try:
                        deletethumbnailimage(user_id=current_user.id, subid=thesub.id, image=subcustom.mini_image)
                    except:
                        pass

                    subcustom.mini_image = ''
                    thesub.mini_image = ''
                    db.session.add(subcustom)
                    db.session.commit()
                    filename = secure_filename(subcustomform_thumbnail.subthumbnailimage.data.filename)
                    # saves it to location
                    subimagefilepath = os.path.join(sub_location, filename)
                    subcustomform_thumbnail.subthumbnailimage.data.save(subimagefilepath)
                    # RENAMING FILE
                    # split file name and ending
                    filenamenew, file_extension = os.path.splitext(subimagefilepath)
                    # gets new 64 digit filename
                    newfilename = id_pic1 + file_extension
                    # puts new name with ending
                    filenamenewfull = filenamenew + file_extension
                    # gets aboslute path of new file
                    newfilenamedestination = os.path.join(sub_location, newfilename)
                    # renames file
                    os.rename(filenamenewfull, newfilenamedestination)

                    if subcustomform_thumbnail.subthumbnailimage.data.filename:
                        thumbimage = convertimage(imagelocation=sub_location, imagename=newfilename)
                        subcustom.mini_image = thumbimage
                        thesub.mini_image = thumbimage

                    else:
                        subcustom.mini_image = ''
                        thesub.mini_image = ''

                    db.session.add(subcustom)
                    db.session.commit()

                    flash("Thumbnail Image has been changed", category="success")
                    return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
                else:
                    flash("No Image uploaded", category="danger")
                    return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))
            else:
                flash("No Image uploaded", category="danger")
                return redirect(url_for('mod.customsub_looks', subname=thesub.subcommon_name))


def deletebannerimage(user_id, subid, image):

    if current_user.id == user_id:
        getsubcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == int(subid)).first()

        str_image = str(image)
        file0 = os.path.join(UPLOADED_FILES_DEST, str_image)
        try:
            os.remove(file0)
        except Exception as e:
            return redirect(url_for('mod.customsub_looks', subname=getsubcustom.subcommon_name))

    else:
        return redirect(url_for('index'))


def deletethumbnailimage(user_id, subid, image):
    if current_user.id == user_id:
        getsubcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == int(subid)).first()

        str_image = str(image)

        file0 = os.path.join(UPLOADED_FILES_DEST, str_image)
        try:
            os.remove(file0)
        except Exception as e:
            return redirect(url_for('mod.customsub_looks', subname=getsubcustom.subcommon_name))

    else:
        return redirect(url_for('index'))


@mod.route('/mods/<string:subname>', methods=['GET'])
@login_required
def modbanoradd_main(subname):

    # forms
    addmodform = AddModForm()
    removemodform = RemoveModForm()

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    mods = db.session.query(Mods).filter(Mods.subcommon_id == thesub.id).all()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/modbanoradd_main.html',
                           addmodform=addmodform,
                           removemodform=removemodform,
                           mods=mods,
                           thesub=thesub
                           )


@mod.route('/mods/moduser/<string:subname>', methods=['POST'])
@login_required
def modadduser(subname):
    addmodform = AddModForm()
    removemodform = RemoveModForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    # add a user to the sub
    if request.method == 'POST':

        # see if user_name exists
        getuser = db.session.query(User).filter(User.user_name == addmodform.user_name.data).first()
        if getuser is None:
            flash("User Does not Exist.", category="danger")
            return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))
        else:
            # see if user is a mod
            seeifuserismod = db.session.query(Mods)
            seeifuserismod = seeifuserismod.filter(Mods.subcommon_id == thesub.id,
                                                   Mods.user_id == getuser.id)
            seeifuserismod = seeifuserismod.first()
            # see if user is an owner
            seeifuserowner = db.session.query(SubForums)
            seeifuserowner = seeifuserowner.filter(SubForums.subcommon_name == subname,
                                                   SubForums.creator_user_id == getuser.id)
            seeifuserowner = seeifuserowner.first()

            if seeifuserismod is None and seeifuserowner is None:
                addnewmod = Mods(
                    user_id=getuser.id,
                    user_name=getuser.user_name,
                    subcommon_id=thesub.id
                )
                add_new_notification(user_id=getuser.id,
                                     subid=thesub.id,
                                     subname=thesub.subcommon_name,
                                     postid=0,
                                     commentid=0,
                                     msg=6
                                     )
                db.session.add(addnewmod)
                db.session.commit()

                flash("User is now a mod.", category="success")
                return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))
            else:
                flash("User is already a mod.", category="danger")
                return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))

    return render_template('mod/modbanoradd_main.html',
                           addmodform=addmodform,
                           removemodform=removemodform,
                           )


@mod.route('/mods/unmoduser/<string:subname>', methods=['POST'])
@login_required
def modremoveuser(subname):
    addmodform = AddModForm()
    removemodform = RemoveModForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    # remove mod status
    if request.method == 'POST':

        # see if user_name exists
        getuser = db.session.query(User).filter(User.user_name == addmodform.user_name.data).first()
        if getuser is None:
            flash("User Does not Exist.", category="danger")
            return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))
        else:
            # see if user is a mod.
            seeifuserismod = db.session.query(Mods)
            seeifuserismod = seeifuserismod.filter(Mods.subcommon_id == thesub.id,
                                                   Mods.user_id == getuser.id)
            seeifuserismod = seeifuserismod.first()
            # see if user is an owner
            seeifuserowner = db.session.query(SubForums)
            seeifuserowner = seeifuserowner.filter(SubForums.subcommon_name == subname,
                                                   SubForums.creator_user_id == getuser.id)
            seeifuserowner = seeifuserowner.first()

            # only allow if user is a mod and not the owner
            if seeifuserismod is not None and seeifuserowner is None:
                add_new_notification(user_id=getuser.id,
                                     subid=thesub.id,
                                     subname=thesub.subcommon_name,
                                     postid=0,
                                     commentid=0,
                                     msg=7
                                     )

                db.session.delete(seeifuserismod)
                db.session.commit()

                flash("User mod status removed.", category="danger")
                return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))
            else:
                flash("User mod status cannot be removed.  May already be removed or an owner.", category="danger")
                return redirect(url_for('mod.modbanoradd_main', subname=thesub.subcommon_name))

    return render_template('mod/modbanoradd_main.html',
                           addmodform=addmodform,
                           removemodform=removemodform,
                           )


# -------------------------------------------------------------------------------------------
@mod.route('/users/<string:subname>', methods=['GET'])
@login_required
def modbanoradduser_main(subname):

    banuserform = BanUserModForm()
    removebanneduserform = UnBanUserModForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    bannedusers = db.session.query(Banned).filter(Banned.subcommon_id == thesub.id).all()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/userbanorunban_main.html',
                           banuserform=banuserform,
                           removebanneduserform=removebanneduserform,
                           thesub=thesub,
                           bannedusers=bannedusers
                           )


@mod.route('/users/banuser/<string:subname>/', methods=['POST'])
@login_required
def banuser(subname):

    # forms
    banuserform = BanUserModForm()
    removebanneduserform = UnBanUserModForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    if request.method == 'POST':
        # get user by form name
        getuser = db.session.query(User).filter(User.user_name == banuserform.user_name.data).first()
        if getuser is None:
            flash("User does not exist.", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        # see if already banned
        banneduser = db.session.query(Banned).filter(Banned.user_id == getuser.id,
                                                     Banned.subcommon_id == thesub.id).first()
        # if not ban that user
        if banneduser is not None:
            flash("User is already banned.", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        # add user to banned list
        addbanhammer = Banned(
            user_id=getuser.id,
            user_name=getuser.user_name,
            subcommon_id=thesub.id
        )
        add_new_notification(user_id=getuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=12
                             )
        db.session.add(addbanhammer)
        db.session.commit()
        flash("User is banned.", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return render_template('mod/userbanorunban_main.html',
                           banuserform=banuserform,
                           removebanneduserform=removebanneduserform,
                           )


@mod.route('/users/unbanuser/<string:subname>', methods=['POST'])
@login_required
def unbanuser(subname):

    # forms
    banuserform = BanUserModForm()
    removebanneduserform = UnBanUserModForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    if request.method == 'POST':
        # get user by form name
        getuser = db.session.query(User).filter(User.user_name == banuserform.user_name.data).first()
        if getuser is None:
            flash("User does not exist.", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        # see if already banned
        banneduser = db.session.query(Banned).filter(Banned.user_id == getuser.id,
                                                     Banned.subcommon_id == thesub.id).first()
        if banneduser is None:
            flash("This user is not banned", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        add_new_notification(user_id=getuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=8
                             )
        db.session.delete(banneduser)
        db.session.commit()
        flash("User Ban Status Removed", category="danger")
        return redirect((request.args.get('next', request.referrer)))

    return render_template('mod/userbanorunban_main.html',
                           removebanneduserform=removebanneduserform,
                           banuserform=banuserform,
                           )


@mod.route('/subinfo/<string:subname>', methods=['GET'])
@login_required
def changesub(subname):
    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    subdescriptionform = ChangeSubInfo(
        subcommondescription=thesub.description,
        typeofsub=thesub.type_of_subcommon,
        age=thesub.age_required,
        exprequiredtopost=thesub.exp_required,
        allowtextposts=thesub.allow_text_posts,
        allowurlposts=thesub.allow_url_posts,
        allowimageposts=thesub.allow_image_posts,
    )

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/changesubinfo.html',
                           subdescriptionform=subdescriptionform,
                           thesub=thesub
                           )


@mod.route('/changesubinfo/<string:subname>', methods=['POST'])
@login_required
def changesubinfo(subname):

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    subdescriptionform = ChangeSubInfo(

    )
    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    if request.method == 'POST':

        # type of subcommon
        subtype = subdescriptionform.typeofsub.data
        # 0 = Public
        # 1 = private
        # 2 = censored
        if subtype == '0':
            subtype = 0
        elif subtype == '1':
            subtype = 1
        elif subtype == '2':
            subtype = 2
        elif subtype == '3':
            subtype = 3
        else:
            subtype = 0

        # have an age requirement
        agereq = subdescriptionform.age.data
        # type of subcommon
        # 0 = No age requirement
        # 1 = Age Requirement
        if agereq is False:
            theage = 0
        else:
            theage = 1

        # allow text posts
        allowtextp = subdescriptionform.allowtextposts.data
        # type of subcommon
        # 0 = No age requirement
        # 1 = Age Requirement
        if allowtextp is False:
            allowtext = 0
        else:
            allowtext = 1

        # allow url posts
        allowurlp = subdescriptionform.allowurlposts.data
        # type of subcommon
        # 0 = No age requirement
        # 1 = Age Requirement
        if allowurlp is False:
            allowurl = 0
        else:
            allowurl = 1

        # allow image posts
        allowimagep = subdescriptionform.allowimageposts.data
        # type of subcommon
        # 0 = No age requirement
        # 1 = Age Requirement
        if allowimagep is False:
            allowimg = 0
        else:
            allowimg = 1

        thesub.description = subdescriptionform.subcommondescription.data
        thesub.exp_required = subdescriptionform.exprequiredtopost.data
        thesub.type_of_subcommon = subtype
        thesub.age_required = theage
        thesub.allow_text_posts = allowtext
        thesub.allow_url_posts = allowurl
        thesub.allow_image_posts = allowimg
        db.session.add(thesub)
        db.session.commit()

        flash("Sub Info Updated.", category="success")
        return redirect(url_for('mod.changesub', subname=thesub.subcommon_name))


@mod.route('/stats/<string:subname>', methods=['GET'])
@login_required
def substats(subname):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    thesubstats = db.session.query(SubForumStats).filter(SubForumStats.subcommon_id == thesub.id).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/substats/statshome.html',
                           thesub=thesub,
                           thesubstats=thesubstats
                           )


@mod.route('/quick/muteuser/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def quickmuteuser(subname, postid):
    now = datetime.utcnow()
    mute_twentyfour_hours = datetime.today() + timedelta(days=1)

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()
    theuser = db.session.query(User).filter(thepost.user_id == User.id).first()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        thepost.muted = 1
        add_new_notification(user_id=theuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=11
                             )
        addnewmute = Muted(
            user_id=theuser.id,
            user_name=theuser.user_name,
            subcommon_id=thesub.id,
            muted_start=now,
            muted_end=mute_twentyfour_hours
        )
        db.session.add(thepost)
        db.session.add(addnewmute)
        db.session.commit()
        flash("Muted User for 24 Hours", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return redirect((request.args.get('next', request.referrer)))


@mod.route('/quick/bananddelete/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def quickbanuserdeletepost(subname, postid):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()
    theuser = db.session.query(User).filter(thepost.user_id == User.id).first()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # add user to the ban post
        banthisuser = Banned(
            user_id=theuser.id,
            user_name=theuser.user_name,
            subcommon_id=thesub.id,
        )
        add_new_notification(user_id=theuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=12
                             )
        thepost.hidden = 1
        # add the ban
        db.session.add(banthisuser)
        # delete the post
        db.session.add(thepost)
        # commit to db
        db.session.commit()
        flash("Banned User/ Deleted Post", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return redirect((request.args.get('next', request.referrer)))


@mod.route('/quick/deletepost/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def quickdeletepost(subname, postid):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first_or_404()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        thepost.hidden = 1
        db.session.add(thepost)
        db.session.commit()
        flash("Deleted Post and comments", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return redirect((request.args.get('next', request.referrer)))


@mod.route('/quick/lockpost/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def quicklockpost(subname, postid):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first_or_404()
    theuser = db.session.query(User).filter(thepost.user_id == User.id).first_or_404()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # add info
        add_new_notification(user_id=theuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=thepost.id,
                             commentid=0,
                             msg=13
                             )
        thepost.locked = 1
        # commit to db
        db.session.add(thepost)
        db.session.commit()
        flash("Locked Post. No comments or votes allowed.", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return redirect((request.args.get('next', request.referrer)))


@mod.route('/quick/nsfwpost/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def quicknsfwpost(subname, postid):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()

    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        thepost.age = 1
        # commit to db
        db.session.add(thepost)
        db.session.commit()
        flash("Post is now NSFW Post.", category="success")
        return redirect((request.args.get('next', request.referrer)))

    return redirect((request.args.get('next', request.referrer)))


@mod.route('/private/viewmembers/<string:subname>', methods=['GET'])
def viewprivatemembers(subname):

    # get subs user belongs too
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()

    page = request.args.get('page', 1, type=int)
    # Get Members
    privatemembers = db.session.query(PrivateMembers)
    privatemembers = privatemembers.filter(PrivateMembers.subcommon_id == thesub.id)
    privatemembers = privatemembers.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('mod.viewprivatemembers', page=privatemembers.next_num) \
        if privatemembers.has_next else None
    prev_url = url_for('mod.viewprivatemembers', page=privatemembers.prev_num) \
        if privatemembers.has_prev else None

    return render_template('mod/private_viewusers.html',

                           thesub=thesub,
                           privatemembers=privatemembers.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@mod.route('/private/remove/<string:subname>', methods=['GET'])
def removeusersprivate(subname):

    removeuserform = RemoveUserForm()
    # get subs user belongs too
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    privatemembers = db.session.query(PrivateMembers)
    privatemembers = privatemembers.filter(PrivateMembers.subcommon_id == thesub.id)
    privatemembers = privatemembers.limit(25)

    return render_template('mod/private_removeusers.html',

                           removeuserform=removeuserform,
                           thesub=thesub,
                           privatemembers=privatemembers)


# this page is utilized if the user is banned from the sub, or
@mod.route('/private/viewapplications/<string:subname>', methods=['GET'])
def viewprivateapplications(subname):
    acceptuserform = AcceptUserForm()
    acceptspecificuserform = AcceptSpecificUserForm()
    # get subs user belongs too
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    applications = db.session.query(PrivateApplications).filter(PrivateApplications.subcommon_id == thesub.id).all()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/private_applications.html',
                           acceptuserform=acceptuserform,
                           acceptspecificuserform=acceptspecificuserform,

                           thesub=thesub,
                           applications=applications)


# this page is utilized if the user is banned from the sub, or
@mod.route('/private/accept/<string:subname>/<int:user_id>', methods=['POST'])
def acceptpersontoprivate(user_id, subname):

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    # get sub apply too
    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get user application
        userapp = db.session.query(PrivateApplications)
        userapp = userapp.filter(PrivateApplications.user_id == user_id)
        userapp = userapp.filter(PrivateApplications.subcommon_id == thesub.id)
        userapp = userapp.first_or_404()

        # add user to list of private members of sub
        addusertoprivate = PrivateMembers(
            user_id=userapp.user_id,
            user_name=userapp.user_name,
            subcommon_id=thesub.id,
        )
        add_new_notification(user_id=userapp.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=9
                             )
        # delete user application/ add to db
        db.session.add(addusertoprivate)
        db.session.delete(userapp)
        db.session.commit()

        flash("User added to sub", category="danger")
        return redirect((request.args.get('next', request.referrer)))



# this page is utilized if the user is banned from the sub, or
@mod.route('/private/accept/<string:subname>', methods=['POST'])
def acceptpersontoprivatespecific(subname):
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()
    # get sub apply too
    acceptspecificuserform = AcceptSpecificUserForm()
    if request.method == 'POST':

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        seeifuserfromformexists = db.session.query(User)
        seeifuserfromformexists = seeifuserfromformexists.filter(User.user_name == acceptspecificuserform.user_name.data)
        seeifuserfromformexists = seeifuserfromformexists.first_or_404()
        # add user to list of private members of sub
        addusertoprivate = PrivateMembers(
            user_id=seeifuserfromformexists.id,
            user_name=seeifuserfromformexists.user_name,
            subcommon_id=thesub.id,
        )
        add_new_notification(user_id=seeifuserfromformexists.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=9
                             )
        # delete user application/ add to db
        db.session.add(addusertoprivate)
        db.session.commit()

        flash("User added to sub", category="danger")
        return redirect((request.args.get('next', request.referrer)))



@mod.route('/private/uninviteuser/<string:subname>', methods=['POST'])
@login_required
def removeuser(subname):

    removeuserform = RemoveUserForm()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    if thesub.type_of_subcommon != 1:
        flash("This feature is only for private subs.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    if request.method == 'POST':
        getuser = db.session.query(User).filter(User.user_name == removeuserform.user_name.data).first()
        if getuser is not None:
            # see if user is already added
            getprivmember = db.session.query(PrivateMembers)
            getprivmember = getprivmember.filter(PrivateMembers.user_name == getuser.user_name)
            getprivmember = getprivmember.filter(PrivateMembers.subcommon_id == thesub.id)
            getprivmember = getprivmember.first()
            # see if user is a mod
            seeifuserismod = db.session.query(Mods)
            seeifuserismod = seeifuserismod.filter(Mods.subcommon_id == thesub.id,
                                                   Mods.user_id == getuser.id)
            seeifuserismod = seeifuserismod.first()
            # see if user is an owner
            seeifuserowner = db.session.query(SubForums)
            seeifuserowner = seeifuserowner.filter(SubForums.subcommon_name == subname,
                                                   SubForums.creator_user_id == getuser.id)
            seeifuserowner = seeifuserowner.first()
            if getprivmember is not None:
                if seeifuserismod is None and seeifuserowner is None:
                    add_new_notification(user_id=getuser.id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=0,
                                         commentid=0,
                                         msg=10
                                         )
                    db.session.delete(getprivmember)
                    db.session.commit()
                    flash("Removed User", category="success")
                    return redirect(url_for('mod.inviteoruninvite_main', subname=thesub.subcommon_name))
                else:
                    flash("Cannot remove this user", category="danger")
                    return redirect(url_for('mod.inviteoruninvite_main', subname=thesub.subcommon_name))
            else:
                flash("This user is not a member", category="danger")
                return redirect(url_for('mod.inviteoruninvite_main', subname=thesub.subcommon_name))
        else:
            flash("User does not exist", category="danger")
            return redirect(url_for('mod.inviteoruninvite_main', subname=thesub.subcommon_name))


# ---------------------------------------------------------------------------------------------
##
# Reported Posts
##
@mod.route('/reported/posts/<string:subname>', methods=['GET'])
@login_required
def viewreportedposts(subname):

    deletepostform = QuickDelete()
    deletepostbanuserform = QuickBanDelete()
    unreport = UnReport()
    voteform = VoteForm()
    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    page = request.args.get('page', 1, type=int)

    reportedposts = db.session.query(CommonsPost)
    reportedposts = reportedposts.join(ReportedPosts, (CommonsPost.id == ReportedPosts.post_id))
    reportedposts = reportedposts.filter(ReportedPosts.subcommon_id == thesub.id)
    reportedposts = reportedposts.order_by(ReportedPosts.created.desc())
    reportedposts = reportedposts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('mod.viewreportedposts', page=reportedposts.next_num) \
        if reportedposts.has_next else None
    prev_url = url_for('mod.viewreportedposts', page=reportedposts.prev_num) \
        if reportedposts.has_prev else None

    return render_template('mod/viewreportedposts.html',
                           deletepostform=deletepostform,
                           thesub=thesub,
                           voteform=voteform,
                           deletepostbanuserform=deletepostbanuserform,
                           unreport=unreport,
                           reportedposts=reportedposts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@mod.route('/reported/posts/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def reportpost(postid, subname):
    now = datetime.utcnow()
    if request.method == 'POST':
        # SPAM CHECKS
        # timer, timeleft
        seeiftimerallowed, timeleft = lastreport(user_id=current_user.id)
        # if there isnt enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " seconds before creating another report", category="info")
            return redirect((request.args.get('next', request.referrer)))
        else:
            thepost = db.session.query(CommonsPost)
            thepost = thepost.filter(CommonsPost.id == postid)
            thepost = thepost.first()

            createnewreport = ReportedPosts(
                created=now,
                reporter_id=current_user.id,
                reporter_user_name=current_user.user_name,
                subcommon_id=thepost.subcommon_id,
                subcommon_name=thepost.subcommon_name,
                post_id=thepost.id,

                poster_user_id=thepost.user_id,
                poster_user_name=thepost.user_name,
                poster_visible_user_id=thepost.visible_user_id,
                poster_visible_user_name=thepost.visible_user_name
            )
            # reset users timer
            getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
            getuser_timers.last_report = now
            db.session.add(getuser_timers)
            db.session.add(createnewreport)
            db.session.commit()

            flash("Post has been reported", category="danger")
            return redirect(url_for('subforum.sub', subname=subname))


@mod.route('/reported/posts/delete/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def deletereportedposts(subname, postid):

    if request.method == 'POST':
        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get the report itself
        reportedpost = db.session.query(ReportedPosts)
        reportedpost = reportedpost.filter(ReportedPosts.subcommon_name == subname)
        reportedpost = reportedpost.filter(ReportedPosts.post_id == postid)
        reportedpost = reportedpost.first()

        # get the post that was reported
        thepost = db.session.query(CommonsPost)
        thepost = thepost.filter(CommonsPost.id == reportedpost.post_id)
        thepost = thepost.first()

        thepost.hidden = 1

        db.session.add(thepost)
        db.session.delete(reportedpost)
        db.session.commit()

        flash("Post has been deleted", category="danger")
        return redirect(url_for('mod.viewreportedposts', subname=subname))


@mod.route('/reported/posts/delete/ban/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def deletereportedpostsandbanuser(subname, postid):
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    if request.method == 'POST':
        # get the report itself
        reportedpost = db.session.query(ReportedPosts)
        reportedpost = reportedpost.filter(ReportedPosts.subcommon_name == subname)
        reportedpost = reportedpost.filter(ReportedPosts.post_id == postid)
        reportedpost = reportedpost.first()

        # get the post that was reported
        thepost = db.session.query(CommonsPost)
        thepost = thepost.filter(CommonsPost.id == reportedpost.post_id)
        thepost = thepost.first()

        # mod security
        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get user by form name
        getuser = db.session.query(User).filter(User.user_name == thepost.user_name).first()
        if getuser is None:
            flash("User does not exist", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        # see if already banned
        banneduser = db.session.query(Banned).filter(Banned.user_id == getuser.id,
                                                     Banned.subcommon_id == thesub.id).first()
        # if not ban that user
        if banneduser is not None:

            flash("User Banned already", category="danger")
            return redirect((request.args.get('next', request.referrer)))

        # add user to banned list
        addbanhammer = Banned(
            user_id=getuser.id,
            user_name=getuser.user_name,
            subcommon_id=thesub.id
        )
        add_new_notification(user_id=getuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=12
                             )
        db.session.add(addbanhammer)

        thepost.hidden = 1

        db.session.add(thepost)
        db.session.delete(reportedpost)
        db.session.commit()

        flash("Post has been deleted. User Banned", category="danger")
        return redirect(url_for('mod.viewreportedposts', subname=subname))


@mod.route('/reported/posts/unreport/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def unreportposts(subname, postid):

    if request.method == 'POST':
        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get the report itself
        reportedpost = db.session.query(ReportedPosts)
        reportedpost = reportedpost.filter(ReportedPosts.subcommon_name == subname)
        reportedpost = reportedpost.filter(ReportedPosts.post_id == postid)
        reportedpost = reportedpost.first()

        db.session.delete(reportedpost)
        db.session.commit()

        flash("Report Removed", category="danger")
        return redirect(url_for('mod.viewreportedposts', subname=subname))


# ---------------------------------------------------------------------------------------------
##
# Reported Comments
##
@mod.route('/reported/comments/<string:subname>', methods=['GET'])
@login_required
def viewreportedcomments(subname):

    deletepostform = QuickDelete()
    deletepostbanuserform = QuickBanDelete()
    unreport = UnReport()

    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    page = request.args.get('page', 1, type=int)
    reportedcomments = db.session.query(ReportedComments)
    reportedcomments = reportedcomments.filter(ReportedComments.subcommon_name == subname)
    reportedcomments = reportedcomments.order_by(ReportedComments.created.desc())
    reportedcomments = reportedcomments.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('mod.viewreportedcomments', page=reportedcomments.next_num) \
        if reportedcomments.has_next else None
    prev_url = url_for('mod.viewreportedcomments', page=reportedcomments.prev_num) \
        if reportedcomments.has_prev else None

    return render_template('mod/viewreprtedcomments.html',
                           deletepostform=deletepostform,
                           deletepostbanuserform=deletepostbanuserform,
                           unreport=unreport,
                           thesub=thesub,
                           # pagination
                           reportedcomments=reportedcomments.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           )


@mod.route('/reported/comments/<string:subname>/<int:postid>/<int:commentid>', methods=['POST', 'GET'])
@login_required
def reportcomment(commentid, subname, postid):
    now = datetime.utcnow()
    if request.method == 'GET':
        seeiftimerallowed, timeleft = lastreport(user_id=current_user.id)
        # if there isnt enough time
        if seeiftimerallowed == 0:
            flash("Please wait " + str(timeleft) + " seconds before creating another report", category="info")
            return redirect((request.args.get('next', request.referrer)))
        else:

            thecomment = db.session.query(Comments)
            thecomment = thecomment.filter(Comments.id == commentid)
            thecomment = thecomment.first()

            createnewreport = ReportedComments(
                created=now,
                reporter_id=current_user.id,
                reporter_user_name=current_user.user_name,
                subcommon_id=thecomment.subcommon_id,
                subcommon_name=subname,
                comment_id=thecomment.id,
                comment_body=thecomment.body_clean,
                commenter_user_id=thecomment.user_id,
                commenter_user_name=thecomment.user_name,
                commenter_visible_user_id=thecomment.visible_user_id,
                commenter_visible_user_name=thecomment.visible_user_name
            )
            # reset users timer
            getuser_timers = db.session.query(UserTimers).filter_by(user_id=current_user.id).first()
            getuser_timers.last_report = now
            db.session.add(getuser_timers)
            db.session.add(createnewreport)
            db.session.commit()

            flash("Comment has been reported", category="danger")
            return redirect(url_for('subforum.viewpost', subname=subname, postid=postid))


@mod.route('/reported/comments/delete/<string:subname>/<int:commentid>', methods=['POST'])
@login_required
def deletereportedcomment(subname, commentid):

    if request.method == 'POST':
        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get the report itself
        reportedcomment = db.session.query(ReportedComments)
        reportedcomment = reportedcomment.filter(ReportedComments.subcommon_name == subname)
        reportedcomment = reportedcomment.filter(ReportedComments.id == commentid)
        reportedcomment = reportedcomment.first()

        # get the comment that was reported
        thecomment = db.session.query(Comments)
        thecomment = thecomment.filter(Comments.id == reportedcomment.comment_id)
        thecomment = thecomment.first()

        thecomment.hidden = 1

        db.session.add(thecomment)
        db.session.delete(reportedcomment)
        db.session.commit()

        flash("Comment has been deleted", category="danger")
        return redirect(url_for('mod.viewreportedcomments', subname=subname))


@mod.route('/reported/comments/delete/ban/<string:subname>/<int:commentid>', methods=['POST'])
@login_required
def deletereportedcommentsandbanuser(subname, commentid):

    if request.method == 'POST':

        # get the report itself
        reportedcomment = db.session.query(ReportedComments)
        reportedcomment = reportedcomment.filter(ReportedComments.subcommon_name == subname)
        reportedcomment = reportedcomment.filter(ReportedComments.id == commentid)
        reportedcomment = reportedcomment.first()

        # get the comment that was reported
        thecomment = db.session.query(Comments)
        thecomment = thecomment.filter(Comments.id == reportedcomment.comment_id)
        thecomment = thecomment.first()

        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get user by form name
        getuser = db.session.query(User).filter(User.user_name == thecomment.user_name).first()
        if getuser is None:
            flash("User doesnt exist.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # see if already banned
        banneduser = db.session.query(Banned).filter(Banned.user_id == getuser.id,
                                                     Banned.subcommon_id == thesub.id).first()
        # if not ban that user
        if banneduser is not None:
            flash("User Banned already", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # add user to banned list
        addbanhammer = Banned(
            user_id=getuser.id,
            user_name=getuser.user_name,
            subcommon_id=thesub.id
        )

        add_new_notification(user_id=getuser.id,
                             subid=thesub.id,
                             subname=thesub.subcommon_name,
                             postid=0,
                             commentid=0,
                             msg=12
                             )

        db.session.add(addbanhammer)
        thecomment.hidden = 1

        db.session.add(thecomment)
        db.session.delete(reportedcomment)
        db.session.commit()

        flash("Comment has been deleted. User Banned", category="danger")
        return redirect((request.args.get('next', request.referrer)))


@mod.route('/reported/comments/unreport/<string:subname>/<int:commentid>', methods=['POST'])
@login_required
def unreportcomment(subname, commentid):
    if request.method == 'POST':
        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        # get the report itself
        reportedcomment = db.session.query(ReportedComments)
        reportedcomment = reportedcomment.filter(ReportedComments.subcommon_name == subname)
        reportedcomment = reportedcomment.filter(ReportedComments.id == commentid)
        reportedcomment = reportedcomment.first()

        db.session.delete(reportedcomment)
        db.session.commit()

        flash("Report Removed", category="danger")
        return redirect((request.args.get('next', request.referrer)))


@mod.route('/subinfoboxone/<string:subname>', methods=['GET'])
@login_required
def subinfoboxmain(subname):
    # mod security
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    subinfobox = db.session.query(SubForumCustomInfoOne).filter(SubForumCustomInfoOne.subcommon_name == subname).first()
    if subinfobox is None:
        newsubbox = SubForumCustomInfoOne(
            subcommon_name=thesub.subcommon_name,
            subcommon_id=thesub.id,
            enabled=0,
            description=''
        )
        db.session.add(newsubbox)
        db.session.commit()
        return redirect(url_for('mod.subinfoboxmain', subname=thesub.subcommon_name))
    subinfoboxform = ChangeSubInfoBoxOne(
        description=subinfobox.description,
        enabled=subinfobox.enabled,
    )

    user_status = modcheck(thesub=thesub, theuser=current_user)
    if user_status == 0:
        flash("You are not a mod of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    return render_template('mod/changesubinfoboxone.html',
                           subinfoboxform=subinfoboxform,
                           thesub=thesub
                           )


@mod.route('/changesubinfoboxone/<string:subname>', methods=['POST'])
@login_required
def subinfoboxpost(subname):
    if request.method == 'POST':
        # mod security
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        subinfobox = db.session.query(SubForumCustomInfoOne).filter(SubForumCustomInfoOne.subcommon_name == subname).first()
        subinfoboxform = ChangeSubInfoBoxOne()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        enab = subinfoboxform.enabled.data
        if enab is False:
            enabledcheck = 0
        else:
            enabledcheck = 1

        subinfobox.description = subinfoboxform.description.data
        subinfobox.enabled = enabledcheck

        db.session.add(subinfobox)
        db.session.commit()

        flash("Sub Info Updated.", category="success")
        return redirect(url_for('mod.subinfoboxmain', subname=thesub.subcommon_name))


@mod.route('/sticky/<int:subid>/<int:postid>', methods=['POST'])
@login_required
def stickypost(subid, postid):
    if request.method == 'POST':
        # get amount of sticky posts
        getstickiescount = db.session.query(CommonsPost).filter(CommonsPost.subcommon_id == subid,
                                                                CommonsPost.sticky == 1).count()
        if getstickiescount >= 2:
            flash("Only 2 posts can be stickied at a time.", category="success")
            return redirect((request.args.get('next', request.referrer)))

        thesub = db.session.query(SubForums).filter(SubForums.id == subid).first()
        thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        thepost.sticky = 1
        db.session.add(thepost)
        db.session.commit()

        flash("Post Stickied", category="success")
        return redirect(url_for('subforum.viewpost',
                                subname=thesub.subcommon_name,
                                postid=thepost.id))


@mod.route('/unsticky/<int:subid>/<int:postid>', methods=['POST'])
@login_required
def unstickypost(subid, postid):
    if request.method == 'POST':
        # get amount of sticky posts
        thesub = db.session.query(SubForums).filter(SubForums.id == subid).first_or_404()
        thepost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first_or_404()

        user_status = modcheck(thesub=thesub, theuser=current_user)
        if user_status == 0:
            flash("You are not a mod of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        thepost.sticky = 0
        db.session.add(thepost)
        db.session.commit()

        flash("Post Unstickied", category="success")
        return redirect(url_for('subforum.viewpost',
                                subname=thesub.subcommon_name,
                                postid=thepost.id))


@mod.route('/owner/delete/<string:subname>', methods=['Get'])
@login_required
def ownerdeletesub(subname):
    deleteform = DeleteRoomForm()

    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first_or_404()

    # see if user is a creator
    seeifowner = db.session.query(SubForums)
    seeifowner = seeifowner.filter(SubForums.subcommon_name == subname,
                                   SubForums.creator_user_id == current_user.id)
    seeifowner = seeifowner.first()
    if seeifowner is None:
        # see if user is a mod

        flash("You are not the owner of this sub.", category="danger")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

    # add a user to the sub

    return render_template('mod/deletesub.html',
                           deleteform=deleteform,
                           thesub=thesub
                           )


@mod.route('/owner/delete/<string:subname>', methods=['POST'])
@login_required
def ownerdeletesubconfirm(subname):

    if request.method == 'POST':
        deleteform = DeleteRoomForm()

        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        if thesub is None:
            flash("Sub not found.  Did you spell it correctly?", category="danger")
            return redirect((request.args.get('next', request.referrer)))
        subcustom = db.session.query(SubForumCustom).filter(SubForumCustom.subcommon_id == thesub.id).first()
        # see if user is a creator
        seeifowner = db.session.query(SubForums)
        seeifowner = seeifowner.filter(SubForums.subcommon_name == subname,
                                       SubForums.creator_user_id == current_user.id)
        seeifowner = seeifowner.first()
        if seeifowner is None:
            # see if user is a mod

            flash("You are not the owner of this sub.", category="danger")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))

        if deleteform.sub_name.data == str(subname):

            # mark as deleted .. not actually deleted incase need to look at in future
            thesub.room_deleted = 1
            deletethumbnailimage(user_id=current_user.id, subid=thesub.id, image=subcustom.mini_image)
            deletebannerimage(user_id=current_user.id, subid=thesub.id, image=subcustom.banner_image)
            db.session.add(thesub)

            # delete all subscriptions
            getallsubs = db.session.query(Subscribed).filter(Subscribed.subcommon_id == thesub.id).all()
            for f in getallsubs:
                db.session.delete(f)

            db.session.commit()
            flash("SUBFORUM HAS BEEN DELETED.", category="danger")
            return redirect(url_for('index'))

    if request.method == 'GET':
        return redirect(url_for('index'))