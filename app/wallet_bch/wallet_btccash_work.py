
from decimal import Decimal
from datetime import datetime
from app import db
from app.common.functions import \
    floating_decimals

from app.wallet_bch.wallet_btccash_security import checkbalance
# models
from app.message.add_notification import add_new_notification
from app.models import \
    BchWallet, \
    BchWalletWork, \
    BchWalletAddresses, \
    BchUnconfirmed, \
    BchWalletFee, User


def bch_wallet_status(user_id):
    """
    This function checks status opf the wallet
    :param user_id:
    :return:
    """
    userswallet = db.session.query(BchWallet).filter_by(user_id=user_id).first()
    getuser = db.session.query(User).filter(User.id == user_id).first()
    if userswallet:
        if userswallet.address1status == 0\
                and userswallet.address2status == 0\
                and userswallet.address3status == 0:
            bch_create_wallet(user_id=user_id)
        else:
            pass
    else:
        bch_create_wallet(user_id=getuser.id)


def bch_create_wallet(user_id):
    """
    This function creates the wallet_btccash and puts its first address there
    if wallet exists it adds an address to wallet
    :param user_id:
    :return:
    """

    userswallet = BchWallet.query.filter_by(user_id=user_id).first()
    if userswallet is not None:

        # find a new clean address
        getnewaddress = BchWalletAddresses.query.filter(BchWalletAddresses.status == 0).first()
        # sets users wallet with this address
        userswallet.address1 = getnewaddress.bchaddress
        userswallet.address1status = 1
        # update address in listing as used
        getnewaddress.status = 1

        db.session.add(userswallet)
        db.session.add(getnewaddress)
        db.session.commit()
    else:
        # create a new wallet
        btc_cash_walletcreate = BchWallet(user_id=user_id,
                                          currentbalance=0,
                                          unconfirmed=0,
                                          address1='',
                                          address1status=0,
                                          address2='',
                                          address2status=0,
                                          address3='',
                                          address3status=0,
                                          locked=0,
                                          transactioncount=0
                                          )
        # add an unconfirmed
        btc_cash_newunconfirmed = BchUnconfirmed(
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
        db.session.add(btc_cash_walletcreate)
        db.session.add(btc_cash_newunconfirmed)
        db.session.commit()

        # get address for wallet
        getnewaddress = BchWalletAddresses.query.filter(BchWalletAddresses.status == 0).first()

        userswallet = BchWallet.query.filter(BchWallet.user_id == user_id).first()
        userswallet.address1 = getnewaddress.bchaddress
        userswallet.address1status = 1
        getnewaddress.status = 1

        db.session.add(userswallet)
        db.session.add(getnewaddress)
        db.session.commit()


def bch_cash_send_coin_offsite(user_id, sendto, amount, comment):
    """
    Add work order to send off site.  more secure using db
    :param user_id:
    :param sendto:
    :param amount:
    :param comment:
    :return:
    """
    getwallet = BchWalletFee.query.get(1)
    walletfee = getwallet.bch
    type_transaction = 2

    a = checkbalance(user_id=user_id, amount=amount)
    if a == 1:
        userswallet = BchWallet.query.filter(BchWallet.user_id == user_id).first()

        strcomment = str(comment)
        timestamp = datetime.utcnow()

        # turn sting to a decimal
        amountdecimal = Decimal(amount)
        # make decimal 8th power
        amounttomod = floating_decimals(amountdecimal, 8)
        # gets current balance
        curbalance = floating_decimals(userswallet.currentbalance, 8)
        # gets amount and fee
        amountandfee = floating_decimals(amounttomod + walletfee, 8)
        # subtracts amount and fee from current balance
        newamount = floating_decimals(curbalance - amountandfee, 8)
        # set balance as new amount
        userswallet.currentbalance = floating_decimals(newamount, 8)

        sendcoinwork = BchWalletWork(
            user_id=user_id,
            type=type_transaction,
            amount=amount,
            sendto=sendto,
            comment=0,
            created=timestamp,
            txtcomment=strcomment,
        )

        db.session.add(sendcoinwork)
        db.session.add(userswallet)
        db.session.commit()

    else:
        add_new_notification(user_id=user_id,
                             subid=0,
                             subname='',
                             postid=0,
                             commentid=0,
                             msg=201
                             )