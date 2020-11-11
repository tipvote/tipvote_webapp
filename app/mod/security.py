from app.classes.subforum import SubForums, Mods
from flask_login import current_user
from app import db
from flask import flash

def modcheck(thesub, theuser):

    # see if user is a creator
    seeifowner = db.session.query(SubForums)
    seeifowner = seeifowner.filter(SubForums.subcommon_name == thesub.subcommon_name,
                                   SubForums.creator_user_id == theuser.id)
    seeifowner = seeifowner.first()

    if seeifowner is None:
        owner_status = 0
    else:
        owner_status = 1


    # see if user is a mod
    seeifmod = db.session.query(Mods)
    seeifmod = seeifmod.filter(Mods.subcommon_id == thesub.id, Mods.user_id == theuser.id)
    seeifmod = seeifmod.first()
    if seeifmod is None:
        mod_status = 0
    else:
        mod_status = 1


    # see if user is an admin
    if current_user.admin == 1:
        admin_status = 1
    else:
        admin_status = 0


    # run security check
    user_status = owner_status + mod_status + admin_status

    return user_status
