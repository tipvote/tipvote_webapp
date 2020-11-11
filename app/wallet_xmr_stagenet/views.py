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
from app.wallet_xmr_stagenet.monero_wallet_work import \
    monerocreatewallet_stagenet, \
    monerosendcoin_stagenet

from app.wallet_xmr_stagenet import wallet_xmr_stagenet

from app.wallet_xmr_stagenet.forms import \
    WalletSendCoin

from app.classes.monero import \
    MoneroWalletStagenet, \
    MoneroWalletFeeStagenet, \
    MoneroTransactionsStagenet,\
    MoneroWalletWorkStagenet

from app.classes.user import User


@wallet_xmr_stagenet.route('', methods=['GET'])
@login_required
def home():
    # forms
    form = WalletSendCoin()

    # Get wallet
    wallet = db.session.query(MoneroWalletStagenet).filter_by(user_id=current_user.id).first()
    if wallet is None:
        monerocreatewallet_stagenet(user_id=current_user.id)
    if wallet.address1status == 0:
        monerocreatewallet_stagenet(user_id=current_user.id)
    walletwork = MoneroWalletWorkStagenet.query.filter_by(user_id=current_user.id).first()
    # walletfee
    walletthefee = db.session.query(MoneroWalletFeeStagenet).get(1)
    wfee = Decimal(walletthefee.amount)

    # Get Transaction history
    page = request.args.get('page', 1, type=int)
    transactfull = db.session.query(MoneroTransactionsStagenet)
    transactfull = transactfull.filter(MoneroTransactionsStagenet.user_id == current_user.id)
    transactfull = transactfull.filter(MoneroTransactionsStagenet.digital_currency == 4)
    transactfull = transactfull.order_by(MoneroTransactionsStagenet.id.desc())
    transactcount = transactfull.count()
    transactfull = transactfull.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('wallet_xmr.home', page=transactfull.next_num) \
        if transactfull.has_next else None
    prev_url = url_for('wallet_xmr.home', page=transactfull.prev_num) \
        if transactfull.has_prev else None

    return render_template('wallet_xmr_stagenet/home.html',
                           # forms
                           form=form,
                           # wallet
                           wallet=wallet,
                           walletwork=walletwork,
                           wfee=wfee,
                           # transactions
                           transactcount=transactcount,
                           transact=transactfull.items,
                           next_url=next_url,
                           prev_url=prev_url,

                           )


@wallet_xmr_stagenet.route('/sendxmr', methods=['POST'])
@login_required
def sendcoin():

    # forms
    form = WalletSendCoin()
    # Get wallet
    wallet = db.session.query(MoneroWalletStagenet).filter_by(user_id=current_user.id).first()
    # walletfee
    walletthefee = db.session.query(MoneroWalletFeeStagenet).get(1)
    wfee = Decimal(walletthefee.amount)

    if request.method == "POST":
        if form.validate_on_submit():
            if User.decryptpassword(pwdhash=current_user.wallet_pin, password=form.pin.data):
                sendto = form.sendto.data
                amount = form.amount.data
                # test wallet_btc stuff for security
                walbal = Decimal(wallet.currentbalance)
                amount2withfee = Decimal(amount) + Decimal(wfee)
                # greater than amount with fee
                if floating_decimals(walbal, 8) >= floating_decimals(amount2withfee, 8):
                    # greater than fee
                    if Decimal(amount) > Decimal(wfee):
                        # add to wallet_btc work
                        monerosendcoin_stagenet(
                            user_id=current_user.id,
                            sendto=sendto,
                            amount=amount,
                        )
                        flash("XMR Sent: " + str(sendto), category="success")
                        flash("Please allow a few minutes for the transaction to appear and process to begin.",
                              category="success")

                        return redirect(url_for('wallet_xmr_stagenet.home',
                                                user_name=current_user.user_name))
                    else:
                        flash("Cannot withdraw amount less than wallet_btc fee: " + str(wfee), category="danger")
                        return redirect(url_for('wallet_xmr_stagenet.home',
                                                user_name=current_user.user_name))
                else:
                    flash("Cannot withdraw amount less than wallet_btc fee: " + str(wfee), category="danger")
                    return redirect(url_for('wallet_xmr_stagenet.home',
                                            user_name=current_user.user_name))
            else:
                flash("Invalid Pin", category="danger")
                return redirect(url_for('wallet_xmr_stagenet.home',
                                        user_name=current_user.user_name))
        else:
            flash("Bad Form.  Did you enter the information correctly?", category="danger")
            return redirect(url_for('wallet_xmr_stagenet.home',
                                    user_name=current_user.user_name))
