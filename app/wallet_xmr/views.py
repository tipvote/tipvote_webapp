from flask import \
    render_template,\
    redirect, \
    url_for, \
    flash, \
    request
from flask_login import current_user
from decimal import Decimal

from app import db, app

from app.common.functions import floating_decimals
from app.common.decorators import\
    login_required
from app.wallet_xmr.monero_wallet_work import monerocreatewallet, monerosendcoin

from app.wallet_xmr import wallet_xmr

from app.wallet_xmr.forms import \
    WalletSendCoin

from app.models import \
    MoneroWallet, \
    MoneroWalletFee, \
    MoneroTransactions,\
    User,\
    MoneroWalletWork, Notifications


@wallet_xmr.route('', methods=['GET'])
@login_required
def home():
    # forms
    form = WalletSendCoin()

    # Get wallet
    wallet = MoneroWallet.query.filter_by(user_id=current_user.id).first()
    if wallet is None:
        monerocreatewallet(user_id=current_user.id)
    if wallet.address1status == 0:
        monerocreatewallet(user_id=current_user.id)

    # get unread messages
    if current_user.is_authenticated:
        thenotes = db.session.query(Notifications)
        thenotes = thenotes.filter(Notifications.user_id == current_user.id)
        thenotes = thenotes.order_by(Notifications.timestamp.desc())
        thenotescount = thenotes.filter(Notifications.read == 0)
        thenotescount = thenotescount.count()
        thenotes = thenotes.limit(10)
    else:
        thenotes = 0
        thenotescount = 0

    walletwork = MoneroWalletWork.query.filter_by(user_id=current_user.id).first()
    # walletfee
    walletthefee = db.session.query(MoneroWalletFee).get(1)
    wfee = Decimal(walletthefee.amount)

    # Get Transaction history
    page = request.args.get('page', 1, type=int)
    transactfull = db.session.query(MoneroTransactions)
    transactfull = transactfull.filter(MoneroTransactions.user_id == current_user.id)
    transactfull = transactfull.filter(MoneroTransactions.digital_currency == 4)
    transactfull = transactfull.order_by(MoneroTransactions.id.desc())
    transactcount = transactfull.count()
    transactfull = transactfull.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('wallet_xmr.home', page=transactfull.next_num) \
        if transactfull.has_next else None
    prev_url = url_for('wallet_xmr.home', page=transactfull.prev_num) \
        if transactfull.has_prev else None

    return render_template('wallet_xmr/home.html',
                           # forms
                           form=form,
                           # wallet
                           wallet=wallet,
                           walletwork=walletwork,
                           thenotes=thenotes,
                           thenotescount=thenotescount,
                           wfee=wfee,
                           # transactions
                           transactcount=transactcount,
                           transact=transactfull.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           )


@wallet_xmr.route('/sendxmr', methods=['POST'])
@login_required
def sendcoin():

    # forms
    form = WalletSendCoin()

    # Get wallet
    wallet = db.session.query(MoneroWallet).filter_by(user_id=current_user.id).first()

    # walletfee
    walletthefee = db.session.query(MoneroWalletFee).get(1)
    wfee = Decimal(walletthefee.amount)

    if request.method == "POST":
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
                        monerosendcoin(
                            user_id=current_user.id,
                            sendto=sendto,
                            amount=amount,
                        )
                        flash("XMR Sent: " + str(sendto), category="success")
                        flash("Please allow a few minutes for the transaction to appear and process to begin.",
                              category="success")

                        return redirect(url_for('wallet_xmr.home', user_name=current_user.user_name))
                    else:
                        flash("Cannot withdraw amount less than wallet_btc fee: " + str(wfee), category="danger")
                        return redirect(url_for('wallet_xmr.home', user_name=current_user.user_name))
                else:
                    flash("Cannot withdraw amount less than wallet_btc fee: " + str(wfee), category="danger")
                    return redirect(url_for('wallet_xmr.home', user_name=current_user.user_name))
            else:
                flash("Invalid Pin.", category="danger")
                return redirect(url_for('wallet_xmr.home', user_name=current_user.user_name))
        else:
            flash("Bad Form.  Did you enter the information correctly?", category="danger")
            return redirect(url_for('wallet_xmr.home', user_name=current_user.user_name))