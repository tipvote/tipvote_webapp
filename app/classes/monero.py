from app import db
from datetime import datetime
import bleach
from markdown import markdown


class MoneroPrices(db.Model):
    __tablename__ = 'prices_monero'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.DECIMAL(50, 2))


class MoneroWallet(db.Model):
    __tablename__ = 'monero_wallet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    currentbalance = db.Column(db.DECIMAL(20, 12))
    address1 = db.Column(db.TEXT)
    address1status = db.Column(db.INTEGER)
    locked = db.Column(db.INTEGER)
    transactioncount = db.Column(db.INTEGER)
    unconfirmed = db.Column(db.DECIMAL(20, 12))


class MoneroTransactions(db.Model):
    __tablename__ = 'monero_transactions'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.INTEGER)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    senderid = db.Column(db.INTEGER)
    confirmations = db.Column(db.INTEGER)
    confirmed = db.Column(db.INTEGER)
    txid = db.Column(db.TEXT)
    amount = db.Column(db.DECIMAL(20, 12))
    balance = db.Column(db.DECIMAL(20, 12))
    block = db.Column(db.INTEGER)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    address = db.Column(db.TEXT)
    note = db.Column(db.TEXT)
    fee = db.Column(db.DECIMAL(20, 12))
    orderid = db.Column(db.INTEGER)
    digital_currency = db.Column(db.INTEGER)


class MoneroTransOrphan(db.Model):
    __tablename__ = 'monero_transorphan'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    xmr = db.Column(db.DECIMAL(20, 12))
    txid = db.Column(db.TEXT)


class MoneroUnconfirmed(db.Model):
    __tablename__ = 'monero_unconfirmed'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))

    unconfirmed1 = db.Column(db.DECIMAL(20, 12))
    unconfirmed2 = db.Column(db.DECIMAL(20, 12))
    unconfirmed3 = db.Column(db.DECIMAL(20, 12))
    unconfirmed4 = db.Column(db.DECIMAL(20, 12))
    unconfirmed5 = db.Column(db.DECIMAL(20, 12))

    txid1 = db.Column(db.TEXT)
    txid2 = db.Column(db.TEXT)
    txid3 = db.Column(db.TEXT)
    txid4 = db.Column(db.TEXT)
    txid5 = db.Column(db.TEXT)


class MoneroWalletWork(db.Model):
    __tablename__ = 'monero_wallet_work'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    type = db.Column(db.INTEGER)
    amount = db.Column(db.DECIMAL(20, 12))
    sendto = db.Column(db.TEXT)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    txnumber = db.Column(db.INTEGER)


class MoneroWalletFee(db.Model):
    __tablename__ = 'monero_walletfee'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.DECIMAL(20, 12))


class MoneroWalletAddresses(db.Model):
    __tablename__ = 'moneroaddresses'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.TEXT)
    status = db.Column(db.INTEGER)


class MoneroBlockHeight(db.Model):
    __tablename__ = 'monero_blockheight'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blockheight = db.Column(db.INTEGER)


class MoneroWalletStagenet(db.Model):
    __tablename__ = 'monero_wallet_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    currentbalance = db.Column(db.DECIMAL(20, 12))
    address1 = db.Column(db.TEXT)
    address1status = db.Column(db.INTEGER)
    locked = db.Column(db.INTEGER)
    transactioncount = db.Column(db.INTEGER)
    unconfirmed = db.Column(db.DECIMAL(20, 12))


class MoneroTransactionsStagenet(db.Model):
    __tablename__ = 'monero_transactions_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.INTEGER)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    senderid = db.Column(db.INTEGER)
    confirmations = db.Column(db.INTEGER)
    confirmed = db.Column(db.INTEGER)
    txid = db.Column(db.TEXT)
    amount = db.Column(db.DECIMAL(20, 12))
    balance = db.Column(db.DECIMAL(20, 12))
    block = db.Column(db.INTEGER)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    address = db.Column(db.TEXT)
    fee = db.Column(db.DECIMAL(20, 12))
    orderid = db.Column(db.INTEGER)
    digital_currency = db.Column(db.INTEGER)


class MoneroTransOrphanStagenet(db.Model):
    __tablename__ = 'monero_transorphan_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    xmr = db.Column(db.DECIMAL(20, 12))
    txid = db.Column(db.TEXT)


class MoneroUnconfirmedStagenet(db.Model):
    __tablename__ = 'monero_unconfirmed_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))

    unconfirmed1 = db.Column(db.DECIMAL(20, 12))
    unconfirmed2 = db.Column(db.DECIMAL(20, 12))
    unconfirmed3 = db.Column(db.DECIMAL(20, 12))
    unconfirmed4 = db.Column(db.DECIMAL(20, 12))
    unconfirmed5 = db.Column(db.DECIMAL(20, 12))

    txid1 = db.Column(db.TEXT)
    txid2 = db.Column(db.TEXT)
    txid3 = db.Column(db.TEXT)
    txid4 = db.Column(db.TEXT)
    txid5 = db.Column(db.TEXT)


class MoneroWalletWorkStagenet(db.Model):
    __tablename__ = 'monero_wallet_work_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    type = db.Column(db.INTEGER)
    amount = db.Column(db.DECIMAL(20, 12))
    sendto = db.Column(db.TEXT)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    txnumber = db.Column(db.INTEGER)


class MoneroWalletFeeStagenet(db.Model):
    __tablename__ = 'monero_walletfee_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.DECIMAL(20, 12))


class MoneroWalletAddressesStagenet(db.Model):
    __tablename__ = 'moneroaddresses_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.TEXT)
    status = db.Column(db.INTEGER)


class MoneroBlockHeightStagenet(db.Model):
    __tablename__ = 'monero_blockheight_stagenet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_monero_stagenet"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blockheight = db.Column(db.INTEGER)
