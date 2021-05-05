
def daily_challenge(user_id, category):
    from app import db
    from app.classes.user import User, DailyChallenge, UserDailyChallenge
    from datetime import datetime
    from app.common.functions import floating_decimals
    from app.wallet_bch.wallet_btccash_daily import sendcoin_user_daily_bch
    from app.wallet_btc.wallet_btc_daily import sendcoin_user_daily_btc
    from app.wallet_xmr.wallet_xmr_daily import sendcoin_user_daily_xmr
    # category 1 = post something
    # category 2 = comment on a post
    # category 3 = vote on a  post
    # category 4 = vote on a  comment

    getuserdaily = db.session.query(UserDailyChallenge)\
        .filter(UserDailyChallenge.user_id == user_id)\
        .all()

    list_of_challenges = []
    for f in getuserdaily:
        list_of_challenges.append(f.category_of_challenge)

    if category in list_of_challenges:
        the_challenge = db.session.query(UserDailyChallenge)\
            .filter(UserDailyChallenge.user_id == user_id, UserDailyChallenge.category_of_challenge  == category)\
            .first()

        if the_challenge.completed == 0:
            new_number_to_complete = the_challenge.current_number_of_times + 1
            the_challenge.current_number_of_times = new_number_to_complete

            # Calculate width to next level
            width_calculator_full = (the_challenge.current_number_of_times / the_challenge.how_many_to_complete) * 100
            width_calculator = floating_decimals(width_calculator_full, 0)

            the_challenge.user_width_next_level = width_calculator

            # see if user completed the daily missions
            if the_challenge.current_number_of_times == the_challenge.how_many_to_complete:

                # make the challenge completed
                the_challenge.completed = 1

                # send the coin
                # if bitcoin
                if the_challenge.reward_coin == 1:
                    sendcoin_user_daily_btc(user_id=user_id, amount=the_challenge.reward_amount)
                # if bitcoin cash
                elif the_challenge.reward_coin == 2:
                    sendcoin_user_daily_bch(user_id=user_id, amount=the_challenge.reward_amount)
                # if monero
                elif the_challenge.reward_coin == 3:
                    sendcoin_user_daily_xmr(user_id=user_id, amount=the_challenge.reward_amount)
                else:
                    pass

            # add to db
            db.session.add(the_challenge)
            db.session.commit()
