from datetime import datetime
from decimal import Decimal
from app import db
from app.common.functions import floating_decimals
from app.message.add_notification import add_new_notification

from app.wallet_xmr_stagenet.security import monero_checkbalance_stagenet
from app.classes.monero import \
    MoneroWalletStagenet, \
    MoneroWalletWorkStagenet, \
    MoneroWalletFeeStagenet, \
    MoneroUnconfirmedStagenet


def monerocreatewallet_stagenet(user_id):
    """
    This creates the wallet and gives it a random payment id for
    deposites
    :param user_id:
    :return:
    """
    timestamp = datetime.utcnow()

    monero_newunconfirmed = MoneroUnconfirmedStagenet(
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
    monero_walletcreate = MoneroWalletStagenet(user_id=user_id,
                                               currentbalance=0,
                                               unconfirmed=0,
                                               address1='',
                                               address1status=1,
                                               locked=0,
                                               transactioncount=0,
                                               )

    wallet = MoneroWalletWorkStagenet(
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


def monero_walletstatus_stagenet(user_id):
    """
    This will check if the wallet is normal,
    if not it creates a new wallet
    :param user_id:
    :return:
    """
    userwallet = db.session.query(MoneroWalletStagenet).filter_by(user_id=user_id).first()
    if userwallet:
       pass
    else:
        monerocreatewallet_stagenet(user_id=user_id)


def monerosendcoin_stagenet(user_id, sendto, amount):
    """
    # OFF SITE
    # withdrawl
    :param user_id:
    :param sendto:
    :param amount:
    :return:
    """
    getwallet = MoneroWalletFeeStagenet.query.get(1)
    walletfee = getwallet.amount
    a = monero_checkbalance_stagenet(user_id=user_id, amount=amount)
    if a == 1:

        timestamp = datetime.utcnow()
        userswallet = MoneroWalletStagenet.query.filter_by(user_id=user_id).first()
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
        # create the work
        wallet = MoneroWalletWorkStagenet(
            user_id=user_id,
            type=1,
            amount=amount,
            sendto=sendto,
            created=timestamp,

        )
        # save it
        db.session.add(wallet)
        db.session.add(userswallet)
        db.session.commit()

    else:
        add_new_notification(user_id=user_id,
                             subid=0,
                             subname='',
                             postid=0,
                             commentid=0,
                             msg=301)
