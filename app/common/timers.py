from app import db
from datetime import datetime
from datetime import timedelta
from string import Template
from app.classes.user import UserTimers

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def lastposted(user_id):
    # time in between posts
    # minutes
    setlimit = 1
    now = datetime.utcnow()
    minutestimer = datetime.utcnow() - timedelta(minutes=setlimit)
    getuser = db.session.query(UserTimers).filter_by(user_id=user_id).first()

    if getuser.last_post is None:
        getuser.last_post = now
        db.session.add(getuser)
        db.session.commit()
    if getuser.last_post > minutestimer:
        # user still hasnt passed enough time
        c = getuser.last_post - minutestimer
        x = strfdelta(c, "%M:%S")
        return 0, x
    else:
        # time has passed
        x = 1
        return 1, x


def lastcommont(user_id):
    # time in between comments
    # 1 minute
    setlimit = 1
    now = datetime.utcnow()
    minutestimer = datetime.utcnow() - timedelta(minutes=setlimit)
    getuser = db.session.query(UserTimers).filter_by(user_id=user_id).first()

    if getuser.last_comment is None:
        getuser.last_comment = now
        db.session.add(getuser)
        db.session.commit()
    if getuser.last_comment > minutestimer:
        # user still hasnt passed enough time
        c = getuser.last_comment - minutestimer
        x = strfdelta(c, "%M:%S")

        return 0, x
    else:

        # time has passed
        x = 1
        return 1, x


def lastcommoncreation(user_id):
    # time in between creation of commons
    # 60 minutes
    setlimit = 60
    now = datetime.utcnow()
    minutestimer = datetime.utcnow() - timedelta(minutes=setlimit)
    getuser = db.session.query(UserTimers).filter_by(user_id=user_id).first()

    if getuser.last_common_creation is None:
        getuser.last_common_creation = now
        db.session.add(getuser)
        db.session.commit()
    if getuser.last_common_creation > minutestimer:
        # user still hasnt passed enough time
        c = getuser.last_common_creation - minutestimer
        x = strfdelta(c, "%M:%S")
        return 0, x
    else:
        # time has passed
        x = 1
        return 1, x


def lastreport(user_id):
    # time in between creation of commons
    # 60 minutes
    setlimit = 1
    now = datetime.utcnow()
    minutestimer = datetime.utcnow() - timedelta(minutes=setlimit)
    getuser = db.session.query(UserTimers).filter_by(user_id=user_id).first()

    if getuser.last_report is None:
        getuser.last_report = now
        db.session.add(getuser)
        db.session.commit()
    if getuser.last_report > minutestimer:
        # user still hasnt passed enough time
        c = getuser.last_report - minutestimer
        x = strfdelta(c, "%M:%S")
        return 0, x
    else:
        # time has passed
        x = 1
        return 1, x
