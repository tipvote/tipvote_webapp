from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, \
    request

from flask_login import \
    current_user

from decimal import \
    Decimal

from app import db, app

from app.common.functions import \
    floating_decimals
from app.common.decorators import \
    login_required

from app.wallet_btc_test.wallet_btc_work import sendcoin_offsite_test

from app.wallet_btc_test import wallet_btc_test

from app.wallet_btc_test.wallet_btc_work import walletstatus_test

# forms
from app.wallet_btc_test.forms import WalletSendcoinTest

# models
from app.classes.btc import \
    TransactionsBtcTest, \
    BtcWalletTest, \
    BtcWalletFeeTest
from app.classes.user import User


@wallet_btc_test.route('/', methods=['GET'])
@login_required
def home():
    form = WalletSendcoinTest()
    if current_user.confirmed == 0:
        flash("You must be confirmed to access a wallet", category="success")
        return redirect(url_for('users.confirmationforwallets'))
    if current_user.wallet_pin == '0':
        flash("You must set a wallet pin in order to access your bitcoin wallet",
              category="success")
        return redirect(url_for('users.setpin'))

    walletstatus_test(user_id=current_user.id)
    wallet = db.session.query(BtcWalletTest)\
        .filter(BtcWalletTest.user_id == current_user.id)\
        .first()

    # get walletfee
    walletthefee = db.session.query(BtcWalletFeeTest).get(1)
    wfee = Decimal(walletthefee.btc)

    # get a number that will pass through withdrawl so they
    # dont have to calculate
    withdrawmamount = Decimal(wallet.currentbalance) - wfee
    if 0 > withdrawmamount:
        withdrawmamount = 0
    else:
        withdrawmamount = withdrawmamount

    # Get Transaction history
    page = request.args.get('page', 1, type=int)
    transactfull = db.session.query(TransactionsBtcTest)
    transactfull = transactfull.filter(TransactionsBtcTest.user_id == current_user.id)
    transactfull = transactfull.order_by(TransactionsBtcTest.id.desc())
    transactcount = transactfull.count()
    transactfull = transactfull.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('wallet_btc_test.home', page=transactfull.next_num) \
        if transactfull.has_next else None
    prev_url = url_for('wallet_btc_test.home', page=transactfull.prev_num) \
        if transactfull.has_prev else None

    return render_template('wallet_btc_test/home.html',
                           # forms
                           form=form,
                           # general
                           wfee=wfee,
                           wallet=wallet,
                           transactcount=transactcount,
                           transact=transactfull.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           withdrawmamount=withdrawmamount
                           )


@wallet_btc_test.route('/sendcoin', methods=['POST'])
@login_required
def sendcoin():
    form = WalletSendcoinTest()

    if request.method == "POST":
        wallet = db.session.query(BtcWalletTest)\
            .filter(BtcWalletTest.user_id == current_user.id)\
            .first()

        # get walletfee
        walletthefee = db.session.query(BtcWalletFeeTest).get(1)
        wfee = Decimal(walletthefee.btc)

        if form.validate_on_submit():
            if User.decryptpassword(pwdhash=current_user.wallet_pin, password=form.pin.data):
                sendto = form.sendto.data
                comment = form.description.data
                amount = form.amount.data
                # test wallet_btc stuff for security
                walbal = Decimal(wallet.currentbalance)
                amount2withfee = Decimal(amount) + Decimal(wfee)
                # greater than amount with fee
                if floating_decimals(walbal, 8) >= floating_decimals(amount2withfee, 8):
                    # greater than fee
                    if Decimal(amount) > Decimal(wfee):
                        # add to wallet_btc work
                        sendcoin_offsite_test(
                            user_id=current_user.id,
                            sendto=sendto,
                            amount=amount,
                            comment=comment
                        )
                        flash("BTC Test Coins Sent: " + str(sendto), category="success")
                        flash("Please allow a few minutes for your coin to be added to transactions", category="success")

                        return redirect(url_for('wallet_btc_test.home', user_name=current_user.user_name))
                    else:
                        flash("Cannot withdraw amount less than fee: " + str(wfee), category="danger")
                        return redirect(url_for('wallet_btc_test.home', user_name=current_user.user_name))
                else:
                    flash("Cannot withdraw more BTC Test Coins than your balance including fee.", category="danger")
                    return redirect(url_for('wallet_btc_test.home', user_name=current_user.user_name))
            else:
                flash("Invalid Pin. Account will be locked with 5 failed attempts.", category="danger")
                return redirect(url_for('wallet_btc_test.home', user_name=current_user.user_name))
        else:
            flash("Form Error.  Did you enter something incorrectly?  ", category="danger")
            return redirect(url_for('wallet_btc_test.home', user_name=current_user.user_name))
