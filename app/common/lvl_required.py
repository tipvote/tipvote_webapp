from app.models import User, UserStats


def lvl_req(userid, lvlnumber):

    userstats = UserStats.query.filter(userid == UserStats.user_id).first()

    if lvlnumber <= userstats.user_level:
        # the level needed is met
        return True
    else:
        # user is not high enough level
        return False


