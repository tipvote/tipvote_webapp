from app import db
from app.classes.notification import Notifications
from datetime import datetime

# 1 New comment on message
# 2 tipped  a post with bitcoin
# 3 tipped a post with xmr
# 4 tipped a comment with btc
# 5 tipped a comment with xmr
# 6 user was made a mod of a sub
# 7 user was removed as mod of a sub
# 8 user was unbanned from a sub
# 9 user was invited to a sub
# 10 user was removed to a sub
# 11 user was muted from a sub
# 12 user was banned from a sub
# 13 user post was locked
# 14 you have a post on your wall
# 15 subforum owner got a tip
# 16 someone wrote on your wall
# 20 tipped a post with bitcoin cash
# 21 tipped a comment with btc cash

# 22 reply to your comment

# 25 subforum owner got a tip in bitcoin
# 26 subforum owner got a tip in bitcoin cash
# 27 subforum owner got a tip in monero
# messaging

# 30 New comment on message


# 50 = new message
# 51 = new reply
# 53 = business new message
# 54 = legal new message
# 55 = legal new reply

# coins
# 60 sent a promotion coin

# bitcoin
# 100 =  too litte or too much at withdrawl
# 101 = not enough funds
# 102 = wallet error
# 103 = btc address error
# 104 = Your Bitcoin withdraw was successful
# 105 = You have a new incomming Bitcoin deposit


# bch
# 0 =  wallet sent
# errors
# 200 =  too litte or too much at withdrawl
# 201 = not enough funds
# 202 = There was a Bitcoin Cash wallet error.
# 203 = You have a Bitcoin Cash address error in your withdrawl
# 204 = Your Bitcoin Cash withdraw was successful
# 205 = You have a new incomming Bitcoin Cash deposit

# xmr
# 0 =  wallet sent
# errors
# 300 =  too litte or too much at withdrawl
# 301 = not enough funds
# 302 = There was a Bitcoin Cash wallet error.
# 303 = You have a Bitcoin Cash address error in your withdrawl
# 304 = Your Bitcoin Cash withdraw was successful
# 305 = You have a new incomming Bitcoin Cash deposit

def add_new_notification(user_id, subid, subname, postid, commentid, msg):

    now = datetime.utcnow()
    newnotification = Notifications(
                        timestamp=now,
                        read=0,
                        user_id=user_id,
                        subcommon_id=subid,
                        subcommon_name=subname,
                        post_id=postid,
                        comment_id=commentid,
                        msg_type=msg,
                            )
    db.session.add(newnotification)
