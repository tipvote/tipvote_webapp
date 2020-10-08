# flask imports
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash
from flask import request
from flask_login import current_user

# general imports
from datetime import datetime
from decimal import Decimal
import re
# common imports
from app import db
from app.common.decorators import login_required
from app.common.functions import floating_decimals
from app.common.validation import btcamount

# relative directory
from app.promote import promote
from app.promote.forms import \
    CreatePromotePostBtc,\
    CreatePromotePostBch,\
    CreatePromotePostXmr,\
    GiveCoin
from app.vote.forms import VoteForm

# other directories
from app.models import\
    UserStatsBTC,\
    UserStatsBCH,\
    UserStatsXMR,\
    BtcWallet,\
    BchWallet,\
    MoneroWallet,\
    CommonsPost, \
    SubForums,\
    BchPrices,\
    MoneroPrices,\
    BtcPrices,\
    UserCoins,\
    PostPromote, \
    PostPromotions, \
    PostCoins

from app.wallet_btc.wallet_btc_promotion import sendcointosite_post_promotion_btc
from app.wallet_bch.wallet_btccash_promotion import sendcointosite_post_promotion_bch
from app.wallet_xmr.wallet_xmr_promotion import sendcointosite_post_promotion_xmr
from app.message.add_notification import add_new_notification


@promote.route('/<string:subname>/<int:postid>', methods=['GET'])
@login_required
def promotepost(subname, postid):
    """
    Promotes a post
    # btc
    """
    form_btc = CreatePromotePostBtc()
    form_bch = CreatePromotePostBch()
    form_xmr = CreatePromotePostXmr()
    voteform = VoteForm()
    givecoinform = GiveCoin()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)

    # queries
    usercoins = db.session.query(UserCoins).filter(UserCoins.user_id == current_user.id).all()

    if thesub is None:

        flash("Sub does not exist.", category="success")
        return redirect(url_for('index'))
    if post is None:
        flash("Post does not exist.", category="success")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
    if post.hidden == 1:
        flash("Post has been removed.", category="success")
        return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
    # get user stats
    return render_template('promote/promote_post.html',
                           # forms
                           form_btc=form_btc,
                           form_bch=form_bch,
                           form_xmr=form_xmr,
                           voteform=voteform,
                           givecoinform=givecoinform,
                           # specific querues
                           thesub=thesub,
                           post=post,
                           usercoins=usercoins
                           )


@promote.route('/coin/<string:subname>/<int:postid>/<int:coinid>', methods=['POST'])
@login_required
def promotepost_coin(subname, postid, coinid):
    """
    Promotes a post
    """

    if request.method == 'POST':

        givecoinform = GiveCoin()

        # get the sub, post, comment
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        post = CommonsPost.query.get(postid)

        if post.shared_post != 0:
            idofpost = post.shared_post
        else:
            idofpost = post.id

        thecoins = PostCoins.query.filter(PostCoins.post_id == idofpost).first()

        if thesub is None:
            flash("Sub does not exist.", category="success")
            return redirect(url_for('index'))
        if post is None:
            flash("Post does not exist.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        if post.hidden == 1:
            flash("Post has been removed.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        # get user stats
        if givecoinform.validate_on_submit():
            usercoin = db.session.query(UserCoins).filter(UserCoins.coin_id == coinid,
                                                          UserCoins.user_id == current_user.id).first()

            if usercoin is not None:
                # give coin to post
                if thecoins is None:
                    newcoinstable = PostCoins(
                        post_id=idofpost,
                        coin_1=0,
                        coin_2=0,
                        coin_3=0,
                        coin_4=0,
                        coin_5=0,
                        coin_6=0,
                        coin_7=0,
                        coin_8=0,
                        coin_9=0,
                        coin_10=0,
                    )
                    db.session.add(newcoinstable)
                    db.session.commit()

                thecoins = PostCoins.query.filter(PostCoins.post_id == idofpost).first_or_404()

                if coinid == 1:
                    new_amount = thecoins.coin_1 + 1
                    thecoins.coin_1 = new_amount
                elif coinid == 2:
                    new_amount = thecoins.coin_2 + 1
                    thecoins.coin_2 = new_amount
                elif coinid == 3:
                    new_amount = thecoins.coin_3 + 1
                    thecoins.coin_3 = new_amount
                elif coinid == 4:
                    new_amount = thecoins.coin_4 + 1
                    thecoins.coin_4 = new_amount
                elif coinid == 5:
                    new_amount = thecoins.coin_5 + 1
                    thecoins.coin_5 = new_amount
                elif coinid == 6:
                    new_amount = thecoins.coin_6 + 1
                    thecoins.coin_6 = new_amount
                elif coinid == 7:
                    new_amount = thecoins.coin_7 + 1
                    thecoins.coin_7 = new_amount
                elif coinid == 8:
                    new_amount = thecoins.coin_8 + 1
                    thecoins.coin_8 = new_amount
                elif coinid == 9:
                    new_amount = thecoins.coin_9 + 1
                    thecoins.coin_9 = new_amount
                else:
                    flash("Coin Does not exist", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                db.session.add(post)

                # subtract or delete users coin

                currentcoinamount = usercoin.quantity - 1

                if currentcoinamount == 0:

                    db.session.delete(usercoin)
                    db.session.commit()
                else:

                    usercoin.quantity = currentcoinamount
                    db.session.add(usercoin)
                    db.session.commit()

                # send notification you got a coin promotion
                add_new_notification(user_id=post.poster_user_id,
                                     subid=post.subcommon_id,
                                     subname=post.subcommon_name,
                                     postid=post.id,
                                     commentid=0,
                                     msg=60,
                                     )

                # commit
                db.session.commit()
                flash("You have promoted the post!", category="success")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
            else:
                flash("You do not have this coin to give", category="success")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
        else:
            flash("Invalid Form", category="success")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@promote.route('/bitcoin/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def promotepost_btc(subname, postid):
    """
    Promotes a post
    # btc
    """
    if request.method == 'POST':
        form_btc = CreatePromotePostBtc()
        now = datetime.utcnow()
        # get the sub, post, comment
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        post = CommonsPost.query.get(postid)
        # see if user has enough
        userwallet_btc = db.session.query(BtcWallet)
        userwallet_btc = userwallet_btc.filter(BtcWallet.user_id == current_user.id)
        userwallet_btc = userwallet_btc.first()

        if post.shared_post != 0:
            idofpost = post.shared_post
        else:
            idofpost = post.id

        seeifpostpromotions = PostPromotions.query.filter(PostPromotions.post_id == idofpost).first()
        if thesub is None:
            flash("That room does not exist", category="success")
            return redirect(url_for('index'))
        if post is None:
            flash("Post does not exist.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        if post.hidden == 1:
            flash("Post has been removed.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        # get user stats
        if form_btc.validate_on_submit():

            # get amount donatred
            getcurrentprice_btc = db.session.query(BtcPrices).get(1)
            btc_current_price_usd = getcurrentprice_btc.price

            # btc
            if form_btc.submit.data:
                seeifcoin = re.compile(btcamount)
                doesitmatch = seeifcoin.match(form_btc.custom_amount.data)
                if doesitmatch:
                    btc_amount_for_submission = Decimal(form_btc.custom_amount.data)
                    decimalform_of_amount = floating_decimals(btc_amount_for_submission, 8)

                    btc_amount = decimalform_of_amount

                    # get usd amount
                    getcurrentprice = db.session.query(BtcPrices).get(1)
                    bt = (Decimal(getcurrentprice.price) * btc_amount)
                    formatteddollar = '{0:.2f}'.format(bt)
                    usd_amount = formatteddollar
                else:
                    flash("Invalid Amount.  Did you not enter the amount correctly?", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))

            elif form_btc.cent_btc.data:
                btc_amount = Decimal(0.01) / Decimal(btc_current_price_usd)
                usd_amount = 0.01

            elif form_btc.quarter_btc.data:
                btc_amount = Decimal(0.25) / Decimal(btc_current_price_usd)
                usd_amount = 0.25

            elif form_btc.dollar_btc.data:
                btc_amount = Decimal(1.00) / Decimal(btc_current_price_usd)
                usd_amount = 1.00

            elif form_btc.five_dollar_btc.data:
                btc_amount = Decimal(5.00) / Decimal(btc_current_price_usd)
                usd_amount = 5.00

            elif form_btc.ten_dollar_btc.data:
                btc_amount = Decimal(10.00) / Decimal(btc_current_price_usd)
                usd_amount = 10.00

            elif form_btc.twentyfive_dollar_btc.data:
                btc_amount = Decimal(25.00) / Decimal(btc_current_price_usd)
                usd_amount = 25.00

            elif form_btc.hundred_dollar_btc.data:
                btc_amount = Decimal(100.00) / Decimal(btc_current_price_usd)
                usd_amount = 100.00

            else:
                flash("Post Promotion Failure.", category="success")
                return redirect(url_for('index'))

            final_amount_btc = (floating_decimals(btc_amount, 8))

            if Decimal(userwallet_btc.currentbalance) >= Decimal(btc_amount):

                if final_amount_btc > 0:

                    createnewpomotion = PostPromote(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        amount_btc=final_amount_btc,
                        amount_xmr=0,
                        amount_bch=0,
                        amount_usd=usd_amount
                    )
                    db.session.add(createnewpomotion)
                    db.session.commit()

                    changeuserbtcstats = db.session.query(UserStatsBTC).filter_by(user_id=current_user.id).first()

                    # create Wallet Transaction for both users
                    sendcointosite_post_promotion_btc(sender_id=current_user.id,
                                                      amount=final_amount_btc,
                                                      postid=postid,
                                                      room=subname)

                    # add stats to user who donated
                    # coin
                    current_amount_donated_to_posts = changeuserbtcstats.total_donated_to_postcomments_btc
                    newamount = (floating_decimals(current_amount_donated_to_posts + final_amount_btc, 8))
                    changeuserbtcstats.total_donated_to_postcomments_btc = newamount
                    # usd
                    current_amount_donated_to_posts_usd = changeuserbtcstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_posts_usd + Decimal(usd_amount), 2))
                    changeuserbtcstats.total_donated_to_postcomments_usd = newamount_usd

                    if seeifpostpromotions is None:
                        addstatstopost = PostPromotions(
                            post_id=idofpost,
                            total_recieved_btc=final_amount_btc,
                            total_recieved_btc_usd=usd_amount,
                            total_recieved_bch=0,
                            total_recieved_bch_usd=0,
                            total_recieved_xmr=0,
                            total_recieved_xmr_usd=0,
                        )

                        db.session.add(addstatstopost)
                    else:

                        # modify comments to show it got btc
                        current_post_btc_amount = seeifpostpromotions.total_recieved_btc
                        current_amount_btc_usd_amount = seeifpostpromotions.total_recieved_btc_usd
                        newamount_for_post = (floating_decimals(current_post_btc_amount + final_amount_btc, 8))
                        newamount_for_post_usd = (floating_decimals(current_amount_btc_usd_amount + Decimal(usd_amount), 2))
                        # set post to active and update post
                        seeifpostpromotions.total_recieved_btc = newamount_for_post
                        seeifpostpromotions.total_recieved_btc_usd = newamount_for_post_usd

                        db.session.add(seeifpostpromotions)

                    post.active = 1
                    post.last_active = now

                    # send notification you got a coin promotion
                    add_new_notification(user_id=post.poster_user_id,
                                         subid=post.subcommon_id,
                                         subname=post.subcommon_name,
                                         postid=post.id,
                                         commentid=0,
                                         msg=61,
                                         )

                    db.session.add(post)
                    db.session.add(changeuserbtcstats)
                    db.session.commit()

                    flash("Successfully Promoted Post with Bitcoin.  In a few minutes the score will be updated.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash(" No Coin Amount given", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
            else:
                flash("Not Enough Coin in your wallet", category="danger")
                return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
        else:
            flash("Invalid Amount", category="danger")
            return redirect(url_for('promote.promotepost', subname=subname, postid=postid))


@promote.route('/bitcoincash/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def promotepost_bch(subname, postid):
    """
    Promotes a post
    # bch
    """
    if request.method == 'POST':
        form_bch = CreatePromotePostBch()
        now = datetime.utcnow()

        # get the sub, post, comment
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        post = db.session.query(CommonsPost).get(postid)

        # see if user has enough
        userwallet_bch = db.session.query(BchWallet)
        userwallet_bch = userwallet_bch.filter(BchWallet.user_id == current_user.id)
        userwallet_bch = userwallet_bch.first()

        # get amount donated
        getcurrentprice_bch = db.session.query(BchPrices).get(1)
        bch_current_price_usd = getcurrentprice_bch.price

        if post.shared_post != 0:
            idofpost = post.shared_post
        else:
            idofpost = post.id

        seeifpostpromotions = PostPromotions.query.filter(PostPromotions.post_id == idofpost).first()
        if thesub is None:
            flash("Sub does not exist.", category="success")
            return redirect(url_for('index'))
        if post is None:
            flash("Post does not exist.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        if post.hidden == 1:
            flash("Post has been removed.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        # get user stats
        if form_bch.validate_on_submit():
            # bch
            if form_bch.submit.data:
                seeifcoin = re.compile(btcamount)
                doesitmatch = seeifcoin.match(form_bch.custom_amount.data)
                if doesitmatch:
                    bch_amount_for_submission = Decimal(form_bch.custom_amount.data)
                    decimalform_of_amount = floating_decimals(bch_amount_for_submission, 8)

                    bch_amount = decimalform_of_amount

                    # get usd amount
                    getcurrentprice = db.session.query(BchPrices).get(1)
                    bt = (Decimal(getcurrentprice.price) * bch_amount)
                    formatteddollar = '{0:.2f}'.format(bt)
                    usd_amount = formatteddollar
                else:
                    flash("Invalid Amount.  Did you not enter the amount correctly?", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))

            elif form_bch.cent_bch.data:
                bch_amount = Decimal(0.01) / Decimal(bch_current_price_usd)
                usd_amount = 0.01

            elif form_bch.quarter_bch.data:
                bch_amount = Decimal(0.25) / Decimal(bch_current_price_usd)
                usd_amount = 0.25

            elif form_bch.dollar_bch.data:
                bch_amount = Decimal(1.00) / Decimal(bch_current_price_usd)
                usd_amount = 1.00

            elif form_bch.five_dollar_bch.data:
                bch_amount = Decimal(5.00) / Decimal(bch_current_price_usd)
                usd_amount = 5.00

            elif form_bch.ten_dollar_bch.data:
                bch_amount = Decimal(10.00) / Decimal(bch_current_price_usd)
                usd_amount = 10.00

            elif form_bch.twentyfive_dollar_bch.data:
                bch_amount = Decimal(25.00) / Decimal(bch_current_price_usd)
                usd_amount = 25.00

            elif form_bch.hundred_dollar_bch.data:
                bch_amount = Decimal(100.00) / Decimal(bch_current_price_usd)
                usd_amount = 100.00
            else:
                flash("Post Promotion Failure.", category="success")
                return redirect(url_for('index'))

            final_amount_bch = (floating_decimals(bch_amount, 8))

            if Decimal(userwallet_bch.currentbalance) >= Decimal(bch_amount):
                if final_amount_bch > 0:

                    createnewpomotion = PostPromote(
                            created=now,
                            created_user_id=current_user.id,
                            created_user_name=current_user.user_name,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=idofpost,
                            amount_bch=final_amount_bch,
                            amount_btc=0,
                            amount_xmr=0,
                            amount_usd=usd_amount
                        )
                    db.session.add(createnewpomotion)
                    db.session.commit()

                    changeuserbchstats = db.session.query(UserStatsBCH).filter_by(user_id=current_user.id).first()

                    # add stats to user who donated
                    # coin
                    current_amount_donated_to_posts = changeuserbchstats.total_donated_to_postcomments_bch
                    newamount = (floating_decimals(current_amount_donated_to_posts + final_amount_bch, 8))
                    changeuserbchstats.total_donated_to_postcomments_bch = newamount
                    # usd
                    current_amount_donated_to_posts_usd = changeuserbchstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_posts_usd + Decimal(usd_amount), 2))
                    changeuserbchstats.total_donated_to_postcomments_usd = newamount_usd

                    if seeifpostpromotions is None:
                        addstatstopost = PostPromotions(
                            post_id=idofpost,
                            total_recieved_bch=final_amount_bch,
                            total_recieved_bch_usd=usd_amount,
                            total_recieved_btc=0,
                            total_recieved_btc_usd=0,
                            total_recieved_xmr=0,
                            total_recieved_xmr_usd=0,
                        )
                        db.session.add(addstatstopost)
                    else:

                        # modify post to show it got bch
                        current_post_bch_amount = seeifpostpromotions.total_recieved_bch
                        current_amount_bch_usd_amount = seeifpostpromotions.total_recieved_bch_usd
                        newamount_for_post = (floating_decimals(current_post_bch_amount + final_amount_bch, 8))
                        newamount_for_post_usd = (floating_decimals(current_amount_bch_usd_amount + Decimal(usd_amount), 2))
                        # set post to active and update post
                        seeifpostpromotions.total_recieved_bch = newamount_for_post
                        seeifpostpromotions.total_recieved_bch_usd = newamount_for_post_usd

                        db.session.add(seeifpostpromotions)

                    # create Wallet Transaction for both users
                    sendcointosite_post_promotion_bch(sender_id=current_user.id,
                                                      amount=final_amount_bch,
                                                      postid=postid,
                                                      room=subname)
                    post.active = 1
                    post.last_active = now

                    db.session.add(post)
                    db.session.add(changeuserbchstats)

                    # send notification you got a coin promotion
                    add_new_notification(user_id=post.poster_user_id,
                                         subid=post.subcommon_id,
                                         subname=post.subcommon_name,
                                         postid=post.id,
                                         commentid=0,
                                         msg=62,
                                         )

                    db.session.commit()

                    flash("Successfully Promoted Post with Bitcoin Cash. In a few minutes the score will be updated.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Invalid Amount", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
            else:
                flash("Not enough coin in your wallet.", category="danger")
                return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
        else:
            flash("Invalid Amount", category="danger")
            return redirect(url_for('promote.promotepost', subname=subname, postid=postid))


@promote.route('/monero/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def promotepost_xmr(subname, postid):
    """
    Promotes a post
    # xmr
    """
    if request.method == 'POST':
        form_xmr = CreatePromotePostXmr()
        now = datetime.utcnow()

        # get the sub, post, comment
        thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
        post = db.session.query(CommonsPost).get(postid)

        # see if user has enough
        userwallet_xmr = db.session.query(MoneroWallet)
        userwallet_xmr = userwallet_xmr.filter(MoneroWallet.user_id == current_user.id)
        userwallet_xmr = userwallet_xmr.first()

        # get amount donated
        getcurrentprice_xmr = db.session.query(MoneroPrices).get(1)
        xmr_current_price_usd = getcurrentprice_xmr.price

        if post.shared_post != 0:
            idofpost = post.shared_post
        else:
            idofpost = post.id

        seeifpostpromotions = PostPromotions.query.\
            filter(PostPromotions.post_id == idofpost)\
            .first()
        if thesub is None:
            flash("Sub does not exist.", category="success")
            return redirect(url_for('index'))
        if post is None:
            flash("Post does not exist.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        if post.hidden == 1:
            flash("Post has been removed.", category="success")
            return redirect(url_for('subforum.sub', subname=thesub.subcommon_name))
        # get user stats
        if form_xmr.validate_on_submit():

            if form_xmr.submit.data:
                seeifcoin = re.compile(btcamount)
                doesitmatch = seeifcoin.match(form_xmr.custom_amount.data)
                if doesitmatch:
                    xmr_amount_for_submission = Decimal(form_xmr.custom_amount.data)
                    decimalform_of_amount = floating_decimals(xmr_amount_for_submission, 12)

                    xmr_amount = decimalform_of_amount

                    # get usd amount
                    getcurrentprice = db.session.query(MoneroPrices).get(1)
                    bt = (Decimal(getcurrentprice.price) * xmr_amount)
                    formatteddollar = '{0:.2f}'.format(bt)
                    usd_amount = formatteddollar
                else:
                    flash("Invalid Amount.  Did you not enter the amount correctly?", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))

            elif form_xmr.cent_xmr.data:
                xmr_amount = Decimal(0.01) / Decimal(xmr_current_price_usd)
                usd_amount = 0.01

            elif form_xmr.quarter_xmr.data:
                xmr_amount = Decimal(0.25) / Decimal(xmr_current_price_usd)
                usd_amount = 0.25

            elif form_xmr.dollar_xmr.data:
                xmr_amount = Decimal(1.00) / Decimal(xmr_current_price_usd)
                usd_amount = 1.00

            elif form_xmr.five_dollar_xmr.data:
                xmr_amount = Decimal(5.00) / Decimal(xmr_current_price_usd)
                usd_amount = 5.00

            elif form_xmr.ten_dollar_xmr.data:
                xmr_amount = Decimal(10.00) / Decimal(xmr_current_price_usd)
                usd_amount = 10.00

            elif form_xmr.twentyfive_dollar_xmr.data:
                xmr_amount = Decimal(25.00) / Decimal(xmr_current_price_usd)
                usd_amount = 25.00

            elif form_xmr.hundred_dollar_xmr.data:
                xmr_amount = Decimal(100.00) / Decimal(xmr_current_price_usd)
                usd_amount = 100.00
            else:
                flash("Post Promotion Failure.", category="success")
                return redirect(url_for('index'))

            final_amount_xmr = (floating_decimals(xmr_amount, 12))

            if Decimal(userwallet_xmr.currentbalance) >= Decimal(xmr_amount):
                if final_amount_xmr > 0:

                    createnewpomotion = PostPromote(
                            created=now,
                            created_user_id=current_user.id,
                            created_user_name=current_user.user_name,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=idofpost,
                            amount_bch=0,
                            amount_btc=0,
                            amount_xmr=final_amount_xmr,
                            amount_usd=usd_amount
                        )
                    db.session.add(createnewpomotion)
                    db.session.commit()

                    changeuserxmrstats = db.session.query(UserStatsXMR)\
                        .filter_by(user_id=current_user.id)\
                        .first()

                    # add stats to user who donated
                    # coin
                    current_amount_donated_to_posts = changeuserxmrstats.total_donated_to_postcomments_xmr
                    newamount = (floating_decimals(current_amount_donated_to_posts + final_amount_xmr, 12))
                    changeuserxmrstats.total_donated_to_postcomments_xmr = newamount
                    # usd
                    current_amount_donated_to_posts_usd = changeuserxmrstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_posts_usd + Decimal(usd_amount), 2))
                    changeuserxmrstats.total_donated_to_postcomments_usd = newamount_usd

                    if seeifpostpromotions is None:
                        addstatstopost = PostPromotions(
                            post_id=idofpost,
                            total_recieved_bch=0,
                            total_recieved_bch_usd=0,
                            total_recieved_btc=0,
                            total_recieved_btc_usd=0,
                            total_recieved_xmr=final_amount_xmr,
                            total_recieved_xmr_usd=usd_amount,
                        )
                        db.session.add(addstatstopost)
                    else:

                        # modify post to show it got xmr
                        current_post_xmr_amount = seeifpostpromotions.total_recieved_xmr
                        current_amount_xmr_usd_amount = seeifpostpromotions.total_recieved_xmr_usd
                        newamount_for_post = (floating_decimals(current_post_xmr_amount + final_amount_xmr, 12))
                        newamount_for_post_usd = (floating_decimals(current_amount_xmr_usd_amount + Decimal(usd_amount), 2))
                        # set post to active and update post
                        seeifpostpromotions.total_recieved_xmr = newamount_for_post
                        seeifpostpromotions.total_recieved_xmr_usd = newamount_for_post_usd

                        db.session.add(seeifpostpromotions)

                    # create Wallet Transaction for both users
                    sendcointosite_post_promotion_xmr(sender_id=current_user.id,
                                                      amount=final_amount_xmr,
                                                      postid=postid,
                                                      room=subname)
                    post.active = 1
                    post.last_active = now

                    db.session.add(post)
                    db.session.add(changeuserxmrstats)

                    # send notification you got a coin promotion
                    add_new_notification(user_id=post.poster_user_id,
                                         subid=post.subcommon_id,
                                         subname=post.subcommon_name,
                                         postid=post.id,
                                         commentid=0,
                                         msg=62,
                                         )

                    db.session.commit()

                    flash("Successfully Promoted Post with Monero. In a few minutes the score will be updated.",
                          category="success")
                    return redirect(url_for('subforum.viewpost',
                                            subname=thesub.subcommon_name,
                                            postid=post.id))
                else:
                    flash("Invalid Amount.", category="danger")
                    return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
            else:
                flash("Not enough coin in your wallet.", category="danger")
                return redirect(url_for('promote.promotepost', subname=subname, postid=postid))
        else:
            flash("Invalid Amount.", category="danger")
            return redirect(url_for('promote.promotepost', subname=subname, postid=postid))


@promote.route('/promotepoints', methods=['GET'])
@login_required
def promotepostpoints():
    """
    Promotes a post
    # btc
    """
    voteform = VoteForm()
    return render_template('promote/promote_post.html',
                           voteform=voteform,
                           )