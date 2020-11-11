from app import db
from decimal import Decimal
from app.classes.monero import MoneroWalletStagenet


def monero_checkbalance_stagenet(user_id, amount):

    # The money requested during the trade
    userwallet = db.session.query(MoneroWalletStagenet).filter_by(user_id=user_id).first()
    x = userwallet.currentbalance
    y = Decimal(amount)

    if x >= y:
        return 1
    else:
        return 0
