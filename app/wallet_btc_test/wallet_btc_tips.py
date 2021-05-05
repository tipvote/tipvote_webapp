
from app import db
from decimal import Decimal

from app.wallet_btc_test.wallet_btc_addtransaction import addtransaction

from app.models import BtcWalletTest
# end models


def sendcoinusertouser_btc_comment(sender_id, amount, commentid, recieverid):

    """
    # From user wallet to user wallet
    # happens during a tip to comment
    user_id0 transfers to user_id1
    :param sender_id:
    :param amount:
    :param commentid:
    :param recieverid:
    :return:
    """
    try:
        type_transaction_tip_comment = 4
        type_transaction_recieve_comment = 5

        senderwallet = BtcWalletTest.query.filter_by(user_id=sender_id).first()
        recieverwallet = BtcWalletTest.query.filter_by(user_id=recieverid).first()

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
                       senderid=recieverid,
                       comment='',
                       orderid=commentid,
                       balance=newbalance_sender
                       )
        # add transaction for senders wallet
        addtransaction(category=type_transaction_recieve_comment,
                       amount=amount,
                       user_id=recieverid,
                       senderid=sender_id,
                       comment='',
                       orderid=commentid,
                       balance=newbalance_reciever
                       )
        # add transaction for comments wallet
    except Exception as e:
        db.session.rollback()


def sendcoinusertouser_btc_post(sender_id, amount, postid, recieverid):

    """
    # From user wallet to user wallet
    # happens during a tip to post
    user_id0 transfers to user_id1
    :param sender_id:
    :param amount:
    :param postid:
    :param recieverid:
    :return:
    """
    try:
        type_transaction_tip_post = 6
        type_transaction_recieve_post = 7
        senderwallet = BtcWalletTest.query.filter_by(user_id=sender_id).first()
        recieverwallet = BtcWalletTest.query.filter_by(user_id=recieverid).first()

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
        addtransaction(category=type_transaction_tip_post,
                       amount=amount,
                       user_id=sender_id,
                       senderid=recieverid,
                       comment='',
                       orderid=postid,
                       balance=newbalance_sender
                       )
        # add transaction for recievers wallet
        addtransaction(category=type_transaction_recieve_post,
                       amount=amount,
                       user_id=recieverid,
                       senderid=sender_id,
                       comment='',
                       orderid=postid,
                       balance=newbalance_reciever
                       )
        # add transaction for comments wallet
    except Exception as e:
        db.session.rollback()