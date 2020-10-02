
def exppoint(user_id, type):
    from app import db
    from app.models import ExpTable, UserStats
    from datetime import datetime
    from app.common.functions import floating_decimals

    # type 1 = User Posted
    # type 2 = User commented
    # type 3 = upvoted
    # type 4 = downvoted
    # type 5 = sent coin
    # type 6 = recieved coin
    # type 7 = created sub

    points_createdsub = 50
    created_post = 25
    created_comment = 5
    points_upvote = 3
    points_downvote = -5
    points_sentcoin = 100
    points_recievedcoin = 100
    gave_vote = 1

    now = datetime.utcnow()
    # get current user stats
    getuser = db.session.query(UserStats)
    getuser = getuser.filter(UserStats.user_id == user_id)
    guser = getuser.first()

    # current user points
    currentpoints = guser.user_exp
    if 1 <= guser.user_level <= 3:
        experienceperlevel = 200
    elif 4 <= guser.user_level <= 7:
        experienceperlevel = 300
    elif 8 <= guser.user_level <= 10:
        experienceperlevel = 500
    elif 11 <= guser.user_level <= 14:
        experienceperlevel = 1000
    elif 16 <= guser.user_level <= 20:
        experienceperlevel = 1500
    elif 21 <= guser.user_level <= 25:
        experienceperlevel = 2250
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 5500
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 10000
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 10000
    elif 30 <= guser.user_level <= 50:
        experienceperlevel = 10000
    elif 51 <= guser.user_level <= 100:
        experienceperlevel = 10000
    elif 101 <= guser.user_level <= 151:
        experienceperlevel = 10000
    else:
        experienceperlevel = 1000

    # type 1 = User Posted
    if type == 1:

        # ads current points to variable points
        addpoints = int(currentpoints + created_post)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=1,
            amount=created_post,
            created=now,
        )

        db.session.add(exp)

    # type 2 = User commented
    elif type == 2:
        # adds current points to variable points
        addpoints = int(currentpoints + created_comment)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=2,
            amount=created_comment,
            created=now,
        )

        db.session.add(exp)

    # type 3 = got upvoted
    elif type == 3:
        # adds current points to variable points
        addpoints = int(currentpoints + points_upvote)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=3,
            amount=points_upvote,
            created=now,
        )

        db.session.add(exp)

    # type 4 = got downvote
    elif type == 4:
        # adds current points to variable points
        addpoints = int(currentpoints + points_downvote)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=4,
            amount=points_downvote,
            created=now,
        )

        db.session.add(exp)

    # type 5 = sent coin
    elif type == 5:
        addpoints = int((currentpoints + points_sentcoin))

        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)

        exp = ExpTable(
            user_id=user_id,
            type=5,
            amount=points_sentcoin,
            created=now,
        )

        db.session.add(exp)

    # type 6 = recieved coin
    elif type == 6:
        # adds current points to variable points
        addpoints = int(currentpoints + points_recievedcoin)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=6,
            amount=points_recievedcoin,
            created=now,
        )

        db.session.add(exp)

    # type 7 = created sub
    elif type == 7:
        # adds current points to variable points
        addpoints = int(currentpoints + points_createdsub)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=7,
            amount=points_createdsub,
            created=now,
        )

        db.session.add(exp)

    # type 8 = gave vote
    elif type == 8:
        # ads current points to variable points
        addpoints = int(currentpoints + gave_vote)
        # uses exp per level chema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)
        # add stats to user

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=8,
            amount=points_createdsub,
            created=now,
        )

        db.session.add(exp)

    else:
        exp_to_next = guser.user_exp
        levels_up = 0
    # finished elif stuff

    # if user leveled up
    if levels_up > 0:
        guser.user_level = guser.user_level + levels_up
        randomcoin(user_id=user_id, newlevel=guser.user_level)
        # random coin

    # set new width of exp bar
    if 1 <= guser.user_level <= 3:
        user1width_calculator = (guser.user_exp / 200) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 4 <= guser.user_level <= 7:
        user1width_calculator = (guser.user_exp / 300) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 8 <= guser.user_level <= 10:
        user1width_calculator = (guser.user_exp / 500) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 11 <= guser.user_level <= 14:
        user1width_calculator = (guser.user_exp / 1000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 16 <= guser.user_level <= 20:
        user1width_calculator = (guser.user_exp / 1500) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 21 <= guser.user_level <= 25:
        user1width_calculator = (guser.user_exp / 2250) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 5500) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 30 <= guser.user_level <= 50:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 51 <= guser.user_level <= 100:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    else:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)

    guser.user_exp = exp_to_next
    guser.user_width_next_level = str(user1width)

    db.session.add(guser)
    db.session.commit()


def randomcoin(user_id, newlevel):
    from app.models import Coins, UserCoins, DisplayCoins, User
    import random
    from app import db
    from datetime import datetime

    now = datetime.utcnow()
    theuser = db.session.query(User).filter(User.id == user_id).first()

    findrandomcoin = random.randint(2, 5)
    findrandomcoin_2 = random.randint(2, 5)
    howmanycoins = 1
    userlevelstring = int(newlevel)

    # coin 1
    getthatcoin = db.session.query(Coins)\
        .filter(Coins.id == findrandomcoin)\
        .first()
    seeifuserhascoin1 = db.session.query(UserCoins)\
        .filter(UserCoins.user_id == user_id,
                UserCoins.coin_name == getthatcoin.coin_name)\
        .first()

    if seeifuserhascoin1 is None:

        createnewcoin = UserCoins(
                        image_thumbnail=getthatcoin.image_thumbnail,
                        user_name=theuser.user_name,
                        user_id=theuser.id,
                        obtained=now,
                        quantity=howmanycoins,
                        coin_name=getthatcoin.coin_name,
                        coin_rarity=getthatcoin.coin_rarity,
                        coin_description=getthatcoin.coin_description,
                        points_value=getthatcoin.points_value,
                        coin_id=getthatcoin.id
                        )
        db.session.add(createnewcoin)
    else:
        currentamount = seeifuserhascoin1.quantity
        newamount = currentamount + 1
        seeifuserhascoin1.quantity = newamount
        db.session.add(seeifuserhascoin1)

    # coin 2
    getsecondcoin = db.session.query(Coins).filter(Coins.id == findrandomcoin_2).first()
    seeifuserhascoin2 = db.session.query(UserCoins).filter(UserCoins.user_id == user_id,
                                                           UserCoins.coin_name == getsecondcoin.coin_name).first()
    if seeifuserhascoin2 is None:
        createnewcoin_2 = UserCoins(
                        image_thumbnail=getsecondcoin.image_thumbnail,
                        user_name=theuser.user_name,
                        user_id=theuser.id,
                        obtained=now,
                        quantity=howmanycoins,
                        coin_name=getsecondcoin.coin_name,
                        coin_rarity=getsecondcoin.coin_rarity,
                        coin_description=getsecondcoin.coin_description,
                        points_value=getsecondcoin.points_value,
                        coin_id=getsecondcoin.id
                        )
        db.session.add(createnewcoin_2)
    else:
        currentamount = seeifuserhascoin2.quantity
        newamount = currentamount + 1
        seeifuserhascoin2.quantity = newamount
        db.session.add(seeifuserhascoin2)

    createdisplayflash = DisplayCoins(
                    created=now,
                    user_name=theuser.user_name,
                    user_id=theuser.id,
                    image_thumbnail_0=getthatcoin.image_thumbnail,
                    coin_name_0=getthatcoin.coin_name,
                    coin_rarity_0=getthatcoin.coin_rarity,
                    coin_description_0=getthatcoin.coin_description,
                    points_value_0=getthatcoin.points_value,
                    image_thumbnail_1=getsecondcoin.image_thumbnail,
                    coin_name_1=getsecondcoin.coin_name,
                    coin_rarity_1=getsecondcoin.coin_rarity,
                    coin_description_1=getsecondcoin.coin_description,
                    points_value_1=getsecondcoin.points_value,
                    seen_by_user=0,
                    new_user_level=userlevelstring,
                    )

    db.session.add(createdisplayflash)
    db.session.commit()
