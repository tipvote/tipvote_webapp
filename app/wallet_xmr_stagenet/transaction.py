from app import db
from datetime import datetime
from app.models import MoneroTransactionsStagenet


# this function will move the coin from holdings back to vendor.  This is for vendor verification
def monero_addtransaction(category, amount, user_id, orderid, balance, senderid):

    now = datetime.utcnow()
    orderid = int(orderid)

    trans = MoneroTransactionsStagenet(
        category=category,
        user_id=user_id,
        senderid=senderid,
        confirmations=0,
        txid='',
        amount=amount,
        balance=balance,
        block=0,
        created=now,
        address='',

        fee=0,
        orderid=orderid,
        digital_currency=4,
        confirmed=0,
    )
    db.session.add(trans)
    db.session.commit()

