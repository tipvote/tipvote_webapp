import os

from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash
from flask import request
from flask_login import\
    current_user
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from app import db
from app import UPLOADED_FILES_DEST
from app.nodelocations import userimagelocation, current_disk
from app.common.functions import mkdir_p
from app.common.functions import id_generator_picture1
from app.common.decorators import login_required

from app.profile_photos import photos
from app.profile_photos.forms import\
    ProfilePicForm,\
    BannerPicForm
from app.classes.user import User
from app.profile_photos.resize_banner import convert_banner_image
from app.profile_photos.resize_profile import convert_profile_image

def deleteuserprofileimage(user_id):
    if current_user.id == user_id:
        user = db.session.query(User).filter(User.id == user_id).first()
        file0 = os.path.join(UPLOADED_FILES_DEST, user.profileimage)
        try:
            os.remove(file0)
        except Exception as e:
            pass
        user.profileimage = ''
        db.session.add(user)
        db.session.commit()
    else:
        return redirect(url_for('index'))

def deleteuserbannerimage(user_id):
    if current_user.id == user_id:
        user = db.session.query(User).filter(User.id == user_id).first()
        file0 = os.path.join(UPLOADED_FILES_DEST, user.bannerimage)
        try:
            os.remove(file0)
        except Exception as e:
            pass
        user.bannerimage = ''
        db.session.add(user)
        db.session.commit()
    else:
        return redirect(url_for('index'))


@photos.route('/profilepic', methods=['GET', 'POST'])
@login_required
def profilepicture():

    id_pic1 = id_generator_picture1()

    form = ProfilePicForm(
        CombinedMultiDict((request.files, request.form)),
    )
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':

        if form.delete.data and form.validate_on_submit():
            deleteuserprofileimage(user_id=user.id)
            return redirect((request.args.get('next', request.referrer)))

        if form.submit.data and form.validate_on_submit():

            getusernodelocation = userimagelocation(x=user.id)
            userlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, 'user', getusernodelocation, str(user.id))

            if form.imageprofile.data:
                try:
                    mkdir_p(path=userlocation)
                    deleteuserprofileimage(user_id=current_user.id)
                    filename = secure_filename(form.imageprofile.data.filename)
                    # makes directory (generic location + auction number id as folder)
                    # saves it to location
                    profileimagefilepath = os.path.join(userlocation, filename)
                    form.imageprofile.data.save(profileimagefilepath)
                    # RENAMING FILE
                    # split file name and ending
                    filenamenew, file_extension = os.path.splitext(profileimagefilepath)
                    # gets new 64 digit filename
                    newfilename = id_pic1 + file_extension
                    # puts new name with ending
                    filenamenewfull = filenamenew + file_extension
                    # gets aboslute path of new file
                    newfilenamedestination = os.path.join(userlocation, newfilename)
                    # renames file
                    os.rename(filenamenewfull, newfilenamedestination)
                    convert_profile_image(imagelocation=userlocation, imagename=newfilename)
                except Exception as e:
                    user.profileimage = "0"
                    flash("Error", category="success")
                    return redirect((request.args.get('next', request.referrer)))
                if not form.imageprofile.data.filename:

                    user.profileimage = ""

                db.session.add(user)
                db.session.commit()
                flash("Profile has been changed", category="success")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash("Error.  No data submitted", category="danger")
            return redirect((request.args.get('next', request.referrer)))

    return render_template('users/profile/profile_forms/profile_picture.html',
                           form=form,
                           user=user,
                           )


@photos.route('/bannerpic', methods=['GET', 'POST'])
@login_required
def bannerpicture():

    id_pic1 = id_generator_picture1()

    form = BannerPicForm(
        CombinedMultiDict((request.files, request.form)),
    )
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        if form.delete.data and form.validate_on_submit():
            deleteuserbannerimage(user_id=user.id)
            return redirect((request.args.get('next', request.referrer)))

        if form.submit.data and form.validate_on_submit():
            getusernodelocation = userimagelocation(x=user.id)
            userlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, 'user', getusernodelocation, str(user.id))

            if form.imageprofile.data:
                try:
                    # make a user a directory
                    mkdir_p(path=userlocation)
                    deleteuserbannerimage(user_id=current_user.id)
                    filename = secure_filename(form.imageprofile.data.filename)
                    # makes directory (generic location + auction number id as folder)
                    # saves it to location
                    profileimagefilepath = os.path.join(userlocation, filename)
                    form.imageprofile.data.save(profileimagefilepath)
                    # RENAMING FILE
                    # split file name and ending
                    filenamenew, file_extension = os.path.splitext(profileimagefilepath)
                    # gets new 64 digit filename
                    newfilename = id_pic1 + file_extension
                    # puts new name with ending
                    filenamenewfull = filenamenew + file_extension
                    # gets aboslute path of new file
                    newfilenamedestination = os.path.join(userlocation, newfilename)
                    # renames file
                    os.rename(filenamenewfull, newfilenamedestination)
                    convert_banner_image(imagelocation=userlocation, imagename=newfilename)

                except Exception as e:
                    user.bannerimage = ""
                    flash("Error", category="success")
                    return redirect((request.args.get('next', request.referrer)))

                if not form.imageprofile.data.filename:
                    user.bannerimage = ''

                db.session.add(user)
                db.session.commit()
                flash("Profile banner has been changed", category="success")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash("Error. No data submitted", category="danger")
            return redirect((request.args.get('next', request.referrer)))

    return render_template('users/profile/profile_forms/profile_banner.html',
                           form=form,
                           user=user,
                           )
