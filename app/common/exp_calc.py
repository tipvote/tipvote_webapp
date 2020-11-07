
def exppoint(user_id, category):
    from app import db
    from app.classes.models import ExpTable
    from app.classes.user import UserStats
    from datetime import datetime
    from app.common.functions import floating_decimals

    # category 1 = User Posted
    # category 2 = User commented
    # category 3 = upvoted
    # category 4 = downvoted
    # category 5 = sent coin
    # category 6 = recieved coin
    # category 7 = created sub

    now = datetime.utcnow()

    points_createdsub = 50
    created_post = 10
    created_comment = 5
    points_upvote = 2
    points_downvote = -5
    points_sentcoin = 100
    points_recievedcoin = 10
    gave_vote = 1

    # get current user stats
    getuser = db.session.query(UserStats)
    getuser = getuser.filter(UserStats.user_id == user_id)
    guser = getuser.first()

    # current user points
    currentpoints = guser.user_exp
    if 0 <= guser.user_level <= 2:
        experienceperlevel = 250
    elif 3 <= guser.user_level <= 5:
        experienceperlevel = 500
    elif 6 <= guser.user_level <= 7:
        experienceperlevel = 1000
    elif 8 <= guser.user_level <= 10:
        experienceperlevel = 2000
    elif 11 <= guser.user_level <= 14:
        experienceperlevel = 4000
    elif 16 <= guser.user_level <= 20:
        experienceperlevel = 6000
    elif 21 <= guser.user_level <= 25:
        experienceperlevel = 10000
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 15500
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 25000
    elif 26 <= guser.user_level <= 30:
        experienceperlevel = 50000
    elif 30 <= guser.user_level <= 50:
        experienceperlevel = 50000
    elif 51 <= guser.user_level <= 100:
        experienceperlevel = 100000
    elif 101 <= guser.user_level <= 151:
        experienceperlevel = 100000
    else:
        experienceperlevel = 1000000

    # category 1 = User Posted
    if category == 1:

        # ads current points to variable points
        addpoints = int(currentpoints + created_post)
        # uses exp per level schema
        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)

        # add exp table
        exp = ExpTable(
            user_id=user_id,
            type=1,
            amount=created_post,
            created=now,
        )

        db.session.add(exp)

    # category 2 = User commented
    elif category == 2:
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

    # category 3 = got upvoted
    elif category == 3:
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

    # category 4 = got downvote
    elif category == 4:
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

    # category 5 = sent coin
    elif category == 5:
        addpoints = int((currentpoints + points_sentcoin))

        levels_up, exp_to_next = divmod(addpoints, experienceperlevel)

        exp = ExpTable(
            user_id=user_id,
            type=5,
            amount=points_sentcoin,
            created=now,
        )

        db.session.add(exp)

    # category 6 = recieved coin
    elif category == 6:
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

    # category 7 = created sub
    elif category == 7:
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

    # category 8 = gave vote
    elif category == 8:
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

    db.session.commit()

    # if user leveled up
    if levels_up > 0:
        guser.user_level = guser.user_level + levels_up
        randomcoin(user_id=user_id, newlevel=guser.user_level)

    # set new width of exp bar
    if 0 <= guser.user_level <= 2:
        user1width_calculator = (guser.user_exp / 250) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 3 <= guser.user_level <= 5:
        user1width_calculator = (guser.user_exp / 500) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 6 <= guser.user_level <= 7:
        user1width_calculator = (guser.user_exp / 1000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 8 <= guser.user_level <= 10:
        user1width_calculator = (guser.user_exp / 2000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 11 <= guser.user_level <= 14:
        user1width_calculator = (guser.user_exp / 4000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 16 <= guser.user_level <= 20:
        user1width_calculator = (guser.user_exp / 6000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 21 <= guser.user_level <= 25:
        user1width_calculator = (guser.user_exp / 10000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 15500) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 25000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 26 <= guser.user_level <= 30:
        user1width_calculator = (guser.user_exp / 50000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 30 <= guser.user_level <= 50:
        user1width_calculator = (guser.user_exp / 50000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    elif 51 <= guser.user_level <= 100:
        user1width_calculator = (guser.user_exp / 100000) * 100
        user1width = floating_decimals(user1width_calculator, 0)
    else:
        user1width_calculator = (guser.user_exp / 100000) * 100
        user1width = floating_decimals(user1width_calculator, 0)

    guser.user_exp = exp_to_next
    guser.user_width_next_level = str(user1width)

    db.session.add(guser)
    db.session.commit()


def randomcoin(user_id, newlevel):
    from app.classes.user import UserCoins, User
    from app.models import Coins, DisplayCoins
    import random
    from app import db
    from datetime import datetime

    now = datetime.utcnow()
    theuser = db.session.query(User) \
        .filter(User.id == user_id) \
        .first()

    findrandomcoin = random.randint(2, 5)
    findrandomcoin_2 = random.randint(2, 5)
    howmanycoins = 1
    userlevelstring = int(newlevel)

    # coin 1
    getthatcoin = db.session.query(Coins) \
        .filter(Coins.id == findrandomcoin) \
        .first()

    seeifuserhascoin1 = db.session.query(UserCoins) \
        .filter(UserCoins.user_id == user_id,
                UserCoins.coin_name == getthatcoin.coin_name) \
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
    getsecondcoin = db.session.query(Coins) \
        .filter(Coins.id == findrandomcoin_2) \
        .first()
    seeifuserhascoin2 = db.session.query(UserCoins) \
        .filter(UserCoins.user_id == user_id,
                UserCoins.coin_name == getsecondcoin.coin_name) \
        .first()
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


    # BONUS
    if 5 <= newlevel <= 10:
        getlevelcoins = db.session.query(Coins) \
            .filter(Coins.id == 5) \
            .first()
        seeifuserhascoinz_level = db.session.query(UserCoins) \
            .filter(UserCoins.user_id == user_id,
                    UserCoins.coin_id == 5) \
            .first()
        if seeifuserhascoinz_level is None:
            createnewcoin_level = UserCoins(
                image_thumbnail=getlevelcoins.image_thumbnail,
                user_name=theuser.user_name,
                user_id=theuser.id,
                obtained=now,
                quantity=5,
                coin_name=getlevelcoins.coin_name,
                coin_rarity=getlevelcoins.coin_rarity,
                coin_description=getlevelcoins.coin_description,
                points_value=getlevelcoins.points_value,
                coin_id=getlevelcoins.id
            )
            db.session.add(createnewcoin_level)
        else:
            currentamount = seeifuserhascoinz_level.quantity
            newamount = currentamount + 5
            seeifuserhascoinz_level.quantity = newamount
            db.session.add(seeifuserhascoinz_level)

    elif 11 <= newlevel <= 20:

        getlevelcoins = db.session.query(Coins) \
            .filter(Coins.id == 5) \
            .first()
        seeifuserhascoinz_level = db.session.query(UserCoins) \
            .filter(UserCoins.user_id == user_id,
                    UserCoins.coin_id == 5) \
            .first()
        if seeifuserhascoinz_level is None:
            createnewcoin_level = UserCoins(
                image_thumbnail=getlevelcoins.image_thumbnail,
                user_name=theuser.user_name,
                user_id=theuser.id,
                obtained=now,
                quantity=10,
                coin_name=getlevelcoins.coin_name,
                coin_rarity=getlevelcoins.coin_rarity,
                coin_description=getlevelcoins.coin_description,
                points_value=getlevelcoins.points_value,
                coin_id=getlevelcoins.id
            )
            db.session.add(createnewcoin_level)
        else:
            currentamount = seeifuserhascoinz_level.quantity
            newamount = currentamount + 10
            seeifuserhascoinz_level.quantity = newamount
            db.session.add(seeifuserhascoinz_level)

    elif 21 <= newlevel <= 100:
        # give 10 5 coins
        getlevelcoins = db.session.query(Coins) \
            .filter(Coins.id == 5) \
            .first()
        seeifuserhascoinz_level = db.session.query(UserCoins) \
            .filter(UserCoins.user_id == user_id,
                    UserCoins.coin_id == 5) \
            .first()
        if seeifuserhascoinz_level is None:
            createnewcoin_level = UserCoins(
                image_thumbnail=getlevelcoins.image_thumbnail,
                user_name=theuser.user_name,
                user_id=theuser.id,
                obtained=now,
                quantity=50,
                coin_name=getlevelcoins.coin_name,
                coin_rarity=getlevelcoins.coin_rarity,
                coin_description=getlevelcoins.coin_description,
                points_value=getlevelcoins.points_value,
                coin_id=getlevelcoins.id
            )
            db.session.add(createnewcoin_level)
        else:
            currentamount = seeifuserhascoinz_level.quantity
            newamount = currentamount + 50
            seeifuserhascoinz_level.quantity = newamount
            db.session.add(seeifuserhascoinz_level)

    else:
        pass

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
