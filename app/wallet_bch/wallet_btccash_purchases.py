
from app import db
from decimal import Decimal

from app.wallet_bch.wallet_btccash_transaction import bch_cash_addtransaction

from app.classes.bch import BchWallet
# end models


def send_coin_to_site_purchase(sender_id, amount, roomid):

    type_transaction_buy_room = 20
    type_transaction_user_purchased_room = 21

    senderwallet = BchWallet.query.filter_by(user_id=sender_id).first()
    recieverwallet = BchWallet.query.filter_by(user_id=1).first()

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
    bch_cash_addtransaction(category=type_transaction_buy_room,
                            amount=amount,
                            user_id=sender_id,
                            senderid=1,
                            comment=roomid,
                            orderid=0,
                            balance=newbalance_sender
                            )
    # add transaction to sites wallet
    bch_cash_addtransaction(category=type_transaction_user_purchased_room,
                            amount=amount,
                            user_id=1,
                            senderid=sender_id,
                            comment=roomid,
                            orderid=0,
                            balance=newbalance_reciever
                            )
