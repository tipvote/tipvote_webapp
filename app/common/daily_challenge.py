
def daily_challenge(user_id, category):
    from app import db
    from app.classes.user import User, DailyChallenge, UserDailyChallenge
    from datetime import datetime
    from app.common.functions import floating_decimals


    now = datetime.utcnow()
    # category 1 = post something
    # category 2 = comment on a post
    # category 3 = vote on a  post
    # category 4 = vote on a  comment

    getuser = db.session.query(User)\
        .filter(User.id == user_id)\
        .first()

    getuserdaily = db.session.query(UserDailyChallenge)\
        .filter(UserDailyChallenge.user_id == user_id)\
        .all()

    list_of_challenges = []
    for f in getuserdaily:
        list_of_challenges.append(f.id_of_challenge)

    if category in list_of_challenges:
        the_challenge = db.session.query(UserDailyChallenge)\
            .filter(UserDailyChallenge.user_id == user_id, UserDailyChallenge.id_of_challenge  == category)\
            .first()

        if the_challenge.completed == 0:
            new_number_to_complete = the_challenge.current_number_of_times + 1
            the_challenge.current_number_of_times = new_number_to_complete

            # Calculate width to next level
            width_calculator_full = (the_challenge.current_number_of_times / the_challenge.how_many_to_complete) * 100
            width_calculator = floating_decimals(width_calculator_full, 0)

            the_challenge.user_width_next_level = width_calculator
            if the_challenge.current_number_of_times == the_challenge.how_many_to_complete:
                the_challenge.completed == 1

                ## TODO send the coin to a person

            db.session.add(the_challenge)

            db.session.commit()
        else:
            pass
    else:
        pass