
from app import db
from decimal import Decimal

from app.wallet_xmr.transaction import monero_addtransaction

from app.models import MoneroWallet
# end models


def take_coin_from_tipper_xmr_comment(sender_id, amount, commentid, recieverid):

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

        senderwallet = MoneroWallet.query.filter_by(user_id=sender_id).first()

        # remove amount from sender
        curbal_sender = Decimal(senderwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_sender = curbal_sender - amounttomod
        senderwallet.currentbalance = newbalance_sender
        db.session.add(senderwallet)

        # add transaction for senders wallet
        monero_addtransaction(category=type_transaction_tip_comment,
                              amount=amount,
                              user_id=sender_id,
                              senderid=recieverid,
                              comment='',
                              orderid=commentid,
                              balance=newbalance_sender
                              )

        # add transaction for comments wallet
    except Exception as e:
        db.session.rollback()


def sendcoin_to_poster_xmr_comment(sender_id, amount, commentid, recieverid):

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
        type_transaction_recieve_comment = 5

        recieverwallet = MoneroWallet.query.filter_by(user_id=recieverid).first()

        # add amount to commenter
        curbal_reciever = Decimal(recieverwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_reciever = curbal_reciever + amounttomod
        recieverwallet.currentbalance = newbalance_reciever
        db.session.add(recieverwallet)

        # add transaction for senders wallet
        monero_addtransaction(category=type_transaction_recieve_comment,
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


def sendcoin_subowner_xmr_comment(sender_id, amount, commentid, recieverid):

    try:

        type_transaction_recieve_post = 10

        recieverwallet = MoneroWallet.query.filter_by(user_id=recieverid).first()

        # add amount to commenter
        curbal_reciever = Decimal(recieverwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_reciever = curbal_reciever + amounttomod
        recieverwallet.currentbalance = newbalance_reciever
        db.session.add(recieverwallet)

        # add transaction for recievers wallet
        monero_addtransaction(category=type_transaction_recieve_post,
                              amount=amount,
                              user_id=recieverid,
                              senderid=sender_id,
                              comment=commentid,
                              orderid='',
                              balance=newbalance_reciever
                              )
        # add transaction for comments wallet
    except Exception as e:
        db.session.rollback()











def take_coin_from_tipper_xmr_post(sender_id, amount, postid, recieverid):

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

        senderwallet = MoneroWallet.query.filter_by(user_id=sender_id).first()

        # remove amount from sender
        curbal_sender = Decimal(senderwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_sender = curbal_sender - amounttomod
        senderwallet.currentbalance = newbalance_sender
        db.session.add(senderwallet)

        # add transaction for senders wallet
        monero_addtransaction(category=type_transaction_tip_post,
                              amount=amount,
                              user_id=sender_id,
                              senderid=recieverid,
                              comment='',
                              orderid=postid,
                              balance=newbalance_sender
                              )

        # add transaction for comments wallet
    except Exception as e:
        db.session.rollback()


def sendcoin_to_poster_xmr_post(sender_id, amount, postid, recieverid):

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
        type_transaction_recieve_post = 7

        recieverwallet = MoneroWallet.query.filter_by(user_id=recieverid).first()

        # add amount to commenter
        curbal_reciever = Decimal(recieverwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_reciever = curbal_reciever + amounttomod
        recieverwallet.currentbalance = newbalance_reciever
        db.session.add(recieverwallet)

        # add transaction for recievers wallet
        monero_addtransaction(category=type_transaction_recieve_post,
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


def sendcoin_subowner_xmr_post(sender_id, amount, postid, recieverid):

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
        type_transaction_recieve_post = 9

        recieverwallet = MoneroWallet.query.filter_by(user_id=recieverid).first()

        # add amount to commenter
        curbal_reciever = Decimal(recieverwallet.currentbalance)
        amounttomod = Decimal(amount)
        newbalance_reciever = curbal_reciever + amounttomod
        recieverwallet.currentbalance = newbalance_reciever
        db.session.add(recieverwallet)

        # add transaction for recievers wallet
        monero_addtransaction(category=type_transaction_recieve_post,
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
