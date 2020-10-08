from decimal import Decimal
from app import db
from app.wallet_xmr.transaction import monero_addtransaction
from app.models import MoneroWallet
# end models


def sendcointosite_post_promotion_xmr(sender_id, amount, postid, room):

    """
    # From user wallet to user wallet
    # happens during a tip to post
    user_id0 transfers to user_id1
    :param sender_id:
    :param amount:
    :param postid:
    :return:
    """

    type_transaction_tip_post = 8
    type_transaction_recieve_post = 9
    senderwallet = MoneroWallet.query.filter_by(user_id=sender_id).first()
    recieverwallet = MoneroWallet.query.filter_by(user_id=1).first()

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
    monero_addtransaction(category=type_transaction_tip_post,
                          amount=amount,
                          comment=room,
                          user_id=sender_id,
                          senderid=1,
                          orderid=postid,
                          balance=newbalance_sender
                          )
    # add transaction for sites wallet
    monero_addtransaction(category=type_transaction_recieve_post,
                          amount=amount,
                          user_id=1,
                          comment=room,
                          senderid=sender_id,
                          orderid=postid,
                          balance=newbalance_reciever
                          )
    # add transaction for comments wallet
