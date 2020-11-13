from app import db
from app.classes.user import *
from app.classes.monero import *
from app.classes.btc import *
from app.classes.subforum import *
from app.classes.post import *
from app.classes.bch import *
from app.classes.btc import *
from app.classes.monero import *
from app.classes.models import *
from app.common.functions import \
    mkdir_p, \
    random_user_name_anon

user_1 = 'bob'
user_2 = 'jim'
user_3 = 'bitcoinman'

now = datetime.utcnow()


def createusers():

    theanonid_1 = random_user_name_anon()
    theanonid_2 = random_user_name_anon()
    theanonid_3 = random_user_name_anon()

    cryptedpwd_1 = User.cryptpassword(password='password')
    cryptedpwd_2 = User.cryptpassword(password='password')
    cryptedpwd_3 = User.cryptpassword(password='password')

    newuser_1 = User(
        user_name=user_1,
        email='test@test.com',
        password_hash=cryptedpwd_1,
        wallet_pin='0',
        profileimage='',
        bannerimage='',
        member_since=now,
        admin=0,
        admin_role=0,
        bio='',
        last_seen=now,
        locked=0,
        fails=0,
        confirmed=0,
        anon_id=theanonid_1,
        anon_mode=0,
        over_age=0,
        agree_to_tos=True,
        banned=0,
        color_theme=1,
        post_style=1
    )

    userbio_1 = UserPublicInfo(
        user_id=1,
        bio='',
        short_bio=''
    )

    stats_for_btc_1 = UserStatsBTC(
        user_name=user_1,
        user_id=1,
        total_donated_to_postcomments_btc=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_btc=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_btc=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_btc=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_bch_1 = UserStatsBCH(
        user_name=user_1,
        user_id=1,
        total_donated_to_postcomments_bch=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_bch=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_bch=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_bch=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_xmr_1 = UserStatsXMR(
        user_name=user_1,
        user_id=1,
        total_donated_to_postcomments_xmr=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_xmr=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_xmr=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_xmr=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_user_1 = UserStats(
        user_name=user_1,
        user_id=1,
        post_upvotes=0,
        post_downvotes=0,
        comment_upvotes=0,
        comment_downvotes=0,
        total_posts=0,
        total_comments=0,
        user_level=11,
        user_exp=100,
        user_width_next_level='0'
    )

    users_timers_1 = UserTimers(
        user_name=user_1,
        user_id=1,
        account_created=now,
        last_post=now,
        last_common_creation=now,
        last_comment=now,
        last_report=now
    )

    # give user a starter coin
    starter_coin_1 = UserCoins(
        user_name=user_1,
        user_id=1,
        image_thumbnail='1',
        coin_id=1,
        obtained=now,
        quantity=1,
        coin_name='starter',
        coin_rarity=1,
        coin_description='Welcome to tipvote. '
                         ' This coin is given to welcome you to tipvote.'
                         '  It provides 25 points on any post.',
        points_value=25,
    )

    db.session.add(newuser_1)
    db.session.add(userbio_1)
    db.session.add(stats_for_btc_1)
    db.session.add(stats_for_bch_1)
    db.session.add(stats_for_xmr_1)
    db.session.add(stats_for_user_1)
    db.session.add(users_timers_1)
    db.session.add(starter_coin_1)

    newuser_2 = User(
        user_name=user_2,
        email='test@test.com',
        password_hash=cryptedpwd_2,
        wallet_pin='0',
        profileimage='',
        bannerimage='',
        member_since=now,
        admin=0,
        admin_role=0,
        bio='',
        last_seen=now,
        locked=0,
        fails=0,
        confirmed=0,
        anon_id=theanonid_2,
        anon_mode=0,
        over_age=0,
        agree_to_tos=True,
        banned=0,
        color_theme=1,
        post_style=1
    )

    userbio_2 = UserPublicInfo(
        user_id=2,
        bio='',
        short_bio=''
    )

    stats_for_btc_2 = UserStatsBTC(
        user_name=user_2,
        user_id=2,
        total_donated_to_postcomments_btc=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_btc=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_btc=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_btc=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_bch_2 = UserStatsBCH(
        user_name=user_2,
        user_id=2,
        total_donated_to_postcomments_bch=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_bch=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_bch=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_bch=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_xmr_2 = UserStatsXMR(
        user_name=user_2,
        user_id=2,
        total_donated_to_postcomments_xmr=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_xmr=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_xmr=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_xmr=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_user_2 = UserStats(
        user_name=user_2,
        user_id=2,
        post_upvotes=0,
        post_downvotes=0,
        comment_upvotes=0,
        comment_downvotes=0,
        total_posts=0,
        total_comments=0,
        user_level=20,
        user_exp=1000,
        user_width_next_level='20'
    )

    users_timers_2 = UserTimers(
        user_name=user_2,
        user_id=2,
        account_created=now,
        last_post=now,
        last_common_creation=now,
        last_comment=now,
        last_report=now
    )

    # give user a starter coin
    starter_coin_2 = UserCoins(
        user_name=user_2,
        user_id=2,
        image_thumbnail='1',
        coin_id=1,
        obtained=now,
        quantity=1,
        coin_name='starter',
        coin_rarity=1,
        coin_description='Welcome to tipvote. '
                         ' This coin is given to welcome you to tipvote.'
                         '  It provides 25 points on any post.',
        points_value=25,
    )
    db.session.add(newuser_2)
    db.session.add(userbio_2)
    db.session.add(stats_for_btc_2)
    db.session.add(stats_for_bch_2)
    db.session.add(stats_for_xmr_2)
    db.session.add(stats_for_user_2)
    db.session.add(users_timers_2)
    db.session.add(starter_coin_2)

    newuser_3 = User(
        user_name=user_3,
        email='test@test.com',
        password_hash=cryptedpwd_3,
        wallet_pin='0',
        profileimage='',
        bannerimage='',
        member_since=now,
        admin=0,
        admin_role=0,
        bio='',
        last_seen=now,
        locked=0,
        fails=0,
        confirmed=0,
        anon_id=theanonid_3,
        anon_mode=0,
        over_age=0,
        agree_to_tos=True,
        banned=0,
        color_theme=1,
        post_style=1
    )

    userbio_3 = UserPublicInfo(
        user_id=3,
        bio='',
        short_bio=''
    )

    stats_for_btc_3 = UserStatsBTC(
        user_name=user_3,
        user_id=3,
        total_donated_to_postcomments_btc=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_btc=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_btc=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_btc=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_bch_3 = UserStatsBCH(
        user_name=user_3,
        user_id=3,
        total_donated_to_postcomments_bch=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_bch=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_bch=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_bch=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_xmr_3 = UserStatsXMR(
        user_name=user_3,
        user_id=3,
        total_donated_to_postcomments_xmr=0,
        total_donated_to_postcomments_usd=0,
        total_recievedfromposts_xmr=0,
        total_recievedfromposts_usd=0,
        total_recievedfromcomments_xmr=0,
        total_recievedfromcomments_usd=0,
        total_donated_to_cause_xmr=0,
        total_donated_to_cause_usd=0,
    )

    stats_for_user_3 = UserStats(
        user_name=user_3,
        user_id=3,
        post_upvotes=0,
        post_downvotes=0,
        comment_upvotes=0,
        comment_downvotes=0,
        total_posts=0,
        total_comments=0,
        user_level=20,
        user_exp=1000,
        user_width_next_level='20'
    )

    users_timers_3 = UserTimers(
        user_name=user_3,
        user_id=3,
        account_created=now,
        last_post=now,
        last_common_creation=now,
        last_comment=now,
        last_report=now
    )

    # give user a starter coin
    starter_coin_3 = UserCoins(
        user_name=user_3,
        user_id=3,
        image_thumbnail='1',
        coin_id=1,
        obtained=now,
        quantity=1,
        coin_name='starter',
        coin_rarity=1,
        coin_description='Welcome to tipvote. '
                         ' This coin is given to welcome you to tipvote.'
                         '  It provides 25 points on any post.',
        points_value=25,
    )
    db.session.add(newuser_3)
    db.session.add(userbio_3)
    db.session.add(stats_for_btc_3)
    db.session.add(stats_for_bch_3)
    db.session.add(stats_for_xmr_3)
    db.session.add(stats_for_user_3)
    db.session.add(users_timers_3)
    db.session.add(starter_coin_3)

    db.session.commit()


def create_rooms():

    name_1 = 'general'
    name_2 = 'bitcoin'
    name_3 = 'funny'

    newcommon_1 = SubForums(subcommon_name=name_1,
                            creator_user_id=1,
                            creator_user_name=user_1,
                            created=now,
                            description='general chat',
                            type_of_subcommon=0,
                            exp_required=0,
                            age_required=0,
                            allow_text_posts=1,
                            allow_url_posts=1,
                            allow_image_posts=1,
                            total_exp_subcommon=0,
                            members=1,
                            mini_image='',
                            room_banned=0,
                            room_suspended=0,
                            room_deleted=0,
                            )

    substats_1 = SubForumStats(
        subcommon_name=name_1,
        subcommon_id=1,
        total_posts=0,
        total_exp_subcommon=0,
        members=1,
    )

    newsubcustom_1 = SubForumCustom(
        subcommon_name=name_1,
        subcommon_id=1,
        banner_image='',
        mini_image='',
    )

    newsubscription_1 = Subscribed(user_id=1,
                                   subcommon_id=1,
                                   )

    db.session.add(newcommon_1)
    db.session.add(substats_1)
    db.session.add(newsubcustom_1)
    db.session.add(newsubscription_1)

    newcommon_2 = SubForums(subcommon_name=name_2,
                            creator_user_id=1,
                            creator_user_name=user_1,
                            created=now,
                            description='Bitcoin stuff',
                            type_of_subcommon=0,
                            exp_required=0,
                            age_required=0,
                            allow_text_posts=1,
                            allow_url_posts=1,
                            allow_image_posts=1,
                            total_exp_subcommon=0,
                            members=1,
                            mini_image='',
                            room_banned=0,
                            room_suspended=0,
                            room_deleted=0,
                            )

    substats_2 = SubForumStats(
        subcommon_name=name_2,
        subcommon_id=1,
        total_posts=0,
        total_exp_subcommon=0,
        members=1,
    )

    newsubcustom_2 = SubForumCustom(
        subcommon_name=name_2,
        subcommon_id=1,
        banner_image='',
        mini_image='',
    )

    newsubscription_2 = Subscribed(user_id=1,
                                   subcommon_id=1,
                                   )

    db.session.add(newcommon_2)
    db.session.add(substats_2)
    db.session.add(newsubcustom_2)
    db.session.add(newsubscription_2)

    newcommon_3 = SubForums(subcommon_name=name_3,
                            creator_user_id=1,
                            creator_user_name=user_1,
                            created=now,
                            description='funny stuff',
                            type_of_subcommon=0,
                            exp_required=0,
                            age_required=0,
                            allow_text_posts=1,
                            allow_url_posts=1,
                            allow_image_posts=1,
                            total_exp_subcommon=0,
                            members=1,
                            mini_image='',
                            room_banned=0,
                            room_suspended=0,
                            room_deleted=0,
                            )

    substats_3 = SubForumStats(
        subcommon_name=name_3,
        subcommon_id=1,
        total_posts=0,
        total_exp_subcommon=0,
        members=1,
    )

    newsubcustom_3 = SubForumCustom(
        subcommon_name=name_3,
        subcommon_id=1,
        banner_image='',
        mini_image='',
    )

    newsubscription_3 = Subscribed(user_id=1,
                                   subcommon_id=1,
                                   )

    db.session.add(newcommon_3)
    db.session.add(substats_3)
    db.session.add(newsubcustom_3)
    db.session.add(newsubscription_3)

    db.session.commit()


def create_subscriptions():

    subtoit_1 = Subscribed(
        user_id=1,
        subcommon_id=1,
    )
    db.session.add(subtoit_1)
    subtoit_2 = Subscribed(
        user_id=1,
        subcommon_id=2,
    )
    db.session.add(subtoit_2)
    subtoit_3 = Subscribed(
        user_id=1,
        subcommon_id=3,
    )
    db.session.add(subtoit_3)

    subtoit_11 = Subscribed(
        user_id=2,
        subcommon_id=1,
    )
    db.session.add(subtoit_11)
    subtoit_12 = Subscribed(
        user_id=2,
        subcommon_id=2,
    )
    db.session.add(subtoit_12)
    subtoit_13 = Subscribed(
        user_id=2,
        subcommon_id=3,
    )
    db.session.add(subtoit_13)

    subtoit_31 = Subscribed(
        user_id=2,
        subcommon_id=1,
    )
    db.session.add(subtoit_31)
    subtoit_32 = Subscribed(
        user_id=2,
        subcommon_id=2,
    )
    db.session.add(subtoit_32)
    subtoit_33 = Subscribed(
        user_id=2,
        subcommon_id=3,
    )
    db.session.add(subtoit_33)

    db.session.commit()


def create_coins():
    coin_1 = Coins(
        id=1,
        image_thumbnail='1',
        created=now,
        coin_name='Starter',
        coin_rarity=2,
        coin_description='Welcome to tipvote',
        points_value=25
    )

    coin_2 = Coins(
        id=2,
        image_thumbnail='2',
        created=now,
        coin_name='tipvote +10',
        coin_rarity=1,
        coin_description='Gives +10 points to a post',
        points_value=10
    )
    coin_3 = Coins(
        id=3,
        image_thumbnail='3',
        created=now,
        coin_name='tipvote +25',
        coin_rarity=1,
        coin_description='Gives +25 points to a post',
        points_value=25
    )
    coin_4 = Coins(
        id=4,
        image_thumbnail='4',
        created=now,
        coin_name='tipvote + 50',
        coin_rarity=2,
        coin_description='Gives +50 points to a post',
        points_value=50
    )
    coin_5 = Coins(
        id=5,
        image_thumbnail='5',
        created=now,
        coin_name='tipvote +5',
        coin_rarity=1,
        coin_description='Gives +5 points to a post',
        points_value=5
    )
    db.session.add(coin_1)
    db.session.add(coin_2)
    db.session.add(coin_3)
    db.session.add(coin_4)
    db.session.add(coin_5)

    db.session.commit()


def create_coin_prices():
    pricebch = BchPrices(
        id=1,
        price=250.00,
    )

    pricebtc = BtcPrices(
        id=1,
        price=10000.00,
    )

    pricexmr = MoneroPrices(
        id=1,
        price=150.00,
    )

    db.session.add(pricebch)
    db.session.add(pricexmr)
    db.session.add(pricebtc)

    db.session.commit()


def create_wallet_fees():
    bchfee = BchWalletFee(
        id=1,
        bch=0.00001,
    )
    db.session.add(bchfee)

    btcfee = BtcWalletFee(
        id=1,
        btc=0.00001,
    )
    db.session.add(btcfee)

    xmrfee = MoneroWalletFee(
        id=1,
        amount=0.00001,
    )
    db.session.add(xmrfee)

    xmrblocks = MoneroBlockHeight(
        id=1,
        blockheight=2229916,
    )
    db.session.add(xmrblocks)

    db.session.commit()


def create_wallet_bch():
    btc_cash_walletcreate_1 = BchWallet(user_id=1,
                                        currentbalance=0,
                                        unconfirmed=0,
                                        address1='',
                                        address1status=0,
                                        address2='',
                                        address2status=0,
                                        address3='',
                                        address3status=0,
                                        locked=0,
                                        transactioncount=0
                                        )
    # add an unconfirmed
    btc_cash_newunconfirmed_1 = BchUnconfirmed(
        user_id=1,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )

    db.session.add(btc_cash_walletcreate_1)
    db.session.add(btc_cash_newunconfirmed_1)

    btc_cash_walletcreate_2 = BchWallet(user_id=2,
                                        currentbalance=0,
                                        unconfirmed=0,
                                        address1='',
                                        address1status=0,
                                        address2='',
                                        address2status=0,
                                        address3='',
                                        address3status=0,
                                        locked=0,
                                        transactioncount=0
                                        )
    # add an unconfirmed
    btc_cash_newunconfirmed_2 = BchUnconfirmed(
        user_id=2,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )

    db.session.add(btc_cash_walletcreate_2)
    db.session.add(btc_cash_newunconfirmed_2)

    btc_cash_walletcreate_3 = BchWallet(user_id=3,
                                        currentbalance=0,
                                        unconfirmed=0,
                                        address1='',
                                        address1status=0,
                                        address2='',
                                        address2status=0,
                                        address3='',
                                        address3status=0,
                                        locked=0,
                                        transactioncount=0
                                        )
    # add an unconfirmed
    btc_cash_newunconfirmed_3 = BchUnconfirmed(
        user_id=3,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )

    db.session.add(btc_cash_walletcreate_3)
    db.session.add(btc_cash_newunconfirmed_3)

    db.session.commit()


def create_wallet_btc():

    btc_walletcreate_1 = BtcWallet(user_id=1,
                                   currentbalance=0,
                                   unconfirmed=0,
                                   address1='',
                                   address1status=1,
                                   address2='',
                                   address2status=0,
                                   address3='',
                                   address3status=0,
                                   locked=0,
                                   transactioncount=0
                                   )
    btc_newunconfirmed_1 = BtcUnconfirmed(
        user_id=1,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(btc_walletcreate_1)
    db.session.add(btc_newunconfirmed_1)

    btc_walletcreate_2 = BtcWallet(user_id=2,
                                   currentbalance=0,
                                   unconfirmed=0,
                                   address1='',
                                   address1status=1,
                                   address2='',
                                   address2status=0,
                                   address3='',
                                   address3status=0,
                                   locked=0,
                                   transactioncount=0
                                   )
    btc_newunconfirmed_2 = BtcUnconfirmed(
        user_id=2,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(btc_walletcreate_2)
    db.session.add(btc_newunconfirmed_2)

    btc_walletcreate_3 = BtcWallet(user_id=3,
                                   currentbalance=0,
                                   unconfirmed=0,
                                   address1='',
                                   address1status=1,
                                   address2='',
                                   address2status=0,
                                   address3='',
                                   address3status=0,
                                   locked=0,
                                   transactioncount=0
                                   )
    btc_newunconfirmed_3 = BtcUnconfirmed(
        user_id=3,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(btc_walletcreate_3)
    db.session.add(btc_newunconfirmed_3)

    db.session.commit()


def create_wallet_xmr():

    monero_walletcreate_1 = MoneroWallet(user_id=1,
                                         currentbalance=0,
                                         unconfirmed=0,
                                         address1='',
                                         address1status=1,
                                         locked=0,
                                         transactioncount=0,
                                         )

    monero_newunconfirmed_1 = MoneroUnconfirmed(
        user_id=1,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(monero_walletcreate_1)
    db.session.commit(monero_newunconfirmed_1)

    monero_walletcreate_2 = MoneroWallet(user_id=2,
                                         currentbalance=0,
                                         unconfirmed=0,
                                         address1='',
                                         address1status=1,
                                         locked=0,
                                         transactioncount=0,
                                         )

    monero_newunconfirmed_2 = MoneroUnconfirmed(
        user_id=2,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(monero_walletcreate_2)
    db.session.commit(monero_newunconfirmed_2)

    monero_walletcreate_3 = MoneroWallet(user_id=3,
                                         currentbalance=0,
                                         unconfirmed=0,
                                         address1='',
                                         address1status=1,
                                         locked=0,
                                         transactioncount=0,
                                         )

    monero_newunconfirmed_3 = MoneroUnconfirmed(
        user_id=3,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )
    db.session.add(monero_walletcreate_3)
    db.session.add(monero_newunconfirmed_3)
    db.session.commit()


if __name__ == '__main':
    createusers()
    create_rooms()
    create_subscriptions()
    create_coins()
    create_coin_prices()
    create_wallet_fees()
    create_wallet_bch()
    create_wallet_btc()
    create_wallet_xmr()

