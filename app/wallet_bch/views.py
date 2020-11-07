
from flask import \
    render_template,\
    redirect, \
    url_for, \
    flash, \
    request
from flask_login import current_user
from decimal import Decimal

from app import db, app
# common
from app.common.decorators import \
    login_required
from app.common.functions import \
    floating_decimals
from app.wallet_bch.wallet_btccash_work import bch_cash_send_coin_offsite, bch_wallet_status

from app.wallet_bch import wallet_bch
# forms
from app.wallet_bch.forms import WalletSendcoin

from app.classes.notification import Notifications
from app.classes.user import User
from app.classes.subforum import SubForums, Subscribed
from app.classes.bch import\
    BchWalletFee, \
    BchWallet,\
    TransactionsBch

@wallet_bch.route('/', methods=['GET'])
@login_required
def home():

    if current_user.confirmed == 0:
        flash("You must be confirmed to access a wallet", category="success")
        return redirect(url_for('users.confirmationforwallets'))

    if current_user.wallet_pin == '0':
        flash("You must set a wallet pin in order to access your bitcoin wallet", category="success")
        return redirect(url_for('users.setpin'))

    form = WalletSendcoin()
    bch_wallet_status(user_id=current_user.id)
    wallet = db.session.query(BchWallet).filter(BchWallet.user_id == current_user.id).first()

    usersubforums = db.session.query(Subscribed)
    usersubforums = usersubforums.join(SubForums, (Subscribed.subcommon_id == SubForums.id))
    usersubforums = usersubforums.filter(current_user.id == Subscribed.user_id)
    usersubforums = usersubforums.filter(SubForums.room_banned == 0,
                                         SubForums.room_deleted == 0,
                                         SubForums.room_suspended == 0
                                         )
    usersubforums = usersubforums.filter(SubForums.id != 1)
    usersubforums = usersubforums.all()

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

    # get walletfee
    walletthefee = db.session.query(BchWalletFee).get(1)
    wfee = Decimal(walletthefee.bch)

    # get a number that will pass through withdrawl so they
    # dont have to calculate
    withdrawmamount = Decimal(wallet.currentbalance) - wfee
    if 0 > withdrawmamount:
        withdrawmamount = 0
    else:
        withdrawmamount = withdrawmamount

    # Get Transaction history
    page = request.args.get('page', 1, type=int)
    transactfull = db.session.query(TransactionsBch)
    transactfull = transactfull.filter(TransactionsBch.user_id == current_user.id)
    transactfull = transactfull.order_by(TransactionsBch.id.desc())
    transactcount = transactfull.count()
    transactfull = transactfull.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('wallet_bch.home', page=transactfull.next_num) \
        if transactfull.has_next else None
    prev_url = url_for('wallet_bch.home', page=transactfull.prev_num) \
        if transactfull.has_prev else None

    return render_template('wallet_bch/home.html',
                           # forms
                           form=form,
                           # general
                           usersubforums=usersubforums,
                           thenotes=thenotes,
                           thenotescount=thenotescount,
                           wfee=wfee,
                           wallet=wallet,
                           transactcount=transactcount,
                           transact=transactfull.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           withdrawmamount=withdrawmamount,
                           )


@wallet_bch.route('/sendcoin', methods=['POST'])
@login_required
def sendcoin():

    if request.method == "GET":
        pass

    if request.method == "POST":
        form = WalletSendcoin()
        wallet = BchWallet.query.filter(BchWallet.user_id == current_user.id).first_or_404()

        # get walletfee
        walletthefee = db.session.query(BchWalletFee).get(1)
        wfee = Decimal(walletthefee.bch)

        if form.validate_on_submit():

            if User.decryptpassword(pwdhash=current_user.wallet_pin, password=form.pin.data):

                sendto = form.sendto.data
                comment = form.description.data
                amount = form.amount.data

                # test wallet_bch stuff for security
                walbal = Decimal(wallet.currentbalance)
                amount2withfee = Decimal(amount) + Decimal(wfee)
                # greater than amount with fee
                if floating_decimals(walbal, 8) >= floating_decimals(amount2withfee, 8):
                    # greater than fee
                    if Decimal(amount) > Decimal(wfee):
                        # add to wallet_bch work
                        bch_cash_send_coin_offsite(
                            user_id=current_user.id,
                            sendto=sendto,
                            amount=amount,
                            comment=comment
                        )

                        flash("BCH Sent: " + str(sendto), category="success")
                        flash("Please allow a few minutes for your coin to be added to transactions",
                              category="success")
                        return redirect(url_for('wallet_bch.home', user_name=current_user.user_name))
                    else:
                        flash("Cannot withdraw amount less than fee: " + str(wfee), category="danger")
                        return redirect(url_for('wallet_bch.home', user_name=current_user.user_name))
                else:
                    flash("Cannot withdraw more than your balance including fee.", category="danger")
                    return redirect(url_for('wallet_bch.home', user_name=current_user.user_name))
            else:
                flash("Invalid Pin.", category="danger")
                return redirect(url_for('wallet_bch.home', user_name=current_user.user_name))
        else:
            flash("Form Error.  Did you enter something inccorrectly?  ", category="danger")
            return redirect(url_for('wallet_bch.home', user_name=current_user.user_name))
