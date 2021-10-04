from app import db
from datetime import datetime
from decimal import Decimal
from app.common.functions import floating_decimals
from app.message.add_notification import add_new_notification
from app.wallet_btc.wallet_btc_security import checkbalance

from app.classes.btc import \
    BtcWallet, \
    BtcWalletWork, \
    BtcWalletFee, \
    BtcWalletAddresses, \
    BtcUnconfirmed
from app.classes.user import User
# end models


def walletstatus(user_id):

    """
    THIS function checks status of the wallet.
    Used for when checking wallets, login etc
    :param user_id:
    :return:
    """
    userswallet = BtcWallet.query.filter_by(user_id=user_id).first()
    getuser = User.query.filter(User.id == user_id).first()
    if userswallet:
        try:
            if userswallet.address1status == 0\
                    and userswallet.address2status == 0\
                    and userswallet.address3status == 0:
                createwallet(user_id=user_id)

        except Exception as e:

            userswallet.address1 = ''
            userswallet.address1status = 0
            userswallet.address2 = ''
            userswallet.address2status = 0
            userswallet.address3 = ''
            userswallet.address3status = 0

            db.session.add(userswallet)
            db.session.commit()

    else:
        # creates wallet_btc in db
        createwallet(user_id=getuser.id)


def createwallet(user_id):
    """
    This function creates the wallet_btc(if one doesnt exist)
    It gets a new address and adds it.

    If wallet exists...find a new address to add to wallet
    :param user_id:
    :return:
    """
    getnewaddress = BtcWalletAddresses.query.filter(BtcWalletAddresses.status == 0).first()


    btc_walletcreate = BtcWallet(user_id=user_id,
                                 currentbalance=0,
                                 unconfirmed=0,
                                 address1=getnewaddress.btcaddress,
                                 address1status=1,
                                 address2='',
                                 address2status=0,
                                 address3='',
                                 address3status=0,
                                 locked=0,
                                 transactioncount=0
                                 )
    btc_newunconfirmed = BtcUnconfirmed(
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
    getnewaddress.status = 1
    db.session.add(btc_walletcreate)
    db.session.add(btc_newunconfirmed)
    db.session.add(getnewaddress)
    db.session.commit()


def sendcoin_offsite(user_id, sendto, amount, comment):

    """
    Withdrawl offsite
    :param user_id:
    :param sendto:
    :param amount:
    :param comment:
    :return:
    """
    type_transaction = 2
    getwallet = BtcWalletFee.query.get(1)
    walletfee = getwallet.btc

    a = checkbalance(user_id=user_id, amount=amount)
    if a == 1:
        userswallet = BtcWallet.query.filter_by(user_id=user_id).first()

        strcomment = str(comment)

        timestamp = datetime.utcnow()

        amountdecimal = Decimal(amount)
        # make decimal 8th power
        amounttomod = floating_decimals(amountdecimal, 8)
        # gets current balance
        curbalance = floating_decimals(userswallet.currentbalance, 8)
        # gets amount and fee
        amountandfee = floating_decimals(amounttomod + walletfee, 8)
        # subtracts amount and fee from current balance
        userfinalbalance = floating_decimals(curbalance - amountandfee, 8)
        # set balance as new amount
        userswallet.currentbalance = floating_decimals(userfinalbalance, 8)

        wallet = BtcWalletWork(
            user_id=user_id,
            type=type_transaction,
            amount=amount,
            sendto=sendto,
            comment=0,
            created=timestamp,
            txtcomment=strcomment,
        )

        db.session.add(wallet)
        db.session.add(userswallet)
        db.session.commit()
    else:
        add_new_notification(user_id=user_id,
                             subid=0,
                             subname='',
                             postid=0,
                             commentid=0,
                             msg=101
                             )


