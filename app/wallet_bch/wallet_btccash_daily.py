
from app import db
from decimal import Decimal

from app.wallet_bch.wallet_btccash_transaction import bch_cash_addtransaction

from app.classes.bch import BchWallet
# end models


def sendcoin_user_daily_bch(user_id, amount):

    """
    :param user_id:
    :param amount:
    :return:
    """

    type_transaction_send_daily = 15
    type_transaction_recieve_daily = 16

    sender_wallet = BchWallet.query.filter_by(user_id=1).first()
    recieve_wallet = BchWallet.query.filter(BchWallet.user_id==user_id).first()

    # remove amount from tipvote wallet
    curbal_sender = Decimal(sender_wallet.currentbalance)
    amount_sent_modified_decimal = Decimal(amount)
    newbalance_sender = curbal_sender - amount_sent_modified_decimal
    sender_wallet.currentbalance = newbalance_sender

    # add amount to user
    current_balance_reciever = Decimal(recieve_wallet.currentbalance)
    amount_recieve_modified_decimal = Decimal(amount)
    newbalance_reciever = current_balance_reciever + amount_recieve_modified_decimal
    recieve_wallet.currentbalance = newbalance_reciever

    # add transaction for tipvote wallet
    bch_cash_addtransaction(category=type_transaction_send_daily,
                            amount=amount,
                            user_id=1,
                            senderid=user_id,
                            comment='daily reward',
                            orderid=0,
                            balance=newbalance_sender
                            )

    # add transaction to reciver wallet
    bch_cash_addtransaction(category=type_transaction_recieve_daily,
                            amount=amount,
                            user_id=user_id,
                            senderid=1,
                            comment='daily reward',
                            orderid=0,
                            balance=newbalance_reciever
                            )

    db.session.add(sender_wallet)
    db.session.add(recieve_wallet)

    db.session.commit()