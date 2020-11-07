# flask imports
from flask import \
    render_template, \
    redirect, \
    url_for, \
    flash,\
    request
from sqlalchemy import or_
from flask_login import current_user
from app.common.decorators import login_required
from datetime import datetime

from app import db, app

# relative directory
from app.message import message
from app.message.forms import\
    MarkAsRead,\
    ReplyToMsg,\
    CreateAMsg,\
    CreateAMsgUser

from app.models import Notifications
from app.classes.business import Business
from app.classes.user import User, BlockedUser
from app.classes.messages import Reply, Messages

from app.message.add_notification import add_new_notification


@message.route('/main', methods=['GET'])
@login_required
def main():
    form = ReplyToMsg()
    markasreadform = MarkAsRead()

    if request.method == 'GET':

        theposts = db.session.query(Messages)
        theposts = theposts.filter(or_(Messages.rec_user_id == current_user.id,
                                       Messages.sender_user_id == current_user.id))
        theposts = theposts.order_by(Messages.last_message.desc())
        posts = theposts.limit(10)

        themessage = db.session.query(Messages)
        themessage = themessage.filter(or_(Messages.sender_user_id == current_user.id,
                                           Messages.rec_user_id == current_user.id))

        themessage = themessage.order_by(Messages.last_message.desc())
        themessage = themessage.first()

        if themessage is None:
            return render_template('/msg/main.html',

                                   themessage=themessage,
                                   form=form,
                                   posts=posts,
                                   markasreadform=markasreadform,
                                   )
        if themessage.sender_user_id == current_user.id:
            if themessage.read_send == 1:
                themessage.read_send = 0

                db.session.add(themessage)
                db.session.commit()
        if themessage.rec_user_id == current_user.id:
            if themessage.read_rec == 1:
                themessage.read_rec = 0

                db.session.add(themessage)
                db.session.commit()

        thereplys = db.session.query(Reply)
        thereplys = thereplys.filter(Reply.message_id == themessage.id)
        thereplys = thereplys.order_by(Reply.created.desc())
        replys = thereplys.all()

        if themessage.msg_type == 1:
            return render_template('/msg/msglayout/viewmsg.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,
                                   markasreadform=markasreadform,
                                   )
        elif themessage.msg_type == 2:

            return render_template('/msg/msglayout/viewmsg_business.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,
                                   markasreadform=markasreadform,
                                   )
        else:
            return render_template('/msg/msglayout/viewmsg.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,
                                   markasreadform=markasreadform,
                                   )
    if request.method == 'POST':
        return redirect((url_for('index')))


@message.route('/markasread', methods=['POST'])
@login_required
def mark_as_read():

    if request.method == 'POST':
        theposts = db.session.query(Messages)
        theposts = theposts.filter(Messages.rec_user_id == current_user.id)
        theposts = theposts.all()

        for f in theposts:
            if f.sender_user_id == current_user.id:
                if f.read_send == 0:
                    f.read_send = 1

                    db.session.add(f)

            if f.rec_user_id == current_user.id:
                if f.read_rec == 0:
                    f.read_rec = 1

                    db.session.add(f)

        db.session.commit()
        flash("Marked as read", category="success")
        return redirect((url_for('message.main')))

    if request.method == 'GET':
        return redirect((url_for('index')))


@message.route('/msg/<int:msgid>', methods=['GET'])
@login_required
def view_message(msgid):
    form = ReplyToMsg()
    if request.method == 'GET':
        themessage = db.session.query(Messages).filter(Messages.id == msgid).first_or_404()

        if (themessage.rec_user_id == current_user.id) or (themessage.sender_user_id == current_user.id):
            theposts = db.session.query(Messages)
            theposts = theposts.filter(or_(Messages.rec_user_id == current_user.id,
                                           Messages.sender_user_id == current_user.id))
            theposts = theposts.order_by(Messages.last_message.desc())
            posts = theposts.limit(100)

            if themessage.sender_user_id == current_user.id:
                if themessage.read_send == 1:
                    themessage.read_send = 0

                    db.session.add(themessage)
                    db.session.commit()
            if themessage.rec_user_id == current_user.id:
                if themessage.read_rec == 1:
                    themessage.read_rec = 0

                    db.session.add(themessage)
                    db.session.commit()

            thereplys = db.session.query(Reply)

            thereplys = thereplys.filter(Reply.message_id == msgid)
            thereplys = thereplys.order_by(Reply.created.desc())
            replys = thereplys.all()

            if themessage.msg_type == 1:
                return render_template('/msg/msglayout/viewmsg.html',
                                       replys=replys,
                                       themessage=themessage,
                                       form=form,
                                       posts=posts
                                       )
            elif themessage.msg_type == 2:

                return render_template('/msg/msglayout/viewmsg_business.html',
                                       replys=replys,
                                       themessage=themessage,
                                       form=form,
                                       posts=posts
                                       )
            else:
                return render_template('/msg/msglayout/viewmsg.html',
                                       replys=replys,
                                       themessage=themessage,
                                       form=form,
                                       posts=posts
                                       )
        else:
            flash("Message not found", category="danger")
            return redirect((url_for('index')))

    if request.method == 'POST':
        return redirect((url_for('index')))


@message.route('/msg/<int:msgid>', methods=['POST'])
@login_required
def reply_message(msgid):
    now = datetime.utcnow()

    form = ReplyToMsg()
    if request.method == 'POST':
        thepost = Messages.query.filter(Messages.id == msgid).first_or_404()

        if (thepost.rec_user_id == current_user.id) or (thepost.sender_user_id == current_user.id):
            if thepost.rec_user_id == current_user.id:
                otheruserid = thepost.sender_user_id
                otherusername = thepost.sender_user_user_name

            elif thepost.sender_user_id == current_user.id:
                otheruserid = thepost.rec_user_id
                otherusername = thepost.rec_user_user_name
            else:
                otheruserid = current_user.id
                otherusername = current_user.id

            if request.method == 'POST':
                if thepost.rec_user_id == current_user.id:
                    if thepost.read_send == 0:
                        thepost.read_send = 1

                        db.session.add(thepost)

                if thepost.sender_user_id == current_user.id:
                    if thepost.read_rec == 0:
                        thepost.read_rec = 1

                        db.session.add(thepost)

                thepost.last_message = now
                newreply = Reply(
                    created=now,
                    message_id=msgid,
                    sender_user_id=current_user.id,
                    sender_user_user_name=current_user.user_name,
                    rec_user_id=otheruserid,
                    rec_user_user_name=otherusername,
                    body=form.postmessage.data,
                    biz_id=thepost.biz_id,
                    biz_name=thepost.biz_name,
                )

                db.session.add(newreply)
                db.session.add(thepost)
                # add notification for poster about new comment
                add_new_notification(user_id=otheruserid,
                                     subid=0,
                                     subname='',
                                     postid=msgid,
                                     commentid=0,
                                     msg=51,
                                     )

                db.session.commit()

                flash("Reply Sent", category="success")
                return redirect((url_for('message.view_message', msgid=thepost.id)))
        else:
            flash("Message not found", category="danger")
            return redirect((url_for('index')))
    if request.method == 'GET':
        return redirect((url_for('index')))


@message.route('/msg/create', methods=['GET', 'POST'])
@login_required
def create_message():
    now = datetime.utcnow()

    form = CreateAMsg()
    theposts = db.session.query(Messages)
    theposts = theposts.filter(or_(Messages.rec_user_id == current_user.id,
                                   Messages.sender_user_id == current_user.id))
    theposts = theposts.order_by(Messages.last_message.desc())
    posts = theposts.limit(100)

    if request.method == 'GET':

        return render_template('/msg/create_msg.html',
                               form=form,
                               posts=posts
                               )

    if request.method == 'POST':

        the_user = User.query.filter(User.user_name == form.user_name.data).first()
        if the_user is None:
            flash("User Not Found.  Did you spell it correctly?", category="success")
            return redirect((url_for('message.create_message')))

        if the_user.id == current_user.id:
            flash("Can not message yourself", category="success")
            return redirect((url_for('message.create_message')))
        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == the_user.id,
                                                 BlockedUser.blocked_user == current_user.id).first()

        isuserbeingblocked = BlockedUser.query.filter(BlockedUser.user_id == current_user.id,
                                                      BlockedUser.blocked_user == the_user.id).first()
        if isuserblocked is not None or isuserbeingblocked is not None:
            flash("User isnt accepting messages.", category="danger")
            return redirect(url_for('index'))

        seeifpostexists = db.session.query(Messages)
        seeifpostexists = seeifpostexists.filter(Messages.rec_user_id == current_user.id)
        seeifpostexists = seeifpostexists.filter(Messages.sender_user_id == the_user.id)
        seeifpostexists = seeifpostexists.first()

        seeifotherpostexists = db.session.query(Messages)
        seeifotherpostexists = seeifotherpostexists.filter(Messages.rec_user_id == the_user.id)
        seeifotherpostexists = seeifotherpostexists.filter(Messages.sender_user_id == current_user.id)
        seeifotherpostexists = seeifotherpostexists.first()

        if seeifpostexists is None and seeifotherpostexists is None:

            newmsg = Messages(
                created=now,
                read_rec=1,
                read_send=0,
                msg_type=1,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_user.id,
                rec_user_user_name=the_user.user_name,
                body='',
                biz_id=None,
                biz_name='',
                last_message=now
            )
            db.session.add(newmsg)
            db.session.commit()

            newreply = Reply(
                created=now,
                message_id=newmsg.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_user.id,
                rec_user_user_name=the_user.user_name,
                body=form.postmessage.data,
                biz_id=None,
                biz_name='',
            )

            # add notification for poster about new comment
            add_new_notification(user_id=the_user.id,
                                 subid=0,
                                 subname='',
                                 postid=newmsg.id,
                                 commentid=0,
                                 msg=50,
                                 )

            db.session.add(newreply)
            db.session.commit()
            flash("Message Sent", category="success")
            return redirect((url_for('message.main')))
        else:
            if seeifotherpostexists is None:
                seeifpostexists.last_message = now

                if seeifpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)

            if seeifpostexists is not None:

                seeifotherpostexists.last_message = now

                if seeifotherpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)

            if seeifpostexists is not None:
                if seeifpostexists.rec_user_id == current_user.id:
                    otheruserid = seeifpostexists.sender_user_id
                    otherusername = seeifpostexists.sender_user_user_name

                elif seeifpostexists.sender_user_id == current_user.id:
                    otheruserid = seeifpostexists.rec_user_id
                    otherusername = seeifpostexists.rec_user_user_name
                else:
                    otheruserid = current_user.id
                    otherusername = current_user.id

                newreply = Reply(
                    created=now,
                    message_id=seeifpostexists.id,
                    sender_user_id=current_user.id,
                    sender_user_user_name=current_user.user_name,
                    rec_user_id=otheruserid,
                    rec_user_user_name=otherusername,
                    body=form.postmessage.data,
                    biz_id=seeifpostexists.biz_id,
                    biz_name=seeifpostexists.biz_name,
                )
                # add notification for poster about new comment
                add_new_notification(user_id=otheruserid,
                                     subid=0,
                                     subname='',
                                     postid=seeifpostexists.id,
                                     commentid=0,
                                     msg=51,
                                     )

                db.session.add(seeifpostexists)
                db.session.add(newreply)
                db.session.commit()

                flash("Reply Sent", category="success")
                return redirect((url_for('message.view_message', msgid=seeifpostexists.id)))

            else:
                if seeifotherpostexists.rec_user_id == current_user.id:
                    otheruserid = seeifotherpostexists.sender_user_id
                    otherusername = seeifotherpostexists.sender_user_user_name

                elif seeifotherpostexists.sender_user_id == current_user.id:
                    otheruserid = seeifotherpostexists.rec_user_id
                    otherusername = seeifotherpostexists.rec_user_user_name
                else:
                    otheruserid = current_user.id
                    otherusername = current_user.id

                newreply = Reply(
                    created=now,
                    message_id=seeifotherpostexists.id,
                    sender_user_id=current_user.id,
                    sender_user_user_name=current_user.user_name,
                    rec_user_id=otheruserid,
                    rec_user_user_name=otherusername,
                    body=form.postmessage.data,
                    biz_id=seeifotherpostexists.biz_id,
                    biz_name=seeifotherpostexists.biz_name,
                )
                # add notification for poster about new comment
                add_new_notification(user_id=otheruserid,
                                     subid=0,
                                     subname='',
                                     postid=seeifotherpostexists.id,
                                     commentid=0,
                                     msg=51,
                                     )
                db.session.add(seeifotherpostexists)

                db.session.add(newreply)
                db.session.commit()

                flash("Reply Sent", category="success")
                return redirect((url_for('message.view_message', msgid=seeifotherpostexists.id)))


@message.route('/msg/create/<user_name>', methods=['GET', 'POST'])
@login_required
def create_message_specific_user(user_name):
    now = datetime.utcnow()

    form = CreateAMsgUser()
    the_user = User.query.filter(User.user_name == user_name).first()

    theposts = db.session.query(Messages)
    theposts = theposts.filter(or_(Messages.rec_user_id == current_user.id,
                                   Messages.sender_user_id == current_user.id))
    theposts = theposts.order_by(Messages.last_message.desc())
    posts = theposts.limit(100)

    seeifpostexists = db.session.query(Messages)
    seeifpostexists = seeifpostexists.filter(Messages.rec_user_id == current_user.id)
    seeifpostexists = seeifpostexists.filter(Messages.sender_user_id == the_user.id)
    seeifpostexists = seeifpostexists.first()

    seeifotherpostexists = db.session.query(Messages)
    seeifotherpostexists = seeifotherpostexists.filter(Messages.sender_user_id == the_user.id)
    seeifotherpostexists = seeifotherpostexists.filter(Messages.rec_user_id == current_user.id)
    seeifotherpostexists = seeifotherpostexists.first()

    if the_user is None:
        flash("User is Not Found.  Did you spell it correctly?", category="success")
        return redirect((url_for('message.create_message_specific_user', user_name=user_name)))

    if request.method == 'GET':
        return render_template('/msg/create_msg_user.html',
                               form=form,
                               the_user=the_user,
                               posts=posts,
                               )

    if request.method == 'POST':
        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == the_user.id,
                                                 BlockedUser.blocked_user == current_user.id).first()

        isuserbeingblocked = BlockedUser.query.filter(BlockedUser.user_id == current_user.id,
                                                      BlockedUser.blocked_user == the_user.id).first()
        if isuserblocked is not None or isuserbeingblocked is not None:
            flash("User isnt accepting messages.", category="danger")
            return redirect(url_for('index'))

        if the_user.id == current_user.id:
            flash("Can not message yourself", category="success")
            return redirect((url_for('message.create_message')))

        if seeifpostexists is None and seeifotherpostexists is None:

            newmsg = Messages(
                created=now,
                read_rec=1,
                read_send=0,
                msg_type=1,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_user.id,
                rec_user_user_name=the_user.user_name,
                body='',
                biz_id=None,
                biz_name='',
                last_message=now
            )

            db.session.add(newmsg)
            db.session.commit()

            newreply = Reply(
                created=now,
                message_id=newmsg.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_user.id,
                rec_user_user_name=the_user.user_name,
                body=form.postmessage.data,
                biz_id=None,
                biz_name='',
            )

            # add notification for poster about new comment
            add_new_notification(user_id=the_user.id,
                                 subid=0,
                                 subname='',
                                 postid=newmsg.id,
                                 commentid=0,
                                 msg=50,
                                 )

            db.session.add(newreply)
            db.session.commit()
            flash("Message Sent", category="success")
            return redirect((url_for('message.view_message', msgid=newmsg.id)))

        else:

            if seeifpostexists.rec_user_id == current_user.id:
                otheruserid = seeifpostexists.sender_user_id
                otherusername = seeifpostexists.sender_user_user_name

            elif seeifpostexists.sender_user_id == current_user.id:
                otheruserid = seeifpostexists.rec_user_id
                otherusername = seeifpostexists.rec_user_user_name
            else:
                otheruserid = current_user.id
                otherusername = current_user.id

            if seeifpostexists is not None:
                seeifpostexists.last_message = now

                if seeifpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)

            if seeifotherpostexists is not None:

                seeifotherpostexists.last_message = now

                if seeifotherpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)


            seeifpostexists.last_message = now
            newreply = Reply(
                created=now,
                message_id=seeifpostexists.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=otheruserid,
                rec_user_user_name=otherusername,
                body=form.postmessage.data,
                biz_id=seeifpostexists.biz_id,
                biz_name=seeifpostexists.biz_name,
            )

            db.session.add(newreply)
            db.session.add(seeifpostexists)
            # add notification for poster about new comment
            add_new_notification(user_id=otheruserid,
                                 subid=0,
                                 subname='',
                                 postid=seeifpostexists.id,
                                 commentid=0,
                                 msg=51,
                                 )

            db.session.commit()

            flash("Reply Sent", category="success")
            return redirect((url_for('message.view_message', msgid=seeifpostexists.id)))


@message.route('/msg/create/business/<bizid>', methods=['GET', 'POST'])
@login_required
def create_message_business(bizid):
    now = datetime.utcnow()

    form = CreateAMsgUser()
    the_biz = Business.query.filter(Business.id == bizid).first()

    if the_biz is None:
        flash("Business is Not Found. Try Back Later or post this issue on /a/bugs", category="success")
        return redirect((url_for('index')))

    theposts = db.session.query(Messages)
    theposts = theposts.filter(or_(Messages.rec_user_id == current_user.id,
                                   Messages.sender_user_id == current_user.id))
    theposts = theposts.order_by(Messages.last_message.desc())
    posts = theposts.limit(100)

    seeifpostexists = db.session.query(Messages)
    seeifpostexists = seeifpostexists.filter(Messages.rec_user_id == current_user.id)
    seeifpostexists = seeifpostexists.filter(Messages.sender_user_id == the_biz.user_id)
    seeifpostexists = seeifpostexists.first()

    seeifotherpostexists = db.session.query(Messages)
    seeifotherpostexists = seeifotherpostexists.filter(Messages.sender_user_id == the_biz.user_id)
    seeifotherpostexists = seeifotherpostexists.filter(Messages.rec_user_id == current_user.id)
    seeifotherpostexists = seeifotherpostexists.first()

    if request.method == 'GET':
        return render_template('/msg/create_msg_biz.html',
                               form=form,
                               the_biz=the_biz,
                               posts=posts
                               )

    if request.method == 'POST':

        if the_biz.user_id == current_user.id:
            flash("Can not message yourself", category="success")
            return redirect((url_for('message.create_message')))

        if seeifpostexists is None and seeifotherpostexists is None:

            newmsg = Messages(
                created=now,
                read=0,
                msg_type=2,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_biz.user_id,
                rec_user_user_name=the_biz.user_name,
                body='',
                biz_id=the_biz.id,
                biz_name=the_biz.business_name,
                last_message=now
            )

            db.session.add(newmsg)
            db.session.commit()

            newreply = Reply(
                created=now,
                message_id=newmsg.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=the_biz.user_id,
                rec_user_user_name=the_biz.user_name,
                body=form.postmessage.data,
                biz_id=the_biz.id,
                biz_name=the_biz.business_name,
            )

            # add notification for poster about new comment
            add_new_notification(user_id=the_biz.user_id,
                                 subid=0,
                                 subname='',
                                 postid=newmsg.id,
                                 commentid=0,
                                 msg=52,
                                 )

            db.session.add(newreply)
            db.session.commit()
            flash("Message Sent", category="success")
            return redirect((url_for('message.view_message', msgid=newmsg.id)))

        else:

            if seeifpostexists.rec_user_id == current_user.id:
                otheruserid = seeifpostexists.sender_user_id
                otherusername = seeifpostexists.sender_user_user_name

            elif seeifpostexists.sender_user_id == current_user.id:
                otheruserid = seeifpostexists.rec_user_id
                otherusername = seeifpostexists.rec_user_user_name
            else:
                otheruserid = current_user.id
                otherusername = current_user.id

            if seeifpostexists is not None:
                seeifpostexists.last_message = now

                if seeifpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)

            if seeifotherpostexists is not None:

                seeifotherpostexists.last_message = now

                if seeifotherpostexists.sender_user_id == current_user.id:
                    if seeifpostexists.read_send == 0:
                        seeifpostexists.read_send = 1

                        db.session.add(seeifpostexists)

                if seeifpostexists.rec_user_id == current_user.id:
                    if seeifpostexists.read_rec == 0:
                        seeifpostexists.read_rec = 1

                        db.session.add(seeifpostexists)

            seeifpostexists.last_message = now
            newreply = Reply(
                created=now,
                message_id=seeifpostexists.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=otheruserid,
                rec_user_user_name=otherusername,
                body=form.postmessage.data,
                biz_id=seeifpostexists.biz_id,
                biz_name=seeifpostexists.biz_name,
            )

            db.session.add(newreply)
            db.session.add(seeifpostexists)
            # add notification for poster about new comment
            add_new_notification(user_id=otheruserid,
                                 subid=0,
                                 subname='',
                                 postid=seeifpostexists.id,
                                 commentid=0,
                                 msg=51,
                                 )

            db.session.commit()

            flash("Reply Sent", category="success")
            return redirect((url_for('message.view_message', msgid=seeifpostexists.id)))


@message.route('/notifications', methods=['GET'])
@login_required
def notifications():

    page = request.args.get('page', 1, type=int)
    thenotes = db.session.query(Notifications)
    thenotes = thenotes.filter(Notifications.user_id == current_user.id)
    thenotes = thenotes.order_by(Notifications.timestamp.desc())
    notes = thenotes.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('message.notifications', page=notes.next_num) \
        if notes.has_next else None
    prev_url = url_for('message.notifications', page=notes.prev_num) \
        if notes.has_prev else None

    for note in thenotes:
        note.read = 1
        db.session.add(note)
    db.session.commit()

    return render_template('/msg/notifications.html',

                           notes=notes.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           )


@message.route('/marknotifications', methods=['GET'])
@login_required
def markallnotifications():
    if request.method == 'GET':
        # mod security
        notes = db.session.query(Notifications)
        notes = notes.filter(Notifications.user_id == current_user.id)
        notes = notes.filter(Notifications.read == 0)
        notes = notes.all()
        for note in notes:
            note.read = 1
            db.session.add(note)
        db.session.commit()

        return redirect((request.args.get('next', request.referrer)))

    elif request.method == 'POST':
        pass

    else:
        pass


