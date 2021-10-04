from app import db
from datetime import datetime
import bleach
from markdown import markdown


class BtcPrices(db.Model):
    __tablename__ = 'prices_btc'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_main"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.DECIMAL(50, 2))


class BtcWallet(db.Model):
    __tablename__ = 'btc_wallet'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    currentbalance = db.Column(db.DECIMAL(20, 8))
    address1 = db.Column(db.TEXT)
    address1status = db.Column(db.INTEGER)
    address2 = db.Column(db.TEXT)
    address2status = db.Column(db.INTEGER)
    address3 = db.Column(db.TEXT)
    address3status = db.Column(db.INTEGER)
    locked = db.Column(db.INTEGER)
    transactioncount = db.Column(db.INTEGER)
    unconfirmed = db.Column(db.DECIMAL(20, 8))


class BtcUnconfirmed(db.Model):
    __tablename__ = 'btc_unconfirmed'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))

    unconfirmed1 = db.Column(db.DECIMAL(20, 8))
    unconfirmed2 = db.Column(db.DECIMAL(20, 8))
    unconfirmed3 = db.Column(db.DECIMAL(20, 8))
    unconfirmed4 = db.Column(db.DECIMAL(20, 8))
    unconfirmed5 = db.Column(db.DECIMAL(20, 8))

    txid1 = db.Column(db.TEXT)
    txid2 = db.Column(db.TEXT)
    txid3 = db.Column(db.TEXT)
    txid4 = db.Column(db.TEXT)
    txid5 = db.Column(db.TEXT)


class BtcWalletWork(db.Model):
    __tablename__ = 'btc_walletwork'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    type = db.Column(db.INTEGER)
    amount = db.Column(db.DECIMAL(20, 8))
    sendto = db.Column(db.TEXT)
    comment = db.Column(db.TEXT)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    txtcomment = db.Column(db.TEXT)


class BtcWalletAddresses(db.Model):
    __tablename__ = 'btc_walletaddresses'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btcaddress = db.Column(db.TEXT)
    status = db.Column(db.INTEGER)


class TransactionsBtc(db.Model):
    __tablename__ = 'btc_transactions'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))
    category = db.Column(db.INTEGER)
    senderid = db.Column(db.INTEGER)
    confirmations = db.Column(db.INTEGER)
    txid = db.Column(db.TEXT)
    amount = db.Column(db.DECIMAL(20, 8))
    blockhash = db.Column(db.TEXT)
    timeoft = db.Column(db.INTEGER)
    timerecieved = db.Column(db.INTEGER)
    commentbtc = db.Column(db.TEXT)
    otheraccount = db.Column(db.INTEGER)
    address = db.Column(db.TEXT)
    fee = db.Column(db.DECIMAL(20, 8))
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    balance = db.Column(db.DECIMAL(20, 8))
    orderid = db.Column(db.INTEGER)
    confirmed = db.Column(db.INTEGER)
    confirmed_fee = db.Column(db.DECIMAL(20, 8))
    digital_currency = db.Column(db.INTEGER)


class BtcWalletFee(db.Model):
    __tablename__ = 'btc_walletfee'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btc = db.Column(db.DECIMAL(20, 8))


class BtcTransOrphan(db.Model):
    __tablename__ = 'btc_transorphan'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btc = db.Column(db.DECIMAL(20, 8))
    btcaddress = db.Column(db.TEXT)
    txid = db.Column(db.TEXT)


class BtcWalletTest(db.Model):
    __tablename__ = 'btc_wallet_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    currentbalance = db.Column(db.DECIMAL(20, 8))
    address1 = db.Column(db.TEXT)
    address1status = db.Column(db.INTEGER)
    address2 = db.Column(db.TEXT)
    address2status = db.Column(db.INTEGER)
    address3 = db.Column(db.TEXT)
    address3status = db.Column(db.INTEGER)
    locked = db.Column(db.INTEGER)
    transactioncount = db.Column(db.INTEGER)
    unconfirmed = db.Column(db.DECIMAL(20, 8))


class BtcUnconfirmedTest(db.Model):
    __tablename__ = 'btc_unconfirmed_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('avengers_user.users.id'))

    unconfirmed1 = db.Column(db.DECIMAL(20, 8))
    unconfirmed2 = db.Column(db.DECIMAL(20, 8))
    unconfirmed3 = db.Column(db.DECIMAL(20, 8))
    unconfirmed4 = db.Column(db.DECIMAL(20, 8))
    unconfirmed5 = db.Column(db.DECIMAL(20, 8))

    txid1 = db.Column(db.TEXT)
    txid2 = db.Column(db.TEXT)
    txid3 = db.Column(db.TEXT)
    txid4 = db.Column(db.TEXT)
    txid5 = db.Column(db.TEXT)


class BtcWalletWorkTest(db.Model):
    __tablename__ = 'btc_walletwork_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    type = db.Column(db.INTEGER)
    amount = db.Column(db.DECIMAL(20, 8))
    sendto = db.Column(db.TEXT)
    comment = db.Column(db.TEXT)
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    txtcomment = db.Column(db.TEXT)


class BtcWalletAddressesTest(db.Model):
    __tablename__ = 'btc_walletaddresses_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btcaddress = db.Column(db.TEXT)
    status = db.Column(db.INTEGER)


class TransactionsBtcTest(db.Model):
    __tablename__ = 'btc_transactions_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER)
    category = db.Column(db.INTEGER)
    senderid = db.Column(db.INTEGER)
    confirmations = db.Column(db.INTEGER)
    txid = db.Column(db.TEXT)
    amount = db.Column(db.DECIMAL(20, 8))
    blockhash = db.Column(db.TEXT)
    timeoft = db.Column(db.INTEGER)
    timerecieved = db.Column(db.INTEGER)
    commentbtc = db.Column(db.TEXT)
    otheraccount = db.Column(db.INTEGER)
    address = db.Column(db.TEXT)
    fee = db.Column(db.DECIMAL(20, 8))
    created = db.Column(db.TIMESTAMP(), default=datetime.utcnow())
    balance = db.Column(db.DECIMAL(20, 8))
    orderid = db.Column(db.INTEGER)
    confirmed = db.Column(db.INTEGER)
    confirmed_fee = db.Column(db.DECIMAL(20, 8))
    digital_currency = db.Column(db.INTEGER)


class BtcWalletFeeTest(db.Model):
    __tablename__ = 'btc_walletfee_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btc = db.Column(db.DECIMAL(20, 8))


class BtcTransOrphanTest(db.Model):
    __tablename__ = 'btc_transorphan_test'
    __bind_key__ = 'avengers'
    __table_args__ = {"schema": "avengers_wallet_btc_test"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btc = db.Column(db.DECIMAL(20, 8))
    btcaddress = db.Column(db.TEXT)
    txid = db.Column(db.TEXT)
