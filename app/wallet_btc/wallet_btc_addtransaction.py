from app import db
from datetime import\
    datetime
from app.classes.btc import TransactionsBtc

# type 1: wallet withdrawl
# type 2: send bitcoin offsite
# type 4: send coin to escrow
# type 5: send coin to user
# type 6: send coin to agoras profit
# type 7: send coin to holdings
# type 8: send coin from holdings

def addtransaction(category, amount, user_id, senderid, comment, orderid, balance):
    """

    :param category:
    :param amount:
    :param user_id:
    :param comment:
    :param senderid:
    :param orderid:
    :param balance:
    :return:
    """
    try:
        now = datetime.utcnow()
        comment = str(comment)
        orderid = int(orderid)

        trans = TransactionsBtc(
            category=category,
            user_id=user_id,
            senderid=senderid,
            confirmations=0,
            confirmed=1,
            txid='',
            blockhash='',
            timeoft=0,
            timerecieved=0,
            otheraccount=0,
            address='',
            fee=0,
            created=now,
            commentbtc=comment,
            amount=amount,
            orderid=orderid,
            balance=balance,
            digital_currency=2,
            confirmed_fee=0
        )
        db.session.add(trans)
        db.session.commit()

    except Exception as e:
        pass
