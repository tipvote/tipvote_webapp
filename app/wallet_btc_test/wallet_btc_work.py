from app import db
from datetime import datetime
from decimal import Decimal
from app.common.functions import floating_decimals
from app.message.add_notification import add_new_notification
from app.wallet_btc_test.wallet_btc_security import checkbalance

from app.classes.btc import \
    BtcWalletTest, \
    BtcWalletWorkTest, \
    BtcWalletFeeTest, \
    BtcWalletAddressesTest, \
    BtcUnconfirmedTest


def walletstatus_test(user_id):

    """
    THIS function checks status of the wallet.
    Used for when checking wallets, login etc
    :param user_id:
    :return:
    """
    userwallet = db.session.query(BtcWalletTest).filter_by(user_id=user_id).first()
    if userwallet:
        pass
    else:
        createwallet_test(user_id=user_id)


def createwallet_test(user_id):
    """
    This function creates the wallet_btc(if one doesnt exist)
    It gets a new address and adds it.

    If wallet exists...find a new address to add to wallet
    :param user_id:
    :return:
    """
    getnewaddress = BtcWalletAddressesTest.query.filter(BtcWalletAddressesTest.status == 0).first()
    getnewaddress.status = 1

    btc_walletcreate = BtcWalletTest(user_id=user_id,
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
    btc_newunconfirmed = BtcUnconfirmedTest(
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

    db.session.add(btc_walletcreate)
    db.session.add(btc_newunconfirmed)
    db.session.add(getnewaddress)
    db.session.commit()


def sendcoin_offsite_test(user_id, sendto, amount, comment):

    """
    Withdrawl offsite
    :param user_id:
    :param sendto:
    :param amount:
    :param comment:
    :return:
    """
    type_transaction = 2
    getwallet = BtcWalletFeeTest.query.get(1)
    walletfee = getwallet.btc

    a = checkbalance(user_id=user_id, amount=amount)
    if a == 1:
        userswallet_test = BtcWalletTest.query.filter_by(user_id=user_id).first()

        strcomment = str(comment)

        timestamp = datetime.utcnow()

        amountdecimal = Decimal(amount)
        # make decimal 8th power
        amounttomod = floating_decimals(amountdecimal, 8)
        # gets current balance
        curbalance = floating_decimals(userswallet_test.currentbalance, 8)
        # gets amount and fee
        amountandfee = floating_decimals(amounttomod + walletfee, 8)
        # subtracts amount and fee from current balance
        userfinalbalance = floating_decimals(curbalance - amountandfee, 8)
        # set balance as new amount
        userswallet_test.currentbalance = floating_decimals(userfinalbalance, 8)

        wallet_test = BtcWalletWorkTest(
            user_id=user_id,
            type=type_transaction,
            amount=amount,
            sendto=sendto,
            comment=0,
            created=timestamp,
            txtcomment=strcomment,
        )

        db.session.add(wallet_test)
        db.session.add(userswallet_test)
        db.session.commit()
    else:
        add_new_notification(user_id=user_id,
                             subid=0,
                             subname='',
                             postid=0,
                             commentid=0,
                             msg=101
                             )


