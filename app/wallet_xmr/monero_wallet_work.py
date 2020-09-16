from datetime import datetime
from decimal import Decimal
from app import db
from app.common.functions import floating_decimals
from app.message.add_notification import add_new_notification

from app.wallet_xmr.security import monero_checkbalance
from app.models import \
    MoneroWallet, \
    MoneroWalletWork, \
    MoneroWalletFee, \
    MoneroUnconfirmed


def monerocreatewallet(user_id):
    """
    This creates the wallet and gives it a random payment id for
    deposites
    :param user_id:
    :return:
    """
    timestamp = datetime.utcnow()

    monero_newunconfirmed = MoneroUnconfirmed(
        user_id=user_id,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )

    # creates wallet_btc in db
    monero_walletcreate = MoneroWallet(user_id=user_id,
                                       currentbalance=0,
                                       unconfirmed=0,
                                       address1='',
                                       address1status=1,
                                       locked=0,
                                       transactioncount=0,
                                       )
    wallet = MoneroWalletWork(
        user_id=user_id,
        type=2,
        amount=0,
        sendto='',
        created=timestamp,

    )
    db.session.add(wallet)
    db.session.add(monero_newunconfirmed)
    db.session.add(monero_walletcreate)
    db.session.commit()



def monero_walletstatus(user_id):
    """
    This will check if the wallet is normal,
    if not it creates a new wallet
    :param user_id:
    :return:
    """
    userwallet = db.session.query(MoneroWallet).filter_by(user_id=user_id).first()

    if userwallet:
        pass
    else:
        monerocreatewallet(user_id=user_id)


def monerosendcoin(user_id, sendto, amount):
    """
    # OFF SITE
    # withdrawl
    :param user_id:
    :param sendto:
    :param amount:
    :return:
    """
    getwallet = MoneroWalletFee.query.get(1)
    walletfee = getwallet.amount
    a = monero_checkbalance(user_id=user_id, amount=amount)
    if a == 1:

        timestamp = datetime.utcnow()
        userswallet = MoneroWallet.query.filter_by(user_id=user_id).first()
        # turn sting to a decimal
        amountdecimal = Decimal(amount)
        # make decimal 8th power
        amounttomod = floating_decimals(amountdecimal, 8)
        # gets current balance
        curbalance = floating_decimals(userswallet.currentbalance, 8)
        # gets amount and fee
        amountandfee = floating_decimals(amounttomod + walletfee, 8)
        # subtracts amount and fee from current balance
        y = floating_decimals(curbalance - amountandfee, 8)
        # set balance as new amount
        userswallet.currentbalance = floating_decimals(y, 8)
        wallet = MoneroWalletWork(
            user_id=user_id,
            type=1,
            amount=amount,
            sendto=sendto,
            created=timestamp,
        )
        db.session.add(wallet)
        db.session.commit()
        db.session.add(userswallet)
        db.session.commit()

    else:
        add_new_notification(user_id=user_id,
                             subid=0,
                             subname='',
                             postid=0,
                             commentid=0,
                             msg=34)
