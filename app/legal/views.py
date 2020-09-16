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
# common imports
from app import db

# relative directory
from app.legal import legal
from app.legal.forms import\
    ReplyToMsg,\
    CreateAMsg,\
    CreateAMsgUser

from app.models import \
    LegalMessages,\
    LegalReply,\
    User, \
    BlockedUser, \
    Business

from app.message.add_notification import add_new_notification


@legal.route('/main', methods=['GET'])
@login_required
def main():
    form = ReplyToMsg()

    if request.method == 'GET':

        theposts = db.session.query(LegalMessages)
        theposts = theposts.filter(or_(LegalMessages.rec_user_id == current_user.id,
                                       LegalMessages.sender_user_id == current_user.id))
        theposts = theposts.order_by(LegalMessages.last_message.desc())
        posts = theposts.limit(10)

        themessage = LegalMessages.query\
            .filter(or_(LegalMessages.sender_user_id == current_user.id, LegalMessages.rec_user_id == current_user.id))\
            .order_by(LegalMessages.id.desc())\
            .first()

        if themessage is None:
            return render_template('/legal/main.html',

                                   themessage=themessage,
                                   form=form,
                                   posts=posts,

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

        thereplys = db.session.query(LegalReply)
        thereplys = thereplys.filter(LegalReply.message_id == themessage.id)
        thereplys = thereplys.order_by(LegalReply.created.asc())
        replys = thereplys.all()

        if themessage.msg_type == 1:
            return render_template('/legal/msglayout/viewmsg.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,

                                   )
        elif themessage.msg_type == 2:

            return render_template('/legal/msglayout/viewmsg_business.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,

                                   )
        else:
            return render_template('/legal/msglayout/viewmsg.html',
                                   replys=replys,
                                   themessage=themessage,
                                   form=form,
                                   posts=posts,

                                   )
    if request.method == 'POST':
        return redirect((url_for('index')))


@legal.route('/markasread', methods=['POST'])
@login_required
def mark_as_read():

    if request.method == 'POST':
        theposts = db.session.query(LegalMessages)
        theposts = theposts.filter(LegalMessages.rec_user_id == current_user.id)
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
        return redirect((url_for('legal.main')))

    if request.method == 'GET':
        return redirect((url_for('index')))


@legal.route('/msg/<int:msgid>', methods=['GET'])
@login_required
def view_message(msgid):
    form = ReplyToMsg()
    if request.method == 'GET':
        themessage = LegalMessages.query.filter(LegalMessages.id == msgid).first_or_404()

        if ((themessage.rec_user_id == current_user.id) or (themessage.sender_user_id == current_user.id)):
            theposts = db.session.query(LegalMessages)
            theposts = theposts.filter(or_(LegalMessages.rec_user_id == current_user.id,
                                           LegalMessages.sender_user_id == current_user.id))
            theposts = theposts.order_by(LegalMessages.last_message.desc())
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

            thereplys = db.session.query(LegalReply)

            thereplys = thereplys.filter(LegalReply.message_id == msgid)
            thereplys = thereplys.order_by(LegalReply.created.asc())
            replys = thereplys.all()

            if themessage.msg_type == 1:
                return render_template('/legal/msglayout/viewmsg.html',
                                       replys=replys,
                                       themessage=themessage,
                                       form=form,
                                       posts=posts
                                       )
            elif themessage.msg_type == 2:

                return render_template('/legal/msglayout/viewmsg_business.html',
                                       replys=replys,
                                       themessage=themessage,
                                       form=form,
                                       posts=posts
                                       )
            else:
                return render_template('/legal/msglayout/viewmsg.html',
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


@legal.route('/msg/<int:msgid>', methods=['POST'])
@login_required
def reply_message(msgid):
    now = datetime.utcnow()

    form = ReplyToMsg()
    if request.method == 'POST':
        thepost = LegalMessages.query.filter(LegalMessages.id == msgid).first_or_404()

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
                newreply = LegalReply(
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
                                     msg=54,
                                     )

                db.session.commit()

                flash("Reply Sent", category="success")
                return redirect((url_for('legal.view_message', msgid=thepost.id)))
        else:

            flash("Message not found", category="danger")
            return redirect((url_for('index')))
    if request.method == 'GET':
        return redirect((url_for('index')))


@legal.route('/msg/create', methods=['GET', 'POST'])
@login_required
def create_message():
    now = datetime.utcnow()

    form = CreateAMsg()
    theposts = db.session.query(LegalMessages)
    theposts = theposts.filter(or_(LegalMessages.rec_user_id == current_user.id,
                                   LegalMessages.sender_user_id == current_user.id))
    theposts = theposts.order_by(LegalMessages.last_message.desc())
    posts = theposts.limit(100)

    if request.method == 'GET':

        return render_template('/legal/create_msg.html',
                               form=form,
                               posts=posts
                               )

    if request.method == 'POST':

        the_user = User.query.filter(User.id == 1).first()
        if the_user is None:
            flash("User Not Found.  Did you spell it correctly?", category="success")
            return redirect((url_for('legal.create_message')))

        if the_user.id == current_user.id:
            flash("Can not message yourself", category="success")
            return redirect((url_for('legal.create_message')))
        # see if blocked
        isuserblocked = BlockedUser.query.filter(BlockedUser.user_id == the_user.id,
                                                 BlockedUser.blocked_user == current_user.id).first()

        isuserbeingblocked = BlockedUser.query.filter(BlockedUser.user_id == current_user.id,
                                                      BlockedUser.blocked_user == the_user.id).first()
        if isuserblocked is not None or isuserbeingblocked is not None:
            flash("User isnt accepting messages.", category="danger")
            return redirect(url_for('index'))

        seeifpostexists = db.session.query(LegalMessages)
        seeifpostexists = seeifpostexists.filter(LegalMessages.sender_user_id == current_user.id)
        seeifpostexists = seeifpostexists.filter(LegalMessages.rec_user_id == the_user.id)
        seeifpostexists = seeifpostexists.first()

        if seeifpostexists is None:

            newmsg = LegalMessages(
                created=now,
                read_rec=1,
                read_send=0,
                msg_type=1,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=1,
                rec_user_user_name='tipvote',
                body='',
                biz_id=None,
                biz_name='',
                last_message=now
            )
            db.session.add(newmsg)
            db.session.commit()

            newreply = LegalReply(
                created=now,
                message_id=newmsg.id,
                sender_user_id=current_user.id,
                sender_user_user_name=current_user.user_name,
                rec_user_id=1,
                rec_user_user_name='tipvote',
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
            return redirect((url_for('legal.main')))
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



            newreply = LegalReply(
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
                                 msg=55,
                                 )

            db.session.commit()

            flash("Reply Sent", category="success")
            return redirect((url_for('legal.view_message', msgid=seeifpostexists.id)))


