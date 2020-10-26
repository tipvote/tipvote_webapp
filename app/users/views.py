from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash,\
    request

from flask_login import\
    current_user,\
    login_user,\
    logout_user
from sqlalchemy.orm.exc import UnmappedInstanceError
from itsdangerous import URLSafeTimedSerializer

import os
from datetime import datetime

from app import db, app
from app import UPLOADED_FILES_DEST

from app.common.functions import\
    mkdir_p,\
    random_user_name_anon

from app.common.decorators import login_required
from app.nodelocations import userimagelocation, current_disk

from app.users import users

from app.users.forms import LoginForm, \
    RegistrationForm, \
    ChangePinForm, \
    ChangePasswordForm,\
    AnonForm,\
    NewPinForm,\
    MyAccountForm,\
    LostPassword,\
    LostPinSendEmail,\
    LostPinForm,\
    PasswordFormReset,\
    ResendConfirmationForm,\
    ChangeEmailForm, \
    DeleteUserForm, \
    DeleteAllForm,\
    ThemeForm

from app.models import\
    User,\
    UserTimers,\
    UserStats,\
    UserStatsBTC,\
    UserStatsBCH,\
    UserStatsXMR,\
    UserCoins, \
    UserPublicInfo, \
    CommonsPost, \
    Comments


from app.wallet_btc.wallet_btc_work import createwallet
from app.wallet_bch.wallet_btccash_work import bch_create_wallet
from app.wallet_xmr.monero_wallet_work import monerocreatewallet
from app.wallet_xmr_stagenet.monero_wallet_work import monerocreatewallet_stagenet
from app.sendmsg import send_email


@users.route("/logout", methods=['GET', 'POST'])
def logout():
    try:
        logout_user()
    except UnmappedInstanceError:
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@users.route('/login', methods=['GET'])
def login():
    form = LoginForm(request.form)

    return render_template('users/login.html',
                           form=form,
                           )


@users.route('/locked/account/locked', methods=['GET', 'POST'])
def account_locked():
    now = datetime.utcnow()
    form = ResendConfirmationForm(request.form)

    if request.method == 'GET':

        return render_template('users/account/locked.html',
                               now=now,
                               form=form,
                               )

    if request.method == 'POST':
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

        theuser = form.username.data
        theemail = form.email.data
        flash("If the information provided is correct, an email will be sent.", category="success")
        password_reset_url = url_for(
            'users.unlock_with_token',
            token=password_reset_serializer.dumps(theemail, salt='password-reset-salt'),
            _external=True)
        authfail = render_template('users/email/accountlocked.html',
                                   user=theuser,
                                   now=now,
                                   password_reset_url=password_reset_url)
        # END EMAIL STUFF

        send_email('Tipvote.com - Account Locked', [theemail], '', authfail)
        return redirect(url_for('users.account_locked'))


@users.route('/login/submit', methods=['POST'])
def login_post():

    if request.method == 'POST':
        form = LoginForm(request.form)

        if form.validate_on_submit():
            user = db.session.query(User).filter_by(user_name=form.user_name.data).first()
            if user is not None:
                if User.decryptpassword(pwdhash=user.password_hash,
                                        password=form.password_hash.data):
                    if user.locked == 0:
                        user.fails = 0
                        db.session.add(user)
                        db.session.commit()
                        login_user(user)
                        current_user.is_authenticated()
                        current_user.is_active()
                        return redirect(url_for('index'))

                    else:
                        return redirect(url_for('users.account_locked'))
                else:
                    x = user.fails
                    y = x + 1
                    user.fails = y
                    db.session.add(user)
                    db.session.commit()

                    if int(user.fails) >= 5:

                        user.locked = 1

                        db.session.add(user)
                        db.session.commit()

                        return redirect(url_for('users.account_locked'))
                    else:
                        flash("Please retry user name or password.", category="danger")
                        return redirect(url_for('users.login'))
            else:
                flash("Please retry user name or password", category="danger")
                return redirect(url_for('users.login'))
        else:
            flash("Please retry user name or password.", category="danger")
            return redirect(url_for('users.login'))

    else:
        flash("Incorrect form.", category="danger")
        return redirect(url_for('index'))


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate_on_submit():

            try:
                theanonid = random_user_name_anon()
                now = datetime.utcnow()
                cryptedpwd = User.cryptpassword(password=form.password.data)

                # add user to db
                newuser = User(
                    user_name=form.user_name.data,
                    email=form.email.data,
                    password_hash=cryptedpwd,
                    wallet_pin='0',
                    profileimage='',
                    bannerimage='',
                    member_since=now,
                    admin=0,
                    admin_role=0,
                    bio='',
                    last_seen=now,
                    locked=0,
                    fails=0,
                    confirmed=0,
                    anon_id=theanonid,
                    anon_mode=0,
                    over_age=0,
                    agree_to_tos=True,
                    banned=0,
                    color_theme=1
                )
                db.session.add(newuser)
                db.session.commit()

                # profile info
                userbio = UserPublicInfo(
                    user_id=newuser.id,
                    bio='',
                    short_bio=''
                )
                stats_for_btc = UserStatsBTC(
                    user_name=newuser.user_name,
                    user_id=newuser.id,
                    # given to posters/commenters
                    total_donated_to_postcomments_btc=0,
                    total_donated_to_postcomments_usd=0,
                    # recieved from posting
                    total_recievedfromposts_btc=0,
                    total_recievedfromposts_usd=0,
                    # recieved from comments
                    total_recievedfromcomments_btc=0,
                    total_recievedfromcomments_usd=0,
                    # given to charities
                    total_donated_to_cause_btc=0,
                    total_donated_to_cause_usd=0,
                )
                stats_for_bch = UserStatsBCH(
                    user_name=newuser.user_name,
                    user_id=newuser.id,
                    # given to posters/commenters
                    total_donated_to_postcomments_bch=0,
                    total_donated_to_postcomments_usd=0,
                    # recieved from posting
                    total_recievedfromposts_bch=0,
                    total_recievedfromposts_usd=0,
                    # recieved from comments
                    total_recievedfromcomments_bch=0,
                    total_recievedfromcomments_usd=0,
                    # given to charities
                    total_donated_to_cause_bch=0,
                    total_donated_to_cause_usd=0,
                )
                stats_for_xmr = UserStatsXMR(
                    user_name=newuser.user_name,
                    user_id=newuser.id,
                    # given to posters/commenters
                    total_donated_to_postcomments_xmr=0,
                    total_donated_to_postcomments_usd=0,
                    # recieved from posting
                    total_recievedfromposts_xmr=0,
                    total_recievedfromposts_usd=0,
                    # recieved from comments
                    total_recievedfromcomments_xmr=0,
                    total_recievedfromcomments_usd=0,
                    # given to charities
                    total_donated_to_cause_xmr=0,
                    total_donated_to_cause_usd=0,
                )

                stats_for_user = UserStats(
                    user_name=newuser.user_name,
                    user_id=newuser.id,
                    post_upvotes=0,
                    post_downvotes=0,
                    comment_upvotes=0,
                    comment_downvotes=0,
                    total_posts=0,
                    total_comments=0,
                    user_level=1,
                    user_exp=0,
                    user_width_next_level='0'
                )

                users_timers = UserTimers(
                    user_name=newuser.user_name,
                    user_id=newuser.id,
                    account_created=now,
                    last_post=now,
                    last_common_creation=now,
                    last_comment=now,
                    last_report=now
                )

                # give user a starter coin
                starter_coin = UserCoins(
                    image_thumbnail='1',
                    coin_id=1,
                    user_id=newuser.id,
                    user_name=newuser.user_name,
                    obtained=now,
                    quantity=1,
                    coin_name='starter',
                    coin_rarity=1,
                    coin_description='Welcome to tipvote. '
                                     ' This coin is given to welcome you to tipvote.'
                                     '  It provides 25 points on any post.',
                    points_value=25,
                                )

                # add to db
                db.session.add(userbio)
                db.session.add(starter_coin)
                db.session.add(users_timers)
                db.session.add(stats_for_user)
                db.session.add(stats_for_btc)
                db.session.add(stats_for_bch)
                db.session.add(stats_for_xmr)

                # commit
                db.session.commit()
                # make a user a directory
                getusernodelocation = userimagelocation(x=newuser.id)
                userfolderlocation = os.path.join(UPLOADED_FILES_DEST,
                                                  current_disk,
                                                  'user',
                                                  getusernodelocation,
                                                  str(newuser.id))
                mkdir_p(path=userfolderlocation)
                # login new user

                try:
                    # Bitcoin
                    createwallet(user_id=newuser.id)
                except:
                    pass

                try:
                    # bitcoin cash
                    bch_create_wallet(user_id=newuser.id)
                except:
                    pass

                try:
                    # Monero
                    monerocreatewallet(user_id=newuser.id)
                except:
                    pass


                login_user(newuser)
                current_user.is_authenticated()
                current_user.is_active()

                flash("Successfully Registered."
                      "  If you want to access your wallets,"
                      " you will need to confirm your email.  If you used an invalid email,"
                      " you can change this in account settings.", category="success")
                return redirect(url_for('welcome'))
            except Exception as e:
                return redirect((request.args.get('next', request.referrer)))

        else:
            for errors in form.user_name.errors:
                flash(errors, category="danger")
            for errors in form.password.errors:
                flash(errors, category="danger")
            for errors in form.passwordtwo.errors:
                flash(errors, category="danger")
            for errors in form.passwordtwo.errors:
                flash(errors, category="danger")

            return redirect((request.args.get('next', request.referrer)))
    return render_template('users/register.html',
                           form=form)


@users.route('/account/', methods=['GET'])
@login_required
def account():
    anonform = AnonForm()

    accountform = MyAccountForm(
                         age=current_user.over_age
                         )
    themeform = ThemeForm()
    now = datetime.utcnow()
    user = db.session.query(User).filter_by(user_name=current_user.user_name).first()

    return render_template('users/account/home.html',
                           now=now,
                           user=user,
                           anonform=anonform,
                           accountform=accountform,
                           themeform=themeform
                           )


@users.route('/account/form', methods=['POST'])
@login_required
def accountformpost():

    accountform = MyAccountForm(
                         age=current_user.over_age
                         )

    user = db.session.query(User).filter_by(user_name=current_user.user_name).first()
    if request.method == 'POST':
        if accountform.validate_on_submit():
            user.over_age = accountform.age.data
            db.session.add(user)
            db.session.commit()

            if user.over_age is False:
                flash('You are NOT allowed to view over 18 posts', category="success")

            if user.over_age is True:
                flash('You are now able to view nsfw subs and posts', category="danger")

    return redirect((request.args.get('next', request.referrer)))


@users.route('/anonymous', methods=['POST'])
@login_required
def anon():

    anonform = AnonForm()
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        if anonform.validate_on_submit():
            if user.anon_mode == 0:
                user.anon_mode = 1
                db.session.add(user)
                db.session.commit()

                flash('You are now anonymous.  Your user_name will not be shown,'
                      ' and points/stats '
                      'will not be calculated.',
                      category="success")
            else:
                user.anon_mode = 0
                db.session.add(user)
                db.session.commit()
                flash("You are now not anonymous.  Your user_name is visible and"
                      " scores/stats are counted.",
                      category="danger")
            return redirect((request.args.get('next', request.referrer)))
        else:
            return redirect((request.args.get('next', request.referrer)))


@users.route('/changepin', methods=['GET', 'POST'])
@login_required
def changepin():
    form = ChangePinForm()

    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        if form.validate_on_submit():
            if User.decryptpassword(pwdhash=user.wallet_pin,
                                    password=form.currentpin.data):
                cryptedpwd = User.cryptpassword(password=form.newpin2.data)
                user.wallet_pin = cryptedpwd

                db.session.add(user)
                db.session.commit()
                flash('Pin has been added.', category="success")

            else:
                flash('Invalid Pin', category="danger")
            return redirect((request.args.get('next', request.referrer)))
        else:
            flash('Invalid Form Entry', category="danger")
            return redirect((request.args.get('next', request.referrer)))
    return render_template('users/account/changepin.html',
                           form=form
                           )


@users.route('/setpin', methods=['GET', 'POST'])
@login_required
def setpin():
    form = NewPinForm()
    user = User.query.filter_by(id=current_user.id).first()
    if user.wallet_pin != '0':
        return redirect((request.args.get('next', request.referrer)))
    if request.method == 'POST':

        if form.validate_on_submit():
            if user.wallet_pin == '0':
                cryptedpwd = User.cryptpassword(password=form.newpin2.data)
                user.wallet_pin = cryptedpwd

                db.session.add(user)
                db.session.commit()
                flash('Pin has been changed', category="success")
                return redirect(url_for('wallet_btc.home', user_name=current_user.user_name))
            else:
                flash('Invalid Pin', category="danger")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash('Invalid Form Entry', category="danger")
            return redirect((request.args.get('next', request.referrer)))
    return render_template('users/account/setpin.html',
                           form=form
                           )


@users.route('/newpassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.decryptpassword(pwdhash=user.password_hash,
                                    password=form.currentpassword.data):
                cryptedpwd = User.cryptpassword(password=form.newpasswordtwo.data)
                user.password_hash = cryptedpwd

                db.session.add(user)
                db.session.commit()
                flash('Password has been changed', category="success")
                return redirect(url_for('users.account'))
            else:
                flash('Bad Password', category="danger")
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash(form.errors, category="danger")
            return redirect(url_for('users.account'))
    return render_template('users/account/changepassword.html',
                           form=form
                           )


@users.route('/myprofile', methods=['GET'])
@login_required
def profile():

    anonform = AnonForm()

    return render_template('users/account/profile.html',
                           anonform=anonform,
                           )


# PASSWORD RESET
def send_password_reset_email(user_email):
    now = datetime.utcnow()
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users.reset_with_token',
        token=password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    user = db.session.query(User).filter_by(email=user_email).first()
    lostpwdtemp = render_template('users/email/lostpasswordemailtemplate.html',
                                  user=user,
                                  now=now,
                                  password_reset_url=password_reset_url)

    send_email('Password Reset Requested', [user_email],'', lostpwdtemp)


@users.route('/changeemail', methods=['GET', 'POST'])
@login_required
def changeemail():

    form = ChangeEmailForm()
    user = User.query.filter_by(user_name=current_user.user_name).first()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                if User.decryptpassword(pwdhash=user.wallet_pin, password=form.accountpin.data):
                    if User.decryptpassword(pwdhash=user.password_hash, password=form.accountpassword.data):
                        user.email = form.newemail.data
                        user.fails = 0
                        db.session.add(user)
                        db.session.commit()
                        flash('Email updated', category="success")
                        return redirect(url_for('users.account', user_name=current_user.user_name))
                    else:
                        x = int(user.fails)
                        y = x + 1
                        user.fails = y
                        db.session.add(user)
                        db.session.commit()
                        if int(user.fails) == 5:
                            user.locked = 1
                            db.session.add(user)
                            db.session.commit()

                            return redirect(url_for('users.account_locked'))
                        else:
                            flash("Invalid Password/Pin", category="danger")
                            return redirect(url_for('users.changeemail', user_name=current_user.user_name))
                else:
                    x = int(user.fails)
                    y = x + 1
                    user.fails = y
                    db.session.add(user)
                    db.session.commit()
                    if int(user.fails) == 5:
                        user.locked = 1
                        db.session.add(user)
                        db.session.commit()

                        return redirect(url_for('users.account_locked'))
                    else:
                        flash("Invalid Password/Pin", category="danger")
                        return redirect(url_for('users.changeemail', user_name=current_user.user_name))
            except Exception:
                return redirect(url_for('index'))
        else:
            flash("Error in Form")
            return redirect(url_for('users.changeemail', user_name=current_user.user_name))

    return render_template('users/account/changeemail.html',

                           form=form,
                           user=user
                           )


@users.route('/lost-password', methods=['GET', 'POST'])
def retrievepassword():

    form = LostPassword()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(email=form.email.data).first()
            if user:
                if user.user_name == form.username.data:
                    if user.email == form.email.data:
                        send_password_reset_email(user_email=user.email)
                        flash('Please check your email for a password reset link.', category="success")
                        return redirect(url_for('users.retrievepassword'))
                    else:
                        flash('Invalid user/email address!', category="danger")
                        return redirect(url_for('users.retrievepassword'))
                else:
                    flash('Invalid user/email address!', category="danger")
                    return redirect(url_for('users.retrievepassword'))
            else:
                flash('Invalid user/email address!', category="danger")
                return redirect(url_for('users.retrievepassword'))
        else:
            flash('Invalid user/email address!', category="danger")
            return redirect(url_for('users.retrievepassword'))

    return render_template('users/lostpassword.html',
                           form=form)


# PIN Reset
def send_pin_reset_email(user_email):
    now = datetime.utcnow()
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users.reset_walletpin_token',
        token=password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    user = db.session.query(User).filter_by(email=user_email).first()
    lostpwdtemp = render_template('users/email/lostpinemailtemplate.html',
                                  user=user,
                                  now=now,
                                  password_reset_url=password_reset_url)

    send_email('Pin Reset Requested', [user_email], '', lostpwdtemp)


@users.route('/lost-pin', methods=['GET', 'POST'])
def retrievepin():
    form = LostPinSendEmail()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = db.session.query(User).filter_by(email=form.email.data).first()
            except:
                flash('Invalid user/email address!', category="success")
                return redirect(url_for('users.retrievepin'))
            if user:
                if user.user_name == form.username.data:
                    if user.email == form.email.data:
                        send_pin_reset_email(user_email=user.email)
                        flash('Please check your email for a password reset link. ', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid user/email address!', category="success")
                        return redirect(url_for('users.login'))
                else:
                    flash('Invalid user/email address!', category="success")
                    return redirect(url_for('users.retrievepin'))
            else:
                flash('Invalid email or username.', 'danger')
                return redirect(url_for('users.retrievepin'))
        else:
            flash('Invalid email or username.', 'danger')
            return redirect(url_for('users.retrievepin'))

    return render_template('users/resetpin.html', form=form)


@users.route('/resetpin/<token>', methods=["GET", "POST"])
def reset_walletpin_token(token):
    form = LostPinForm()
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The pin reset link is invalid or has expired. '
              'Request another email through lost pin.', category="danger")
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        if form.validate_on_submit():

            try:
                user = User.query.filter_by(email=email).first()
            except:
                flash('Invalid email address!', category="danger")
                return redirect(url_for('users.reset_walletpin_token', token=token))
            cryptedpwd = User.cryptpassword(password=form.pintwo.data)
            user.wallet_pin = cryptedpwd
            db.session.add(user)
            db.session.commit()
            flash('Your pin has been updated!', category="success")
            return redirect(url_for('index'))
        else:
            flash('Invalid form.  Pin must be 6 digits and match!', category="danger")
            return redirect(url_for('users.reset_walletpin_token', token=token))

    return render_template('users/lostpinsubmit.html',
                           form=form,
                           token=token)


@users.route('/resetpassword/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    form = PasswordFormReset()
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired. Request another email through lost password.', category="danger")
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = User.query.filter_by(email=email).first()
            except:
                flash('Invalid email address!', category="danger")
                return redirect(url_for('users.login'))
            cryptedpwd = User.cryptpassword(password=form.newpasswordtwo.data)
            user.password_hash = cryptedpwd
            db.session.add(user)
            db.session.commit()
            flash('Your password has been updated! Please login with it.', category="success")
            return redirect(url_for('users.login'))

    return render_template('users/newpassword.html', form=form, token=token)


@users.route('/unlock/<token>', methods=["GET", "POST"])
def unlock_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)

        user = User.query.filter_by(email=email).first()
        user.locked = 0
        user.fails = 0
        user.confirmed = 1
        db.session.add(user)
        db.session.commit()

        flash('Your account has been unlocked.  You can now log In.', category="success")
        return redirect(url_for('users.login'))
    except:
        flash('The password reset link is invalid or has expired.', category="success")

    return render_template('users/unlockaccount.html', token=token)


@users.route('/confirm/<token>', methods=["GET", "POST"])
def confirm_account_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)

        user = User.query.filter_by(email=email).first()
        if user.confirmed == 0:
            user.locked = 0
            user.fails = 0
            user.confirmed = 1
            db.session.add(user)
            db.session.commit()

            flash('Your Account has been confirmed.', category="success")
            return redirect(url_for('index'))
        else:
            flash('Your Account has already been confirmed.', category="success")
    except Exception as e:
        flash('Invalid or out of time!  Send another confirmation', category="danger")
    return render_template('users/unlockaccount.html', token=token)


@users.route('/confirm/<token>', methods=["GET", "POST"])
def reconfirm_account_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)

        user = User.query.filter_by(email=email).first()
        if user.confirmed == 0:
            user.locked = 0
            user.fails = 0
            user.confirmed = 1
            db.session.add(user)
            db.session.commit()

            flash('Your Account has been confirmed.', category="success")
            return redirect(url_for('index'))
        else:
            flash('Your Account has already been confirmed', category="success")
            return redirect(url_for('index'))
    except Exception as e:
        flash('Invalid or out of time!  Send another confirmation', category="danger")
    return render_template('users/unlockaccount.html', token=token)


@users.route('/resend', methods=['GET', 'POST'])
def resendconfirmation():
    now = datetime.utcnow()
    form = ResendConfirmationForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(user_name=form.username.data).first()
            if user is not None:
                if user.email == form.email.data:
                    if user.confirmed == 0:
                        # login user
                        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                        confirm_account_url = url_for(
                            'users.confirm_account_with_token',
                            token=password_reset_serializer.dumps(user.email, salt='password-reset-salt'),
                            _external=True)
                        accountreg = render_template('users/email/welcome.html',
                                                     user=user.user_name,
                                                     now=now,
                                                     password_reset_url=confirm_account_url)
                        send_email('Welcome to Tipvote! ', [user.email], '', accountreg)
                        flash("Please check your email for link to confirm account", category="success")
                        return redirect(url_for('users.resendconfirmation'))
                    else:
                        flash("Your Account is already confirmed", category="danger")
                        return redirect(url_for('users.login'))
                else:
                    flash("Incorrect Information", category="danger")
                    return redirect(url_for('users.login'))
            else:
                flash("User Doesnt exist", category="danger")
                return redirect(url_for('users.resendconfirmation'))
        else:
            flash("Form Error", category="danger")
            return redirect(url_for('users.resendconfirmation'))

    return render_template('/users/resendconfirmation.html', form=form)


@users.route('/resend/wallet', methods=['GET', 'POST'])
def confirmationforwallets():
    now = datetime.utcnow()
    form = ResendConfirmationForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(user_name=form.username.data).first()
            if user is not None:
                if user.email == form.email.data:
                    if user.confirmed == 0:
                        # login user
                        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                        confirm_account_url = url_for(
                            'users.confirm_account_with_token',
                            token=password_reset_serializer.dumps(user.email, salt='password-reset-salt'),
                            _external=True)
                        accountreg = render_template('users/email/resendconfirm.html',
                                                     user=user.user_name,
                                                     now=now,
                                                     password_reset_url=confirm_account_url)
                        send_email('Welcome to Tipvote! ', [user.email], '', accountreg)
                        flash("Please check your email for link to confirm account", category="success")
                        return redirect(url_for('index'))
                    else:
                        flash("Your Account is already confirmed", category="danger")
                        return redirect(url_for('index'))
                else:
                    flash("Incorrect Information", category="danger")
                    return redirect(url_for('users.confirmationforwallets'))
            else:
                flash("User Doesnt exist", category="danger")
                return redirect(url_for('users.resendconfirmation'))
        else:
            flash("Form Error", category="danger")
            return redirect(url_for('users.resendconfirmation'))

    return render_template('/users/resendconfirmation.html', form=form)


@users.route('/delete', methods=['GET'])
@login_required
def deleteaccount():

    if request.method == 'POST':
        return redirect(url_for('index'))

    if request.method == 'GET':
        deleteform = DeleteUserForm()

        return render_template('users/account/delete.html',
                               deleteform=deleteform,
                               )


@users.route('/delete/posts', methods=['GET'])
@login_required
def deleteallposts():

    if request.method == 'POST':
        return redirect(url_for('index'))

    if request.method == 'GET':
        deleteform = DeleteAllForm()

        return render_template('users/account/deleteposts.html',
                               deleteform=deleteform,
                               )


@users.route('/delete/posts/confirm', methods=['POST'])
@login_required
def deleteallpostsconfirm():
    if request.method == 'GET':
        return redirect(url_for('index'))

    elif request.method == 'POST':

        # user posts
        user_posts_content = CommonsPost.query.filter(CommonsPost.content_user_id == current_user.id).all()
        for f in user_posts_content:
            f.content_user_name = 'Deleted'
            f.hidden = 1
            db.session.add(f)

        user_posts_poster = CommonsPost.query.filter(CommonsPost.poster_user_id == current_user.id).all()
        for f in user_posts_poster:
            f.poster_user_name = 'Deleted'
            f.hidden = 1
            db.session.add(f)

        user_posts_username = CommonsPost.query.filter(CommonsPost.user_id == current_user.id).all()
        for f in user_posts_username:
            f.user_name = 'Deleted'
            f.hidden = 1
            db.session.add(f)

        db.session.commit()
        flash("All Posts have been marked as deleted", category="danger")
        return redirect(url_for('users.deleteallposts'))
    else:
        return redirect(url_for('index'))


@users.route('/delete/comments', methods=['GET'])
@login_required
def deleteallcomments():
    if request.method == 'POST':
        return redirect(url_for('index'))

    elif request.method == 'GET':
        deleteform = DeleteAllForm()

        return render_template('users/account/deletecomments.html',
                               deleteform=deleteform,
                               )
    else:
        return redirect(url_for('index'))


@users.route('/delete/comments/confirm', methods=['POST'])
@login_required
def deleteallcommentsconfirm():
    if request.method == 'GET':
        return redirect(url_for('index'))

    elif request.method == 'POST':

        # user comments
        user_comments = Comments.query.filter(Comments.user_id == current_user.id).all()
        for f in user_comments:
            f.user_name = 'Deleted'
            f.body = "Deleted by Author"
            f.deleted = 1
            f.visible_user_name = 'Deleted'
            db.session.add(f)
        db.session.commit()
        flash("All comments have been marked as deleted", category="danger")
        return redirect(url_for('users.deleteallcomments'))
    else:
        return redirect(url_for('index'))


@users.route('/theme/colors', methods=['POST'])
@login_required
def changetheme():
    if request.method == 'GET':
        return redirect(url_for('index'))

    elif request.method == 'POST':
        theuser = db.session.query(User).filter(current_user.id == User.id).first()
        themeform = ThemeForm()
        if themeform.validate_on_submit():
            if themeform.theme_one.data == '1':
                theuser.color_theme = 1
            elif themeform.theme_one.data == '2':
                theuser.color_theme = 2
            elif themeform.theme_one.data == '3':
                theuser.color_theme = 3
            else:
                theuser.color_theme = 1

            db.session.add(theuser)
            db.session.commit()

        else:
            theuser.color_theme = 1

            db.session.add(theuser)
            db.session.commit()
        return redirect(url_for('users.account'))