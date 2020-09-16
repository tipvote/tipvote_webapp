
from app import db
from decimal import Decimal

from app.wallet_btc.wallet_btc_addtransaction import addtransaction
from app.models import BtcWallet
# end models


def sendcointosite_post_promotion_btc(sender_id, amount, postid, room):

    """
    # From user wallet to user wallet
    # happens during a tip to comment
    user_id0 transfers to user_id1
    :param sender_id:
    :param amount:
    :param postid:
    :param room:
    :return:
    """
    try:
        type_transaction_tip_comment = 8
        type_transaction_recieve_comment = 9

        senderwallet = BtcWallet.query.filter_by(user_id=sender_id).first()
        recieverwallet = BtcWallet.query.filter_by(user_id=1).first()

        # remove amount from sender
        curbal_sender = Decimal(senderwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_sender = curbal_sender - amounttomod
        senderwallet.currentbalance = newbalance_sender
        db.session.add(senderwallet)

        # add amount to commenter
        curbal_reciever = Decimal(recieverwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_reciever = curbal_reciever + amounttomod
        recieverwallet.currentbalance = newbalance_reciever
        db.session.add(recieverwallet)

        # add transaction for senders wallet
        addtransaction(category=type_transaction_tip_comment,
                       amount=amount,
                       user_id=sender_id,
                       senderid=1,
                       comment=room,
                       orderid=postid,
                       balance=newbalance_sender
                       )
        # add transaction to sites wallet
        addtransaction(category=type_transaction_recieve_comment,
                       amount=amount,
                       user_id=1,
                       senderid=sender_id,
                       comment=room,
                       orderid=postid,
                       balance=newbalance_reciever
                       )
        # add transaction for comments wallet
    except Exception as e:

        db.session.rollback()