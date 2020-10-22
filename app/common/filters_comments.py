from app import app


@app.template_filter('seeifvoted')
def seeifvoted(postid):
    """
    see if user voted on a post
    """
    from app.models import PostUpvotes
    from app import db
    from flask_login import current_user

    if current_user.is_authenticated:
        get_vote = db.session.query(PostUpvotes).filter(PostUpvotes.user_id == current_user.id,
                                                        PostUpvotes.post_id == postid).first()

        if get_vote:

            if get_vote.vote_up == 1:
                vote = 1
            elif get_vote.vote_up == 0:
                vote = 2
            else:
                vote = 0
        else:
            vote = 0
    else:
        vote = 0

    return vote