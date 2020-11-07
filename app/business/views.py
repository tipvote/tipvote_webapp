
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash, request
from flask_login import current_user
from app import db
from werkzeug.datastructures import CombinedMultiDict
from app.business import business

from app.profile.forms import FriendForm
from app.create.forms import BusinessPostForm
from app.edit.forms import DeletePostTextForm
from app.business.forms import SubscribeForm

from app.mod.forms import \
    QuickBanDelete, \
    QuickDelete, \
    QuickLock, \
    QuickMute

from app.classes.post import CommonsPost
from app.classes.business import Business, BusinessFollowers, BusinessStats

from sqlalchemy import func
from datetime import datetime

@business.route('/<string:business_name>', methods=['GET'])
def main(business_name):
    # forms
    business_post_form = BusinessPostForm(CombinedMultiDict((request.files, request.form)))

    friendform = FriendForm()
    deleteposttextform = DeletePostTextForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    subform = SubscribeForm()
    navlink = 1

    thebizname = business_name.lower()
    thebiz = db.session.query(Business).filter(func.lower(Business.business_name) == thebizname).first()
    if thebiz is None:
        flash('Business does not exist', category='warning')
        return redirect(url_for('index'))

    if current_user.is_authenticated:
        seeifsubbedtobiz = BusinessFollowers.query.filter(BusinessFollowers.user_id == current_user.id,
                                                          BusinessFollowers.business_id == thebiz.id).first()
    else:
        seeifsubbedtobiz = None

    if seeifsubbedtobiz is None:
        seeifsubbed = 0
    else:
        seeifsubbed = 1

    # get users posts
    biz_posts = db.session.query(CommonsPost)
    biz_posts = biz_posts.filter(thebiz.id == CommonsPost.poster_user_id)
    biz_posts = biz_posts.filter(CommonsPost.subcommon_id == 13)
    biz_posts = biz_posts.filter(CommonsPost.userhidden == 0)
    biz_posts = biz_posts.filter(CommonsPost.hidden == 0)
    biz_posts = biz_posts.filter(CommonsPost.muted == 0)
    biz_posts = biz_posts.order_by(CommonsPost.created.desc())
    posts = biz_posts.limit(50)

    return render_template('business/main.html',
                           now=datetime.utcnow(),
                           business_post_form=business_post_form,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           muteuserform=muteuserform,
                           friendform=friendform,
                           deleteposttextform=deleteposttextform,
                           posts=posts,
                           seeifsubbed=seeifsubbed,
                           thebiz=thebiz,
                           navlink=navlink,
                           subform=subform,

                           biz_posts=biz_posts,
                           )


@business.route('/<string:business_name>/other', methods=['GET'])
def main_post_to_another_wall(business_name):
    # forms
    business_post_form = BusinessPostForm(CombinedMultiDict((request.files, request.form)))

    friendform = FriendForm()
    deleteposttextform = DeletePostTextForm()
    banuserdeleteform = QuickBanDelete()
    lockpostform = QuickLock()
    deletepostform = QuickDelete()
    muteuserform = QuickMute()

    subform = SubscribeForm()
    navlink = 2

    thebiz = db.session.query(Business).filter(Business.business_name == business_name).first()

    seeifsubbedtobiz = BusinessFollowers.query.filter(BusinessFollowers.user_id == current_user.id,
                                                      BusinessFollowers.business_id == thebiz.id).first()
    if seeifsubbedtobiz is None:
        seeifsubbed = 0
    else:
        seeifsubbed = 1

    if thebiz is None:
        flash('Business does not exist', category='warning')
        return redirect(url_for('index'))



    # get users posts
    biz_posts = db.session.query(CommonsPost)
    biz_posts = biz_posts.filter(thebiz.id == CommonsPost.business_id)
    biz_posts = biz_posts.filter(CommonsPost.user_id != thebiz.user_id)
    biz_posts = biz_posts.filter(CommonsPost.subcommon_id == 13)
    biz_posts = biz_posts.filter(CommonsPost.userhidden == 0)
    biz_posts = biz_posts.filter(CommonsPost.hidden == 0)
    biz_posts = biz_posts.filter(CommonsPost.muted == 0)
    biz_posts = biz_posts.order_by(CommonsPost.created.desc())
    posts = biz_posts.limit(50)

    return render_template('business/main_other_wall.html',
                           now=datetime.utcnow(),
                           business_post_form=business_post_form,
                           banuserdeleteform=banuserdeleteform,
                           lockpostform=lockpostform,
                           deletepostform=deletepostform,
                           seeifsubbed=seeifsubbed,
                           muteuserform=muteuserform,
                           friendform=friendform,
                           deleteposttextform=deleteposttextform,
                           posts=posts,
                           subform=subform,
                           thebiz=thebiz,
                           navlink=navlink,

                           biz_posts=biz_posts,
                           )


# SubScribe to a forum
@business.route('/suborunsub/<string:business_name>', methods=['POST'])
def subunsubtobusiness(business_name):
    subform = SubscribeForm()
    # get the sub
    thebiz = db.session.query(Business).filter(Business.business_name == business_name).first()
    bizstats = BusinessStats.query.filter(BusinessStats.business_id == thebiz.id).first()
    # get id of the sub
    subid = int(thebiz.id)

    # subscribe to a sub
    if request.method == 'POST':
        if subform.validate_on_submit():
            # see if user subscribed
            if current_user.is_authenticated:
                # see if user already subbed

                if subform.subscribe.data is True:
                    seeifsubbed = db.session.query(BusinessFollowers).filter(BusinessFollowers.user_id == current_user.id,
                                                                             BusinessFollowers.business_id == subid).first()
                    if seeifsubbed is None:
                        # add subscribition
                        subtoit = BusinessFollowers(
                            user_id=current_user.id,
                            business_id=subid,

                        )
                        # add new member to sub
                        current_members = bizstats.total_followers
                        addmembers = current_members + 1
                        bizstats.total_followers = addmembers

                        db.session.add(bizstats)
                        db.session.add(subtoit)
                        db.session.commit()
                        flash("subscribed.", category="success")
                        return redirect(url_for('business.main', business_name=business_name))
                    else:
                        flash("You are already subbed.", category="success")
                        return redirect(url_for('business.main', business_name=business_name))
                elif subform.unsubscribe.data is True:

                    if thebiz.user_name == current_user.user_name:

                        flash("Cannot unsubscribe from your page.  You are the owner", category="success")
                        return redirect(url_for('business.main', business_name=business_name))

                    # get the sub query and delete it
                    unsubtoit = BusinessFollowers.query.filter(BusinessFollowers.user_id == current_user.id,
                                                               BusinessFollowers.business_id == subid).first()

                    # add new member to sub
                    current_members = bizstats.total_followers
                    addmembers = current_members - 1
                    bizstats.total_followers = addmembers
                    db.session.add(bizstats)
                    db.session.delete(unsubtoit)
                    db.session.commit()
                    flash("unsubscribed.", category="danger")
                    return redirect(url_for('business.main', business_name=business_name))
                else:

                    flash("No Selection", category="danger")
                    return redirect(url_for('business.main', business_name=business_name))
            else:
                flash("User must be logged in", category='danger')
                return redirect(url_for('business.main', business_name=business_name))
        else:
            flash("Form Error", category='danger')
            return redirect(url_for('business.main', business_name=business_name))
