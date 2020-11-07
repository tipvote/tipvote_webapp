import os
from flask import \
    render_template, \
    redirect, \
    url_for, \
    request, \
    flash
from flask_login import current_user
from app import db
from app import UPLOADED_FILES_DEST

from app.business_edit import business_edit

from app.common.decorators import login_required
from app.common.functions import mkdir_p


from app.business_edit.forms import \
    ProfilePicForm, \
    BannerPicForm, \
    MyAccountForm, \
    MyLocationForm, \
    DeleteRoomForm, \
    AcceptsCurrency,  UserBioForm

from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from app.common.functions import id_generator_picture1

from app.nodelocations import userimagelocation, current_disk
from app.business_edit.resize_banner import convert_banner_image
from app.business_edit.resize_profile import convert_profile_image

from app.classes.business import Business, \
    BusinessInfo, \
    BusinessFollowers, \
    BusinessStats, \
    BusinessLocation, \
    BusinessServices,\
    BusinessAccepts,\
    BusinessSpecificInfo
from app.classes.post import CommonsPost

def deleteprofileimage(business_id):
    thebiz = db.session.query(Business).filter(Business.id == business_id).first()
    if current_user.id == thebiz.user_id:

        file0 = os.path.join(UPLOADED_FILES_DEST, thebiz.profileimage)
        try:
            os.remove(file0)
        except Exception as e:
            pass
        thebiz.profileimage = ''
        db.session.add(thebiz)
        db.session.commit()
    else:
        return redirect(url_for('index'))


def deletebannerimage(business_id):
    thebiz = db.session.query(Business).filter(Business.id == business_id).first()
    if current_user.id == thebiz.user_id:

        file0 = os.path.join(UPLOADED_FILES_DEST, thebiz.bannerimage)
        try:
            os.remove(file0)
        except Exception as e:
            pass
        thebiz.bannerimage = ''
        db.session.add(thebiz)
        db.session.commit()
    else:
        return redirect(url_for('index'))


@business_edit.route('/<business_id>/profilepic', methods=['GET', 'POST'])
@login_required
def profilepicture(business_id):

    id_pic1 = id_generator_picture1()

    form = ProfilePicForm(
        CombinedMultiDict((request.files, request.form)),
    )
    thebiz = db.session.query(Business).filter(Business.id == business_id).first()
    if current_user.id != thebiz.user_id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if current_user.id != thebiz.user_id:
            return redirect(url_for('index'))
        if form.delete.data and form.validate_on_submit():
            deleteprofileimage(business_id=thebiz.id)
            return redirect((request.args.get('next', request.referrer)))

        if form.submit.data and form.validate_on_submit():

            getusernodelocation = userimagelocation(x=thebiz.id)
            userlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, 'business', getusernodelocation, str(thebiz.id))

            if form.imageprofile.data:
                try:
                    mkdir_p(path=userlocation)
                    deleteprofileimage(business_id=thebiz.id)
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
                    convert_profile_image(imagelocation=userlocation, imagename=newfilename, business_id=thebiz.id)
                except Exception as e:
                    thebiz.profileimage = "0"
                    flash("Error", category="success")
                    return redirect((request.args.get('next', request.referrer)))
                if not form.imageprofile.data.filename:

                    thebiz.profileimage = "0"

                db.session.add(thebiz)
                db.session.commit()
                flash("Profile Image  has been changed", category="success")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash("Error.  No data submitted", category="danger")
            return redirect((request.args.get('next', request.referrer)))

    return render_template('business/edit/images/profile_picture.html',
                           form=form,
                           thebiz=thebiz,
                           )


@business_edit.route('/<business_id>/bannerpic', methods=['GET', 'POST'])
@login_required
def bannerpicture(business_id):

    id_pic1 = id_generator_picture1()

    form = BannerPicForm(
        CombinedMultiDict((request.files, request.form)),
    )
    thebiz = db.session.query(Business).filter(Business.id == business_id).first()
    if current_user.id != thebiz.user_id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if current_user.id != thebiz.user_id:
            return redirect(url_for('index'))
        if form.delete.data and form.validate_on_submit():
            deletebannerimage(business_id=thebiz.id)
            return redirect((request.args.get('next', request.referrer)))

        if form.submit.data and form.validate_on_submit():
            getusernodelocation = userimagelocation(x=thebiz.id)
            userlocation = os.path.join(UPLOADED_FILES_DEST, current_disk, 'business', getusernodelocation, str(thebiz.id))

            if form.imageprofile.data:
                try:
                    # make a user a directory
                    mkdir_p(path=userlocation)
                    deletebannerimage(business_id=thebiz.id)
                    filename = secure_filename(form.imageprofile.data.filename)
                    # makes directory (generic location + auction number id as folder)
                    profileimagefilepath = os.path.join(userlocation, filename)
                    # saves it to location
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
                    convert_banner_image(imagelocation=userlocation, imagename=newfilename, business_id=thebiz.id)

                except Exception as e:
                    thebiz.bannerimage = ""
                    flash("Error", category="success")
                    return redirect((request.args.get('next', request.referrer)))

                if not form.imageprofile.data.filename:
                    thebiz.bannerimage = ''

                db.session.add(thebiz)
                db.session.commit()
                flash("Profile banner has been changed", category="success")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash("Error. No data submitted", category="danger")
            return redirect((request.args.get('next', request.referrer)))

    return render_template('business/edit/images/profile_banner.html',
                           form=form,
                           thebiz=thebiz,
                           )


@business_edit.route('/view/<business_name>', methods=['GET'])
@login_required
def view_bio(business_name):
    thebiz = Business.query.filter(Business.business_name == business_name).first()

    if current_user.id != thebiz.user_id:
        flash('Invalid user', category="success")
        return redirect(url_for('index'))
    if thebiz.biz_info is None:

        bizbio = BusinessInfo(
            official_business_name='',
            business_id=thebiz.id,
            phone_number='',
            email='',
            about='',

            website='',
            facebook='',
            twitter='',
        )

        db.session.add(bizbio)
        db.session.commit()

    form = MyAccountForm(business_name=thebiz.official_business_name,
                         about=thebiz.biz_info.about,
                         email=thebiz.biz_info.email,
                         phone=thebiz.biz_info.phone_number,
                         website=thebiz.biz_info.website,
                         facebook=thebiz.biz_info.facebook,
                         twitter=thebiz.biz_info.twitter,
                         )

    return render_template('business/edit/info.html',
                           form=form,
                           thebiz=thebiz
                           )


@business_edit.route('/edit/<business_name>/basic', methods=['POST'])
@login_required
def edit_bio(business_name):
    thebiz = Business.query.filter(Business.business_name == business_name).first()

    form = MyAccountForm(about=thebiz.biz_info.about,
                         email=thebiz.biz_info.email,
                         phone=thebiz.biz_info.phone_number,
                         business_name=thebiz.official_business_name,

                         website=thebiz.biz_info.website,
                         facebook=thebiz.biz_info.facebook,
                         twitter=thebiz.biz_info.twitter,
                         )
    if request.method == 'POST':
        if form.validate_on_submit():

            thebiz.biz_info.about = form.about.data
            thebiz.biz_info.email = form.email.data
            thebiz.biz_info.phone_number = form.phone.data
            thebiz.official_business_name = form.business_name.data

            thebiz.biz_info.website = form.website.data
            thebiz.biz_info.facebook = form.facebook.data
            thebiz.biz_info.twitter = form.twitter.data

            db.session.add(thebiz)
            db.session.add(thebiz.biz_info)
            db.session.commit()

            flash('Profile has been changed', category="success")
            return redirect(url_for('business.main', business_name=thebiz.business_name))
        else:
            for errors in form.about.errors:
                flash(errors, category="danger")
            for errors in form.email.errors:
                flash(errors, category="danger")
            for errors in form.phone.errors:
                flash(errors, category="danger")
            for errors in form.business_name.errors:
                flash(errors, category="danger")
            for errors in form.website.errors:
                flash(errors, category="danger")
            for errors in form.facebook.errors:
                flash(errors, category="danger")
            for errors in form.twitter.errors:
                flash(errors, category="danger")
            return redirect(url_for('business_edit.view_bio', business_name=thebiz.business_name))
    return redirect(url_for('business.main', business_name=thebiz.business_name))


@business_edit.route('/view/location/<business_name>', methods=['GET'])
@login_required
def view_location(business_name):
    thebiz = Business.query.filter(Business.business_name == business_name).first()
    if thebiz is not None:
        if current_user.id != thebiz.user_id:
            flash('Invalid user', category="success")
            return redirect(url_for('index'))
        if thebiz is not None:
            # form = MyLocationForm(theaddress=thebiz.biz_location.address,
            #                       thetown=thebiz.biz_location.town,
            #                       thestate=thebiz.biz_location.state_or_province,
            #                       thecountry=thebiz.biz_location.country,
            #                       thezipcode=thebiz.biz_location.zipcode,
            #                       )
            form = MyLocationForm()
        else:
            form = MyLocationForm()
    else:
        flash('Business not found', category="success")
        return redirect(url_for('index'))
    return render_template('business/edit/locations.html',
                           form=form,
                           thebiz=thebiz
                           )


@business_edit.route('/edit/location/<business_name>', methods=['POST'])
@login_required
def edit_location(business_name):

    if request.method == 'POST':
        thebiz = Business.query.filter(Business.business_name == business_name).first()

        if current_user.id != thebiz.user_id:
            flash('Invalid user', category="success")
            return redirect(url_for('index'))

        form = MyLocationForm(theaddress=thebiz.biz_location.address,
                              thetown=thebiz.biz_location.town,
                              thestate=thebiz.biz_location.state_or_province,
                              thecountry=thebiz.biz_location.country,
                              thezipcode=thebiz.biz_location.zipcode,
                              )
        if form.validate_on_submit():

            thebiz.biz_location.address = form.theaddress.data
            thebiz.biz_location.town = form.thetown.data
            thebiz.biz_location.state_or_province = form.thestate.data
            thebiz.biz_location.country = form.thecountry.data
            thebiz.biz_location.zipcode = form.thezipcode.data

            db.session.add(thebiz.biz_location)
            db.session.commit()

            flash('Location has been changed', category="success")
            return redirect(url_for('business.main', business_name=thebiz.business_name))
        else:
            for errors in form.theaddress.errors:
                flash(errors, category="danger")
            for errors in form.thetown.errors:
                flash(errors, category="danger")
            for errors in form.thestate.errors:
                flash(errors, category="danger")
            for errors in form.thecountry.errors:
                flash(errors, category="danger")
            for errors in form.thezipcode.errors:
                flash(errors, category="danger")
            return redirect(url_for('business_edit.view_location', business_name=thebiz.business_name))


@business_edit.route('/owner/delete/<string:business_name>', methods=['GET'])
@login_required
def ownerdeletepage(business_name):

    if request.method == 'GET':
        deleteform = DeleteRoomForm()

        thebiz = Business.query.filter(Business.business_name == business_name).first()

        # see if user is a creator
        if thebiz.user_id != current_user.id:

            # see if user is a mod

            flash("You are not the owner of this page.", category="danger")
            return redirect(url_for('index'))

        # add a user to the sub

        return render_template('business/edit/delete.html',
                               deleteform=deleteform,
                               thebiz=thebiz
                               )


@business_edit.route('/owner/delete/<string:business_name>', methods=['POST'])
@login_required
def ownerdeletepageconfirm(business_name):

    if request.method == 'POST':
        deleteform = DeleteRoomForm()

        thebiz = Business.query.filter(Business.business_name == business_name).first()

        if thebiz.user_id != current_user.id:
            # see if user is a mod

            flash("You are not the owner of this page.", category="danger")
            return redirect(url_for('index'))
        else:

            if deleteform.page_name.data == str(business_name):
                # delete business
                deleteprofileimage(business_id=thebiz.id)
                deletebannerimage(business_id=thebiz.id)

                # delete business followers
                biz_followers = BusinessFollowers.query.filter(BusinessFollowers.business_id == thebiz.id).all()
                for f in biz_followers:
                    db.session.delete(f)

                # delete stats
                biz_stats = BusinessStats.query.filter(BusinessStats.business_id == thebiz.id).first()
                if biz_stats:
                    db.session.delete(biz_stats)

                # delete info
                biz_info = BusinessInfo.query.filter(BusinessInfo.business_id == thebiz.id).first()
                if biz_info:
                    db.session.delete(biz_info)

                # delete services
                biz_services = BusinessServices.query.filter(BusinessServices.business_id == thebiz.id).first()
                if biz_services:
                    db.session.delete(biz_services)

                # delete location
                biz_location = BusinessLocation.query.filter(BusinessLocation.business_id == thebiz.id).first()
                if biz_location:
                    db.session.delete(biz_location)

                # delete posts
                biz_posts = CommonsPost.query.filter(CommonsPost.content_user_id == thebiz.id,
                                                     CommonsPost.type_of_post == 1,
                                                     CommonsPost.subcommon_id == 13).all()
                for f in biz_posts:
                    db.session.delte(f)
                db.session.delete(thebiz)
                db.session.commit()

                flash("PAGE HAS BEEN DELETED.", category="danger")
                return redirect(url_for('index'))
            else:
                flash("Page Name not found.  Did you spell it correctly?", category="danger")
                return redirect(url_for('business_edit.ownerdeletepage', business_name=thebiz.business_name))


@business_edit.route('/owner/accepts/<string:business_name>', methods=['GET'])
@login_required
def acceptswhatcurrency(business_name):

    if request.method == 'GET':
        whatcurrencyform = AcceptsCurrency()

        thebiz = Business.query.filter(Business.business_name == business_name).first()

        # see if user is a creator
        if thebiz.user_id != current_user.id:

            # see if user is a mod

            flash("You are not the owner of this page.", category="danger")
            return redirect(url_for('index'))

        # add a user to the sub

        return render_template('business/edit/accepts.html',
                               whatcurrencyform=whatcurrencyform,
                               thebiz=thebiz
                               )


@business_edit.route('/owner/accepts/confirm/<string:business_name>', methods=['POST'])
@login_required
def acceptswhatcurrencyconfirm(business_name):

    if request.method == 'POST':
        whatcurrencyform = AcceptsCurrency()

        thebiz = Business.query.filter(Business.business_name == business_name).first()

        if thebiz.user_id != current_user.id:
            # see if user is a mod

            flash("You are not the owner of this page.", category="danger")
            return redirect(url_for('index'))
        else:

            acc_btc = whatcurrencyform.accepts_btc.data
            if acc_btc is True:
                biz_accepts_btc = 1
            else:
                biz_accepts_btc = 0

            acc_bch = whatcurrencyform.accepts_bch.data
            if acc_bch is True:
                biz_accepts_bch = 1
            else:
                biz_accepts_bch = 0

            acc_xmr = whatcurrencyform.accepts_xmr.data
            if acc_xmr is True:
                biz_accepts_xmr = 1
            else:
                biz_accepts_xmr = 0

            whataccepted = BusinessAccepts(
                business_id=thebiz.id,
                accepts_bitcoin=biz_accepts_btc,
                accepts_bitcoin_cash=biz_accepts_bch,
                accepts_monero=biz_accepts_xmr,
            )

            db.session.add(whataccepted)
            db.session.commit()
            flash("Updated Currencies.", category="danger")
            return redirect(url_for('business_edit.acceptswhatcurrency', business_name=thebiz.business_name))


@business_edit.route('/largebio/<string:business_name>', methods=['GET'])
@login_required
def view_large_bio(business_name):

    if request.method == "GET":
        thebiz = Business.query.filter(Business.business_name == business_name).first()
        if thebiz.biz_bio is None:
            newbio = BusinessSpecificInfo(
                bio='',
                business_id = thebiz.id

            )
            db.session.add(newbio)
            db.session.commit()
        form = UserBioForm(bio=thebiz.biz_bio.bio)
        if thebiz.user_id != current_user.id:
            # see if user is a mod

            flash("You are not the owner of this page.", category="danger")
            return redirect(url_for('index'))

        return render_template('business/edit/profile_large_bio.html',
                               form=form,
                               thebiz=thebiz
                               )

    if request.method == 'POST':
        return redirect(url_for('index'))


@business_edit.route('/edit/largebio/<string:business_name>', methods=['POST'])
@login_required
def edit_large_bio(business_name):

    if request.method == 'POST':
        thebiz = Business.query.filter(Business.business_name == business_name).first()
        form = UserBioForm(Bio=thebiz.biz_bio.bio)
        bizbio = BusinessSpecificInfo.query.filter(BusinessSpecificInfo.business_id == thebiz.id).first()

        if form.validate_on_submit():

            bizbio.bio = form.bio.data
            db.session.add(bizbio)
            db.session.commit()

            flash('Profile has been changed', category="success")
            return redirect(url_for('business_edit.view_large_bio', business_name=thebiz.business_name))
        else:
            flash('Form Error', category="danger")
            return redirect(url_for('business_edit.view_large_bio', business_name=thebiz.business_name))

    if request.method == 'GET':
        return redirect(url_for('index'))
