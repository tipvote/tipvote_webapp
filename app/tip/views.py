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
from app.common.exp_calc import exppoint
from app.message.add_notification import add_new_notification
from app.common.validation import btcamount

# relative directory
from app.tip import tip
from app.tip.forms import \
    CreateTipBTC, \
    CreateTipBCH, \
    CreateTipXMR
from app.vote.forms import VoteForm
from app.models import \
    BtcCommentTips, \
    XmrCommentTips, \
    BtcPostTips, \
    XmrPostTips, \
    BchCommentTips, \
    BchPostTips, \
    RecentTips, \
    UserStatsBCH, \
    UserStatsXMR, \
    UserStatsBTC, \
    BchPrices, \
    MoneroPrices, \
    BtcPrices, \
    BtcWallet, \
    MoneroWallet, \
    BchWallet, \
    Comments, \
    CommonsPost, \
    SubForums, \
    PostDonations,\
    PayoutSubOwner

# wallet imports
from app.wallet_btc.wallet_btc_tips import \
    take_coin_from_tipper_btc_comment, sendcoin_subowner_btc_comment, sendcoin_to_poster_btc_comment, \
    take_coin_from_tipper_btc_post, sendcoin_subowner_btc_post, sendcoin_to_poster_btc_post


from app.wallet_bch.wallet_bch_tips import \
    take_coin_from_tipper_bch_comment, sendcoin_subowner_bch_comment, sendcoin_to_poster_bch_comment, \
    take_coin_from_tipper_bch_post, sendcoin_subowner_bch_post, sendcoin_to_poster_bch_post


from app.wallet_xmr.wallet_xmr_tips import \
    take_coin_from_tipper_xmr_comment, sendcoin_subowner_xmr_comment, sendcoin_to_poster_xmr_comment, \
    take_coin_from_tipper_xmr_post, sendcoin_subowner_xmr_post, sendcoin_to_poster_xmr_post


@tip.route('/comment/<string:subname>/<int:postid>/<int:commentid>', methods=['GET'])
@login_required
def create_tip_comment(subname, postid, commentid):
    voteform = VoteForm()
    form_btc = CreateTipBTC()
    form_bch = CreateTipBCH()
    form_xmr = CreateTipXMR()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    thepost = db.session.query(CommonsPost).get(postid)
    thecomment = db.session.query(Comments).get(commentid)
    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if thepost is None:
        flash("The post has been removed or doesnt exist")
        return redirect((request.args.get('next', request.referrer)))
    if thecomment is None:
        flash("Comment doesnt exist or has been removed")
        return redirect((request.args.get('next', request.referrer)))
    if thepost.hidden == 1:
        flash("Post Has been deleted")
        return redirect((request.args.get('next', request.referrer)))

    return render_template('tips/tip_comment/tip_comment.html',
                           # forms
                           form_btc=form_btc,
                           voteform=voteform,
                           form_bch=form_bch,
                           form_xmr=form_xmr,
                           # specific querues
                           thesub=thesub,
                           thepost=thepost,
                           thecomment=thecomment,
                           )


@tip.route('/post/<string:subname>/<int:postid>', methods=['GET'])
@login_required
def create_tip_post(subname, postid):
    form_btc = CreateTipBTC()
    form_bch = CreateTipBCH()
    form_xmr = CreateTipXMR()
    voteform = VoteForm()
    # get the sub, post
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted")
        return redirect((request.args.get('next', request.referrer)))

    return render_template('tips/tip_post/tip_post.html',
                           # forms
                           form_btc=form_btc,
                           voteform=voteform,
                           form_bch=form_bch,
                           form_xmr=form_xmr,
                           # specific querues
                           thesub=thesub,
                           post=post,

                           )


@tip.route('/createbtctip/comment/<string:subname>/<int:postid>/<int:commentid>', methods=['POST'])
@login_required
def create_tip_comment_btc(subname, postid, commentid):
    """
    Creates a btc tip for a comment
    """
    form_btc = CreateTipBTC()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)
    thecomment = db.session.query(Comments).get(commentid)

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if thecomment is None:
        flash("Comment doesnt exist or has been removed", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    if request.method == 'POST':
        if form_btc.validate_on_submit():
            if thecomment.user_id != current_user.id:

                userwallet_btc = db.session.query(BtcWallet)
                userwallet_btc = userwallet_btc.filter(BtcWallet.user_id == current_user.id)
                userwallet_btc = userwallet_btc.first()

                # get user stats
                changeuserbtcstats = db.session.query(UserStatsBTC).filter_by(user_id=current_user.id).first()
                changeposterbtcstats = db.session.query(UserStatsBTC).filter_by(user_id=thecomment.user_id).first()

                # get amount donatred
                getcurrentprice = db.session.query(BtcPrices).get(1)
                btc_current_price_usd = getcurrentprice.price

                if form_btc.submit.data:
                    seeifcoin = re.compile(btcamount)
                    doesitmatch = seeifcoin.match(form_btc.custom_amount.data)
                    if doesitmatch:

                        btc_amount_for_submission = Decimal(form_btc.custom_amount.data)
                        decimalform_of_amount = floating_decimals(btc_amount_for_submission, 8)
                        # see if user has enough
                        getcurrentprice = db.session.query(BtcPrices).get(1)
                        btc_amount = decimalform_of_amount

                        # get usd amount
                        bt = (Decimal(getcurrentprice.price) * btc_amount)
                        formatteddollar = '{0:.2f}'.format(bt)
                        usd_amount = formatteddollar
                    else:
                        flash("Form Failure.  Did you enter the amount correctly?", category="success")
                        return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))
                elif form_btc.cent.data:
                    btc_amount = Decimal(0.01) / Decimal(btc_current_price_usd)
                    usd_amount = 0.01
                elif form_btc.quarter.data:
                    btc_amount = Decimal(0.25) / Decimal(btc_current_price_usd)
                    usd_amount = 0.25
                elif form_btc.dollar.data:
                    btc_amount = Decimal(1.00) / Decimal(btc_current_price_usd)
                    usd_amount = 1.00
                elif form_btc.five_dollar.data:
                    btc_amount = Decimal(5.00) / Decimal(btc_current_price_usd)
                    usd_amount = 5.00
                elif form_btc.ten_dollar.data:
                    btc_amount = Decimal(10.00) / Decimal(btc_current_price_usd)
                    usd_amount = 10.00
                elif form_btc.twentyfive_dollar.data:
                    btc_amount = Decimal(25.00) / Decimal(btc_current_price_usd)
                    usd_amount = 25.00
                elif form_btc.hundred_dollar.data:
                    btc_amount = Decimal(100.00) / Decimal(btc_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Tip Failure.", category="success")
                    return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))

                final_amount = (floating_decimals(btc_amount, 8))

                lowestdonation = 0.000001
                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(userwallet_btc.currentbalance) >= Decimal(btc_amount):

                    # btc amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = subownerformatteddollar

                    # Btc amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * btc_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = posterformatteddollar
                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=thecomment.id,
                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,
                            currency_type=1,
                            amount_btc=amount_to_subowner,
                            amount_bch=0,
                            amount_xmr=0,
                            amount_usd=subowner_usd_amount,
                        )

                        db.session.add(newpayout)

                    # poster gets payout
                    createnewtip = BtcCommentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=thecomment.user_id,
                        recieved_user_name=thecomment.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        amount_btc=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=thecomment.user_id,
                        recieved_user_name=thecomment.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        currency_type=1,
                        amount_btc=amount_to_poster,
                        amount_xmr=0,
                        amount_bch=0,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user who donated
                    current_amount_donated_to_comments = changeuserbtcstats.total_donated_to_postcomments_btc
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserbtcstats.total_donated_to_postcomments_btc = newamount
                    current_amount_donated_to_comments_usd = changeuserbtcstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserbtcstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_comments = changeposterbtcstats.total_recievedfromcomments_btc
                    newamount_commenter = (floating_decimals(current_amount_recieved_to_comments + amount_to_poster, 8))
                    changeposterbtcstats.total_recievedfromcomments_btc = newamount_commenter
                    current_amount_recieved_to_comments_usd = changeposterbtcstats.total_recievedfromcomments_usd
                    newamount_commenter_usd = (floating_decimals(current_amount_recieved_to_comments_usd + Decimal(poster_usd_amount), 2))
                    changeposterbtcstats.total_recievedfromcomments_usd = newamount_commenter_usd

                    # modify comments to show it got btc
                    current_comment_btc_amount = thecomment.total_recieved_btc
                    current_comment_btc_usd_amount = thecomment.total_recieved_btc_usd
                    newamount_for_comment = (floating_decimals(current_comment_btc_amount + amount_to_poster, 8))
                    newamount_for_comment_usd = (floating_decimals(current_comment_btc_usd_amount + Decimal(poster_usd_amount), 2))
                    thecomment.total_recieved_btc = newamount_for_comment
                    thecomment.total_recieved_btc_usd = newamount_for_comment_usd

                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=thecomment.id,
                                             msg=15
                                             )

                    add_new_notification(user_id=thecomment.user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=post.id,
                                         commentid=thecomment.id,
                                         msg=4
                                         )

                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=thecomment.user_id, type=6)

                    take_coin_from_tipper_btc_comment(sender_id=current_user.id,
                                                      amount=final_amount,
                                                      commentid=thecomment.id,
                                                      recieverid=thecomment.id
                                                      )

                    # create Wallet Transaction for reciever (post creator)
                    sendcoin_to_poster_btc_comment(sender_id=current_user.id,
                                                   amount=amount_to_poster,
                                                   commentid=thecomment.id,
                                                   recieverid=thecomment.user_id
                                                   )

                    if payout == 1:
                        # create Wallet Transaction for subowner
                        sendcoin_subowner_btc_comment(sender_id=current_user.id,
                                                      amount=amount_to_subowner,
                                                      commentid=thecomment.id,
                                                      recieverid=thesub.creator_user_id
                                                      )
                    post.last_active = now
                    post.active = 1

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(thecomment)
                    db.session.add(changeposterbtcstats)
                    db.session.add(changeuserbtcstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("You do not have enough coin in your wallet", category="danger")
                    return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))
            else:
                flash("Cannot tip yourself.  You can only promote your own posts for better visibility.", category="danger")
                return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))
        else:
            flash("Invalid Form.  Did you enter the amount correctly?", category="danger")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))

    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@tip.route('/createbtctip/post/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def create_tip_post_btc(subname, postid):
    """
    Creates a btc tip for a post
    """
    form_btc = CreateTipBTC()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()

    post = db.session.query(CommonsPost).get(postid)

    if post.shared_post != 0:
        idofpost = post.shared_post
    else:
        idofpost = post.id

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    # get user stats
    changeuserbtcstats = db.session.query(UserStatsBTC).filter_by(user_id=current_user.id).first()
    # get poster stats
    changeposterbtcstats = db.session.query(UserStatsBTC).filter_by(user_id=post.content_user_id).first()

    if request.method == 'POST':
        if form_btc.validate_on_submit():

            # check to see if tipper != poster
            if post.content_user_id != current_user.id:

                # see if user has enough
                userwallet_btc = db.session.query(BtcWallet)
                userwallet_btc = userwallet_btc.filter(BtcWallet.user_id == current_user.id)
                userwallet_btc = userwallet_btc.first()

                # get amount donated
                getcurrentprice = db.session.query(BtcPrices).get(1)
                btc_current_price_usd = getcurrentprice.price

                if form_btc.submit.data:
                    seeifcoin = re.compile(btcamount)
                    doesitmatch = seeifcoin.match(form_btc.custom_amount.data)
                    if doesitmatch:
                        btc_amount_for_submission = Decimal(form_btc.custom_amount.data)
                        decimalform_of_amount = floating_decimals(btc_amount_for_submission, 8)
                        btc_amount = decimalform_of_amount
                        # get usd amount
                        bt = (Decimal(getcurrentprice.price) * btc_amount)
                        formatteddollar = '{0:.2f}'.format(bt)
                        usd_amount = formatteddollar
                    else:
                        flash("Invalid coin amount.  Did you enter the amount wrong?", category="danger")
                        return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                elif form_btc.cent.data:
                    btc_amount = Decimal(0.01) / Decimal(btc_current_price_usd)
                    usd_amount = 0.01
                elif form_btc.quarter.data:
                    btc_amount = Decimal(0.25) / Decimal(btc_current_price_usd)
                    usd_amount = 0.25
                elif form_btc.dollar.data:
                    btc_amount = Decimal(1.00) / Decimal(btc_current_price_usd)
                    usd_amount = 1.00
                elif form_btc.five_dollar.data:
                    btc_amount = Decimal(5.00) / Decimal(btc_current_price_usd)
                    usd_amount = 5.00
                elif form_btc.ten_dollar.data:
                    btc_amount = Decimal(10.00) / Decimal(btc_current_price_usd)
                    usd_amount = 10.00
                elif form_btc.twentyfive_dollar.data:
                    btc_amount = Decimal(25.00) / Decimal(btc_current_price_usd)
                    usd_amount = 25.00
                elif form_btc.hundred_dollar.data:
                    btc_amount = Decimal(100.00) / Decimal(btc_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Tip Failure.", category="success")
                    return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                final_amount = (floating_decimals(btc_amount, 8))

                lowestdonation = 0.000001

                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(userwallet_btc.currentbalance) >= Decimal(btc_amount):
                    # btc amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = subownerformatteddollar

                    # Btc amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * btc_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = posterformatteddollar

                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=0,
                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,
                            currency_type=1,
                            amount_btc=amount_to_subowner,
                            amount_bch=0,
                            amount_xmr=0,
                            amount_usd=subowner_usd_amount,
                        )
                        db.session.add(newpayout)

                    createnewtip = BtcPostTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        amount_btc=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        comment_id=0,
                        currency_type=1,
                        amount_btc=amount_to_poster,
                        amount_bch=0,
                        amount_xmr=0,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user who donated
                    current_amount_donated_to_comments = changeuserbtcstats.total_donated_to_postcomments_btc
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserbtcstats.total_donated_to_postcomments_btc = newamount
                    current_amount_donated_to_comments_usd = changeuserbtcstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserbtcstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_posts = changeposterbtcstats.total_recievedfromposts_btc
                    newamount_poster = (floating_decimals(current_amount_recieved_to_posts + amount_to_poster, 8))
                    changeposterbtcstats.total_recievedfromposts_btc = newamount_poster
                    current_amount_recieved_to_posts_usd = changeposterbtcstats.total_recievedfromposts_usd
                    newamount_poster_usd = (floating_decimals(current_amount_recieved_to_posts_usd + Decimal(poster_usd_amount), 2))
                    changeposterbtcstats.total_recievedfromposts_usd = newamount_poster_usd

                    seeifpostdonates = PostDonations.query.filter(PostDonations.post_id == idofpost).first()

                    if seeifpostdonates is None:
                        addstatstopost = PostDonations(
                            post_id=idofpost,
                            total_recieved_btc=final_amount,
                            total_recieved_btc_usd=usd_amount,
                            total_recieved_bch=0,
                            total_recieved_bch_usd=0,
                            total_recieved_xmr=0,
                            total_recieved_xmr_usd=0,
                        )
                        db.session.add(addstatstopost)

                    else:
                        # modify comments to show it got btc
                        current_post_btc_amount = seeifpostdonates.total_recieved_btc
                        current_amount_btc_usd_amount = seeifpostdonates.total_recieved_btc_usd
                        newamount_for_post = (floating_decimals(current_post_btc_amount + amount_to_poster, 8))
                        newamount_for_post_usd = (floating_decimals(current_amount_btc_usd_amount + Decimal(poster_usd_amount), 2))
                        seeifpostdonates.total_recieved_btc = newamount_for_post
                        seeifpostdonates.total_recieved_btc_usd = newamount_for_post_usd

                        db.session.add(seeifpostdonates)

                    add_new_notification(user_id=post.content_user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=idofpost,
                                         commentid=0,
                                         msg=2)
                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=0,
                                             msg=15
                                             )

                    take_coin_from_tipper_btc_post(sender_id=current_user.id,
                                                   amount=final_amount,
                                                   postid=idofpost,
                                                   recieverid=post.content_user_id
                                                   )

                    sendcoin_to_poster_btc_post(sender_id=current_user.id,
                                                amount=amount_to_poster,
                                                postid=idofpost,
                                                recieverid=post.content_user_id
                                                )

                    if payout == 1:
                        sendcoin_subowner_btc_post(sender_id=current_user.id,
                                                   amount=amount_to_subowner,
                                                   postid=idofpost,
                                                   recieverid=thesub.creator_user_id
                                                   )
                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=post.content_user_id, type=6)

                    post.last_active = now
                    post.active = 1

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(post)
                    db.session.add(changeposterbtcstats)
                    db.session.add(changeuserbtcstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Insufficient coin in your wallet.", category="danger")
                    return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))
            else:
                flash("Cannot tip yourself.  You can only promote your posts.", category="danger")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
        else:
            flash("Invalid form...did you enter amount correctly?", category="success")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@tip.route('/createxmrtip/comment/<string:subname>/<int:postid>/<int:commentid>', methods=['POST'])
@login_required
def create_tip_comment_xmr(subname, postid, commentid):
    """
    Creates a xmr tip for a comment
    """
    form_xmr = CreateTipXMR()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums) \
        .filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)
    thecomment = db.session.query(Comments).get(commentid)

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if thecomment is None:
        flash("Comment doesnt exist or has been removed", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    # get user stats
    changeuserxmrstats = db.session.query(UserStatsXMR).filter_by(user_id=current_user.id).first()
    changecommenterxmrstats = db.session.query(UserStatsXMR).filter_by(user_id=thecomment.user_id).first()

    if request.method == 'POST':
        if form_xmr.validate_on_submit():

            # check to see if tipper != poster
            if thecomment.user_id != current_user.id:

                usercoinsamount = db.session.query(MoneroWallet)
                usercoinsamount = usercoinsamount.filter(MoneroWallet.user_id == current_user.id)
                usercoinsamount = usercoinsamount.first()

                # get amount donated
                getcurrentprice = db.session.query(MoneroPrices).get(1)
                xmr_current_price_usd = getcurrentprice.price

                if form_xmr.submit.data:
                    # regex test
                    seeifcoin = re.compile(btcamount)
                    doesitmatch = seeifcoin.match(form_xmr.custom_amount.data)
                    if doesitmatch:
                        # if it passes
                        xmr_amount_for_submission = Decimal(form_xmr.custom_amount.data)
                        decimalform_of_amount = floating_decimals(xmr_amount_for_submission, 8)
                        #
                        xmr_amount = decimalform_of_amount
                        # get usd amount
                        bt = (Decimal(getcurrentprice.price) * xmr_amount)
                        formatteddollar = '{0:.2f}'.format(bt)
                        usd_amount = formatteddollar
                    else:
                        flash("Invalid coin amount", category="danger")
                        return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                elif form_xmr.cent.data:
                    xmr_amount = Decimal(0.01) / Decimal(xmr_current_price_usd)
                    usd_amount = 0.01
                elif form_xmr.quarter.data:
                    xmr_amount = Decimal(0.25) / Decimal(xmr_current_price_usd)
                    usd_amount = 0.25
                elif form_xmr.dollar.data:
                    xmr_amount = Decimal(1.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 1.00
                elif form_xmr.five_dollar.data:
                    xmr_amount = Decimal(5.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 5.00
                elif form_xmr.ten_dollar.data:
                    xmr_amount = Decimal(10.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 10.00
                elif form_xmr.twentyfive_dollar.data:
                    xmr_amount = Decimal(25.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 25.00
                elif form_xmr.hundred_dollar.data:
                    xmr_amount = Decimal(100.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Tip Failure.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))

                final_amount = (floating_decimals(xmr_amount, 8))

                lowestdonation = 0.000001
                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(usercoinsamount.currentbalance) >= Decimal(final_amount):
                    # btc amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = subownerformatteddollar

                    # Btc amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * xmr_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = posterformatteddollar

                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=thecomment.id,

                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,

                            currency_type=3,
                            amount_btc=0,
                            amount_bch=0,
                            amount_xmr=amount_to_subowner,
                            amount_usd=subowner_usd_amount,
                        )
                        db.session.add(newpayout)

                    createnewtip = XmrCommentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=thecomment.user_id,
                        recieved_user_name=thecomment.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        amount_xmr=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )
                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.user_id,
                        recieved_user_name=post.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        currency_type=2,
                        amount_btc=0,
                        amount_bch=0,
                        amount_xmr=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user
                    current_amount_donated_to_comments = changeuserxmrstats.total_donated_to_postcomments_xmr
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserxmrstats.total_donated_to_postcomments_xmr = newamount
                    current_amount_donated_to_comments_usd = changeuserxmrstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserxmrstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_comments = changecommenterxmrstats.total_recievedfromcomments_xmr
                    newamount_poster = (floating_decimals(current_amount_recieved_to_comments + amount_to_poster, 8))
                    changecommenterxmrstats.total_recievedfromcomments_xmr = newamount_poster
                    current_amount_recieved_to_comments_usd = changecommenterxmrstats.total_recievedfromcomments_usd
                    newamount_poster_usd = (floating_decimals(current_amount_recieved_to_comments_usd + Decimal(poster_usd_amount), 2))
                    changecommenterxmrstats.total_recievedfromcomments_usd = newamount_poster_usd

                    # modify comments to show it got xmr
                    current_comment_xmr_amount = thecomment.total_recieved_xmr
                    current_comment_xmr_usd_amount = thecomment.total_recieved_xmr_usd
                    newamount_for_comment = (floating_decimals(current_comment_xmr_amount + amount_to_poster, 8))
                    newamount_for_comment_usd = (floating_decimals(current_comment_xmr_usd_amount + Decimal(poster_usd_amount), 2))
                    thecomment.total_recieved_xmr = newamount_for_comment
                    thecomment.total_recieved_xmr_usd = newamount_for_comment_usd

                    add_new_notification(user_id=post.user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=post.id,
                                         commentid=thecomment.id,
                                         msg=5
                                         )
                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=0,
                                             msg=15
                                             )

                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=thecomment.user_id, type=6)

                    take_coin_from_tipper_xmr_comment(sender_id=current_user.id,
                                                      amount=final_amount,
                                                      commentid=thecomment.id,
                                                      recieverid=thecomment.id
                                                      )

                    # create Wallet Transaction for reciever (post creator)
                    sendcoin_to_poster_xmr_comment(sender_id=current_user.id,
                                                   amount=amount_to_poster,
                                                   commentid=thecomment.id,
                                                   recieverid=thecomment.user_id
                                                   )
                    if payout == 1:
                        # create Wallet Transaction for subowner
                        sendcoin_subowner_xmr_comment(sender_id=current_user.id,
                                                      amount=amount_to_subowner,
                                                      commentid=thecomment.id,
                                                      recieverid=thesub.creator_user_id
                                                      )

                    post.last_active = now
                    post.active = 1

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(post)
                    db.session.add(thecomment)
                    db.session.add(changecommenterxmrstats)
                    db.session.add(changeuserxmrstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Insufficient Funds.", category="danger")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
            else:
                flash("Cannot tip yourself", category="success")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
        else:
            flash("Invalid Form", category="success")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@tip.route('/createxmrtip/post/<string:subname>/<int:postid>',methods=['POST'])
@login_required
def create_tip_post_xmr(subname, postid):
    """
    Creates a xmr tip for a post
    """
    form_xmr = CreateTipXMR()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)

    if post.shared_post != 0:
        idofpost = post.shared_post
    else:
        idofpost = post.id

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    # get user stats
    changeuserxmrstats = db.session.query(UserStatsXMR).filter_by(user_id=current_user.id).first()
    changeposterxmrstats = db.session.query(UserStatsXMR).filter_by(user_id=post.content_user_id).first()

    if request.method == 'POST':
        if form_xmr.validate_on_submit():

            # check to see if tipper != poster
            if post.user_id != current_user.id:

                # SECURITY - see if user has enough coins
                usercoinsamount = db.session.query(MoneroWallet)
                usercoinsamount = usercoinsamount.filter(MoneroWallet.user_id == current_user.id)
                usercoinsamount = usercoinsamount.first()

                # get amount donatred
                getcurrentprice = db.session.query(MoneroPrices).get(1)
                xmr_current_price_usd = getcurrentprice.price

                if form_xmr.submit.data:
                    # run regex to see if not being tricked
                    seeifcoin = re.compile(btcamount)
                    doesitmatch = seeifcoin.match(form_xmr.custom_amount.data)
                    if doesitmatch:
                        # if it passes regex test
                        xmr_amount_for_submission = Decimal(form_xmr.custom_amount.data)
                        decimalform_of_amount = floating_decimals(xmr_amount_for_submission, 12)
                        xmr_amount = decimalform_of_amount
                        # get usd amount
                        bt = (Decimal(getcurrentprice.price) * xmr_amount)
                        formatteddollar = '{0:.2f}'.format(bt)
                        usd_amount = formatteddollar
                    else:
                        flash("Invalid coin amount.  Did you enter the amount wrong?", category="danger")
                        return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                elif form_xmr.cent.data:
                    xmr_amount = Decimal(0.01) / Decimal(xmr_current_price_usd)
                    usd_amount = 0.01
                elif form_xmr.quarter.data:
                    xmr_amount = Decimal(0.25) / Decimal(xmr_current_price_usd)
                    usd_amount = 0.25
                elif form_xmr.dollar.data:
                    xmr_amount = Decimal(1.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 1.00
                elif form_xmr.five_dollar.data:
                    xmr_amount = Decimal(5.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 5.00
                elif form_xmr.ten_dollar.data:
                    xmr_amount = Decimal(10.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 10.00
                elif form_xmr.twentyfive_dollar.data:
                    xmr_amount = Decimal(25.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 25.00
                elif form_xmr.hundred_dollar.data:
                    xmr_amount = Decimal(100.00) / Decimal(xmr_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Invalid coin amount.  Did you enter the amount wrong?", category="danger")
                    return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                final_amount = (floating_decimals(xmr_amount, 12))

                lowestdonation = 0.000001

                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(usercoinsamount.currentbalance) >= Decimal(xmr_amount):

                    # xmr amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = float(subownerformatteddollar)

                    # xmr amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * xmr_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = float(posterformatteddollar)

                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=0,
                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,
                            currency_type=3,
                            amount_btc=0,
                            amount_bch=0,
                            amount_xmr=amount_to_subowner,
                            amount_usd=subowner_usd_amount,
                        )
                        db.session.add(newpayout)

                    createnewtip = XmrPostTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        amount_xmr=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        comment_id=0,
                        currency_type=3,
                        amount_btc=0,
                        amount_bch=0,
                        amount_xmr=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user
                    # coin
                    current_amount_donated_to_comments = changeuserxmrstats.total_donated_to_postcomments_xmr
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserxmrstats.total_donated_to_postcomments_xmr = newamount
                    current_amount_donated_to_comments_usd = changeuserxmrstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserxmrstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_posts = changeposterxmrstats.total_recievedfromposts_xmr
                    newamount_poster = (floating_decimals(current_amount_recieved_to_posts + amount_to_poster, 8))
                    changeposterxmrstats.total_recievedfromposts_xmr = newamount_poster
                    current_amount_recieved_to_posts_usd = changeposterxmrstats.total_recievedfromposts_usd
                    newamount_poster_usd = (floating_decimals(current_amount_recieved_to_posts_usd + Decimal(poster_usd_amount), 2))
                    changeposterxmrstats.total_recievedfromposts_usd = newamount_poster_usd

                    # add to posts
                    seeifpostdonates = PostDonations.query\
                        .filter(PostDonations.post_id == idofpost)\
                        .first()

                    if seeifpostdonates is None:
                        addstatstopost = PostDonations(
                            post_id=idofpost,
                            total_recieved_btc=0,
                            total_recieved_btc_usd=0,
                            total_recieved_bch=0,
                            total_recieved_bch_usd=0,
                            total_recieved_xmr=final_amount,
                            total_recieved_xmr_usd=usd_amount,
                        )
                        db.session.add(addstatstopost)
                    else:
                        # modify comments to show it got xmr
                        current_post_xmr_amount = seeifpostdonates.total_recieved_xmr
                        current_amount_xmr_usd_amount = seeifpostdonates.total_recieved_xmr_usd
                        newamount_for_post = (floating_decimals(current_post_xmr_amount + amount_to_poster, 8))
                        newamount_for_post_usd = (floating_decimals(current_amount_xmr_usd_amount + Decimal(poster_usd_amount), 2))
                        seeifpostdonates.total_recieved_xmr = newamount_for_post
                        seeifpostdonates.total_recieved_xmr_usd = newamount_for_post_usd

                        db.session.add(seeifpostdonates)

                    add_new_notification(user_id=post.content_user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=idofpost,
                                         commentid=0,
                                         msg=3
                                         )

                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=0,
                                             msg=15
                                             )

                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=post.content_user_id, type=6)

                    post.last_active = now
                    post.active = 1

                    # create Wallet Transaction for both users
                    take_coin_from_tipper_xmr_post(sender_id=current_user.id,
                                                   amount=final_amount,
                                                   postid=idofpost,
                                                   recieverid=post.content_user_id
                                                   )

                    # create Wallet Transaction for both users
                    sendcoin_to_poster_xmr_post(sender_id=current_user.id,
                                                amount=amount_to_poster,
                                                postid=idofpost,
                                                recieverid=post.content_user_id
                                                )

                    if payout == 1:
                        # create Wallet Transaction for both users
                        sendcoin_subowner_xmr_post(sender_id=current_user.id,
                                                   amount=amount_to_subowner,
                                                   postid=idofpost,
                                                   recieverid=thesub.creator_user_id
                                                   )

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(post)
                    db.session.add(changeposterxmrstats)
                    db.session.add(changeuserxmrstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Not enough coin in your wallet.", category="danger")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
            else:
                flash("Cannot tip yourself.", category="danger")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
        else:
            flash("Invalid Form.  Did you enter the amount correctly?", category="danger")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@tip.route('/createbchtip/comment/<string:subname>/<int:postid>/<int:commentid>', methods=['POST'])
@login_required
def create_tip_comment_bch(subname, postid, commentid):
    """
    Creates a btc tip for a comment
    """
    form_bch = CreateTipBCH()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)
    thecomment = db.session.query(Comments).get(commentid)

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if thecomment is None:
        flash("Comment doesnt exist or has been removed", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    # get user stats
    changeuserbchstats = db.session.query(UserStatsBCH).filter(UserStatsBCH.user_id == current_user.id).first()
    changeposterbchstats = db.session.query(UserStatsBCH).filter(UserStatsBCH.user_id == thecomment.user_id).first()

    if request.method == 'POST':
        if form_bch.validate_on_submit():

            userwallet_bch = db.session.query(BchWallet)
            userwallet_bch = userwallet_bch.filter(BchWallet.user_id == current_user.id)
            userwallet_bch = userwallet_bch.first()

            if thecomment.user_id != current_user.id:

                # get amount donatred
                getcurrentprice = db.session.query(BchPrices).get(1)
                bch_current_price_usd = getcurrentprice.price

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
                        flash("Invalid coin amount", category="danger")
                        return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                elif form_bch.cent.data:
                    bch_amount = Decimal(0.01) / Decimal(bch_current_price_usd)
                    usd_amount = 0.01
                elif form_bch.quarter.data:
                    bch_amount = Decimal(0.25) / Decimal(bch_current_price_usd)
                    usd_amount = 0.25
                elif form_bch.dollar.data:
                    bch_amount = Decimal(1.00) / Decimal(bch_current_price_usd)
                    usd_amount = 1.00
                elif form_bch.five_dollar.data:
                    bch_amount = Decimal(5.00) / Decimal(bch_current_price_usd)
                    usd_amount = 5.00
                elif form_bch.ten_dollar.data:
                    bch_amount = Decimal(10.00) / Decimal(bch_current_price_usd)
                    usd_amount = 10.00
                elif form_bch.twentyfive_dollar.data:
                    bch_amount = Decimal(25.00) / Decimal(bch_current_price_usd)
                    usd_amount = 25.00
                elif form_bch.hundred_dollar.data:
                    bch_amount = Decimal(100.00) / Decimal(bch_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Tip Failure.", category="success")
                    return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))

                final_amount = (floating_decimals(bch_amount, 8))

                lowestdonation = 0.000001
                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(userwallet_bch.currentbalance) > Decimal(final_amount):

                    # btc amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = subownerformatteddollar

                    # Btc amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * bch_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = posterformatteddollar

                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=thecomment.id,

                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,

                            currency_type=2,
                            amount_btc=0,
                            amount_bch=amount_to_subowner,
                            amount_xmr=0,
                            amount_usd=subowner_usd_amount,
                        )
                        db.session.add(newpayout)

                    createnewtip = BchCommentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=thecomment.user_id,
                        recieved_user_name=thecomment.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        amount_bch=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=thecomment.user_id,
                        recieved_user_name=thecomment.user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=post.id,
                        comment_id=thecomment.id,
                        currency_type=2,
                        amount_btc=0,
                        amount_bch=amount_to_poster,
                        amount_xmr=0,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user
                    current_amount_donated_to_comments = changeuserbchstats.total_donated_to_postcomments_bch
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserbchstats.total_donated_to_postcomments_bch = newamount
                    current_amount_donated_to_comments_usd = changeuserbchstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserbchstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_comments = changeposterbchstats.total_recievedfromcomments_bch
                    newamount_commenter = (floating_decimals(current_amount_recieved_to_comments + amount_to_poster, 8))
                    changeposterbchstats.total_recievedfromcomments_bch = newamount_commenter
                    current_amount_recieved_to_comments_usd = changeposterbchstats.total_recievedfromcomments_usd
                    newamount_commenter_usd = (floating_decimals(current_amount_recieved_to_comments_usd + Decimal(poster_usd_amount), 2))
                    changeposterbchstats.total_recievedfromcomments_usd = newamount_commenter_usd

                    # modify comments to show it got btc
                    current_comment_bch_amount = thecomment.total_recieved_bch
                    current_comment_bch_usd_amount = thecomment.total_recieved_bch_usd
                    newamount_for_comment = (floating_decimals(current_comment_bch_amount + amount_to_poster, 8))
                    newamount_for_comment_usd = (floating_decimals(current_comment_bch_usd_amount + Decimal(poster_usd_amount), 2))
                    thecomment.total_recieved_bch = newamount_for_comment
                    thecomment.total_recieved_bch_usd = newamount_for_comment_usd

                    add_new_notification(user_id=thecomment.user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=post.id,
                                         commentid=thecomment.id,
                                         msg=4
                                         )

                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=thecomment.id,
                                             msg=15
                                             )

                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=thecomment.user_id, type=6)

                    take_coin_from_tipper_bch_comment(sender_id=current_user.id,
                                                      amount=final_amount,
                                                      commentid=thecomment.id,
                                                      recieverid=thecomment.id
                                                      )

                    # create Wallet Transaction for reciever (post creator)
                    sendcoin_to_poster_bch_comment(sender_id=current_user.id,
                                                   amount=amount_to_poster,
                                                   commentid=thecomment.id,
                                                   recieverid=thecomment.user_id
                                                   )

                    if payout == 1:
                        # create Wallet Transaction for subowner
                        sendcoin_subowner_bch_comment(sender_id=current_user.id,
                                                      amount=amount_to_subowner,
                                                      commentid=thecomment.id,
                                                      recieverid=thesub.creator_user_id
                                                      )

                    post.last_active = now
                    post.active = 1

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(thecomment)
                    db.session.add(changeposterbchstats)
                    db.session.add(changeuserbchstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Not enough coin in your wallet. ", category="danger")
                    return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))
            else:
                flash("Cannot tip yourself.  You can only promote your own posts.", category="danger")
                return redirect(url_for('tip.create_tip_comment', subname=subname, postid=postid, commentid=commentid))
        else:
            flash("Invalid Form.  Did you enter the amount correctly?", category="danger")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))

    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))


@tip.route('/createbchtip/post/<string:subname>/<int:postid>', methods=['POST'])
@login_required
def create_tip_post_bch(subname, postid):
    """
    Creates a bch tip for a post
    """
    form_bch = CreateTipBCH()
    now = datetime.utcnow()

    # get the sub, post, comment
    thesub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
    post = db.session.query(CommonsPost).get(postid)

    if post.shared_post != 0:
        idofpost = post.shared_post
    else:
        idofpost = post.id

    if thesub is None:
        flash("Sub does not exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post is None:
        flash("The post has been removed or doesnt exist", category="success")
        return redirect((request.args.get('next', request.referrer)))
    if post.hidden == 1:
        flash("Post Has been deleted", category="success")
        return redirect((request.args.get('next', request.referrer)))

    # get user stats
    changeuserbchstats = db.session.query(UserStatsBCH).filter_by(user_id=current_user.id).first()
    # get poster stats
    changeposterbchstats = db.session.query(UserStatsBCH).filter_by(user_id=post.content_user_id).first()
    if request.method == 'POST':
        if form_bch.validate_on_submit():
            # check to see if tipper != poster
            if post.content_user_id != current_user.id:

                # get amount donatred
                getcurrentprice = db.session.query(BchPrices).get(1)
                bch_current_price_usd = getcurrentprice.price

                usercoinsamount = db.session.query(BchWallet)
                usercoinsamount = usercoinsamount.filter(BchWallet.user_id == current_user.id)
                usercoinsamount = usercoinsamount.first()

                if form_bch.submit.data:
                    seeifcoin = re.compile(btcamount)
                    doesitmatch = seeifcoin.match(form_bch.custom_amount.data)
                    if doesitmatch:
                        bch_amount_for_submission = Decimal(form_bch.custom_amount.data)
                        decimalform_of_amount = floating_decimals(bch_amount_for_submission, 8)
                        bch_amount = decimalform_of_amount
                        # get usd amount
                        bt = (Decimal(getcurrentprice.price) * bch_amount)
                        formatteddollar = '{0:.2f}'.format(bt)
                        usd_amount = formatteddollar
                    else:
                        flash("Invalid coin amount.  Did you enter the amount wrong?", category="danger")
                        return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                elif form_bch.cent.data:
                    bch_amount = Decimal(0.01) / Decimal(bch_current_price_usd)
                    usd_amount = 0.01
                elif form_bch.quarter.data:
                    bch_amount = Decimal(0.25) / Decimal(bch_current_price_usd)
                    usd_amount = 0.25
                elif form_bch.dollar.data:
                    bch_amount = Decimal(1.00) / Decimal(bch_current_price_usd)
                    usd_amount = 1.00
                elif form_bch.five_dollar.data:
                    bch_amount = Decimal(5.00) / Decimal(bch_current_price_usd)
                    usd_amount = 5.00
                elif form_bch.ten_dollar.data:
                    bch_amount = Decimal(10.00) / Decimal(bch_current_price_usd)
                    usd_amount = 10.00
                elif form_bch.twentyfive_dollar.data:
                    bch_amount = Decimal(25.00) / Decimal(bch_current_price_usd)
                    usd_amount = 25.00
                elif form_bch.hundred_dollar.data:
                    bch_amount = Decimal(100.00) / Decimal(bch_current_price_usd)
                    usd_amount = 100.00
                else:
                    flash("Tip Failure.", category="success")
                    return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))

                final_amount = (floating_decimals(bch_amount, 8))
                lowestdonation = 0.000001
                if final_amount >= lowestdonation:
                    percent_to_subowner = 0.07
                    payout = 1
                else:
                    percent_to_subowner = 0
                    payout = 0

                if Decimal(usercoinsamount.currentbalance) >= Decimal(final_amount):
                    # btc amount
                    amount_to_subowner = Decimal(final_amount) * Decimal(percent_to_subowner)
                    # get usd amount
                    subownerbt = (Decimal(getcurrentprice.price) * amount_to_subowner)
                    subownerformatteddollar = '{0:.2f}'.format(subownerbt)
                    subowner_usd_amount = subownerformatteddollar

                    # Btc amount
                    amount_to_poster = Decimal(final_amount) - Decimal(amount_to_subowner)
                    # get usd amount
                    posterbt = (Decimal(getcurrentprice.price) * bch_amount)
                    posterformatteddollar = '{0:.2f}'.format(posterbt)
                    poster_usd_amount = posterformatteddollar

                    if payout == 1:
                        # subowner gets payout
                        newpayout = PayoutSubOwner(
                            created=now,
                            subcommon_id=thesub.id,
                            subcommon_name=thesub.subcommon_name,
                            post_id=post.id,
                            comment_id=0,

                            sub_owner_user_id=thesub.creator_user_id,
                            sub_owner_user_name=thesub.creator_user_name,
                            tipper_user_id=current_user.id,
                            tipper_user_name=current_user.user_name,

                            currency_type=2,
                            amount_btc=0,
                            amount_bch=amount_to_subowner,
                            amount_xmr=0,
                            amount_usd=subowner_usd_amount,
                        )
                        db.session.add(newpayout)

                    createnewtip = BchPostTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        amount_bch=amount_to_poster,
                        amount_usd=poster_usd_amount,
                    )

                    createrecenttip = RecentTips(
                        created=now,
                        created_user_id=current_user.id,
                        created_user_name=current_user.user_name,
                        recieved_user_id=post.content_user_id,
                        recieved_user_name=post.content_user_name,
                        subcommon_id=thesub.id,
                        subcommon_name=thesub.subcommon_name,
                        post_id=idofpost,
                        comment_id=0,
                        currency_type=2,
                        amount_bch=amount_to_poster,
                        amount_btc=0,
                        amount_xmr=0,
                        amount_usd=poster_usd_amount,
                    )

                    # add stats to user who donated
                    current_amount_donated_to_comments = changeuserbchstats.total_donated_to_postcomments_bch
                    newamount = (floating_decimals(current_amount_donated_to_comments + final_amount, 8))
                    changeuserbchstats.total_donated_to_postcomments_bch = newamount
                    current_amount_donated_to_comments_usd = changeuserbchstats.total_donated_to_postcomments_usd
                    newamount_usd = (floating_decimals(current_amount_donated_to_comments_usd + Decimal(usd_amount), 2))
                    changeuserbchstats.total_donated_to_postcomments_usd = newamount_usd

                    # add stats to user who recieved coin
                    current_amount_recieved_to_posts = changeposterbchstats.total_recievedfromposts_bch
                    newamount_poster = (floating_decimals(current_amount_recieved_to_posts + amount_to_poster, 8))
                    changeposterbchstats.total_recievedfromposts_bch = newamount_poster
                    current_amount_recieved_to_posts_usd = changeposterbchstats.total_recievedfromposts_usd
                    newamount_poster_usd = (floating_decimals(current_amount_recieved_to_posts_usd + Decimal(poster_usd_amount), 2))
                    changeposterbchstats.total_recievedfromposts_usd = newamount_poster_usd

                    seeifpostdonates = PostDonations.query.filter(PostDonations.post_id == idofpost).first()
                    if seeifpostdonates is None:

                        addstatstopost = PostDonations(
                            post_id=idofpost,
                            total_recieved_btc=0,
                            total_recieved_btc_usd=0,
                            total_recieved_bch=final_amount,
                            total_recieved_bch_usd=usd_amount,
                            total_recieved_xmr=0,
                            total_recieved_xmr_usd=0,

                        )
                        db.session.add(addstatstopost)
                    else:
                        # modify comments to show it got btc
                        current_post_bch_amount = seeifpostdonates.total_recieved_bch
                        current_amount_bch_usd_amount = seeifpostdonates.total_recieved_bch_usd
                        newamount_for_post = (floating_decimals(current_post_bch_amount + amount_to_poster, 8))
                        newamount_for_post_usd = (floating_decimals(current_amount_bch_usd_amount + Decimal(poster_usd_amount), 2))
                        seeifpostdonates.total_recieved_bch = newamount_for_post
                        seeifpostdonates.total_recieved_bch_usd = newamount_for_post_usd

                        db.session.add(seeifpostdonates)

                    add_new_notification(user_id=post.content_user_id,
                                         subid=thesub.id,
                                         subname=thesub.subcommon_name,
                                         postid=idofpost,
                                         commentid=0,
                                         msg=2
                                         )

                    if payout == 1:
                        add_new_notification(user_id=thesub.creator_user_id,
                                             subid=thesub.id,
                                             subname=thesub.subcommon_name,
                                             postid=post.id,
                                             commentid=0,
                                             msg=15
                                             )

                    # add exp points to donater
                    exppoint(user_id=current_user.id, type=5)
                    # add exp points to reciever
                    exppoint(user_id=post.content_user_id, type=6)

                    # create Wallet Transaction for both users
                    take_coin_from_tipper_bch_post(sender_id=current_user.id,
                                                   amount=final_amount,
                                                   postid=idofpost,
                                                   recieverid=post.content_user_id
                                                   )

                    # create Wallet Transaction for both users
                    sendcoin_to_poster_bch_post(sender_id=current_user.id,
                                                amount=amount_to_poster,
                                                postid=idofpost,
                                                recieverid=post.content_user_id
                                                )

                    if payout == 1:
                        # create Wallet Transaction for both users
                        sendcoin_subowner_bch_post(sender_id=current_user.id,
                                                   amount=amount_to_subowner,
                                                   postid=idofpost,
                                                   recieverid=thesub.creator_user_id
                                                   )

                    post.last_active = now
                    post.active = 1

                    db.session.add(createrecenttip)
                    db.session.add(createnewtip)
                    db.session.add(post)
                    db.session.add(changeposterbchstats)
                    db.session.add(changeuserbchstats)
                    db.session.commit()

                    flash("Tip was successful.", category="success")
                    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
                else:
                    flash("Insufficient Funds.", category="danger")
                    return redirect(url_for('tip.create_tip_post', subname=subname, postid=postid))
            else:
                flash("Cannot tip yourself.  You can promote your posts to boost visibility.  ", category="success")
                return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
        else:
            flash("Invalid Form", category="success")
            return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))
    return redirect(url_for('subforum.viewpost', subname=thesub.subcommon_name, postid=post.id))

