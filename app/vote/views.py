# flask imports
from flask import \
    redirect, \
    url_for, \
    flash, \
    request, \
    jsonify
import time
from flask_login import current_user

from app import db

from app.common.exp_calc import exppoint
from app.common.decorators import login_required

from app.vote import vote

from app.models import \
    CommentsUpvotes, \
    PostUpvotes, \
    Banned, \
    CommonsPost, \
    Comments, \
    PrivateMembers, \
    SubForums, \
    UserStats


@vote.route('/downvotecomment/<int:commentid>', methods=['POST'])
@login_required
def downvote_comment(commentid):
    """
    upvote post
    """
    # get the post by its id

    if request.method == 'POST':

        # get the comment
        getcomment = db.session.query(Comments) \
            .filter(Comments.id == commentid) \
            .first()

        # get the post
        post = db.session.query(CommonsPost) \
            .filter(CommonsPost.id == getcomment.commons_post_id) \
            .first()

        # see if user voted
        seeifvoted = db.session.query(CommentsUpvotes) \
            .filter(CommentsUpvotes.user_id == current_user.id,
                    CommentsUpvotes.comment_id == getcomment.id) \
            .first()

        # get the current sub
        getcurrentsub = db.session.query(SubForums) \
            .filter(SubForums.subcommon_name == post.subcommon_name) \
            .first()

        # get comment user stats
        comment_owner_stats = db.session.query(UserStats) \
            .filter(UserStats.user_id == getcomment.user_id) \
            .first()

        # see if banned or if private
        seeifbanned = db.session.query(Banned) \
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == getcurrentsub.id) \
            .first()

        # set easy variables
        subid = getcurrentsub.id
        subtype = getcurrentsub.type_of_subcommon
        str_comment_id = str(commentid)

        if post is None:
            return jsonify({
                'result': 'Post has been removed or not found.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcomment is None:
            return jsonify({
                'result': 'Comment does not exist.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if post.hidden == 1:
            return jsonify({
                'result': post.id,
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if post.locked == 1:
            return jsonify({
                'result': 'Post has been locked.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcomment.user_id == current_user.id:
            return jsonify({
                'result': 'You can not vote on your own comments.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if seeifvoted is not None:
            return jsonify({
                'result': 'You have already voted.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcurrentsub is None:
            return jsonify({
                'result': 'Room does not exist.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        # if user on banned list turn him away
        if seeifbanned is not None:
            return jsonify({
                'result': 'You are banned from this room.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        # if room is private
        if subtype == 1:
            seeifuserinvited = db.session.query(PrivateMembers).filter(
                current_user.id == PrivateMembers.user_id,
                PrivateMembers.subcommon_id == subid).first()
            # if user is not on the list turn him away
            if seeifuserinvited is None:
                return jsonify({
                    'result': 'Room is a private community!',
                    'thecommentid': str_comment_id,
                    'newnumber': None
                })

        currentdownvotes = getcomment.downvotes_on_comment
        # add the vote to current votes
        newvotes_down = currentdownvotes - 1
        # set post variable to this new post number
        getcomment.downvotes_on_comment = newvotes_down
        # subtract from downvotes
        newvotes_up = getcomment.upvotes_on_comment
        getcommentexp = newvotes_up + newvotes_down
        # set exp number to exp_commons
        getcomment.total_exp_commons = getcommentexp

        # number used to show ajax response
        # It takes the current exp (upvotes - downvotes) then adds 1
        # downvote comment
        newvotenumber = getcomment.total_exp_commons

        # raise all in path for thread votes down
        if getcomment.comment_parent_id is None:
            # get comments of this comment and raise there thread downvotes for sorting purposes
            getrelativecomments = db.session.query(Comments)\
                .filter(Comments.path.like(getcomment.path + '%'))
            for comment in getrelativecomments:
                comment.thread_downvotes = newvotes_down
                db.session.add(comment)

            getcomment.thread_downvotes = newvotes_down
            db.session.add(getcomment)

        # add to user stats
        current_downvotes_comment = comment_owner_stats.comment_downvotes
        new_downvotes_comment = current_downvotes_comment + 1
        comment_owner_stats.comment_downvotes = new_downvotes_comment

        # add exp points
        exppoint(user_id=current_user.id, category=8)
        exppoint(user_id=getcomment.user_id, category=4)

        # add user_id to vote so user doesnt double vote
        create_new_vote = CommentsUpvotes(
            user_id=current_user.id,
            comment_id=getcomment.id,
        )

        db.session.add(comment_owner_stats)
        db.session.add(getcomment)
        db.session.add(create_new_vote)
        db.session.commit()

        if seeifvoted is not None:
            return jsonify({
                'result': 'You have already voted.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })
        else:
            return jsonify({
                'result': 'Downvoted!',
                'thecommentid': str_comment_id,
                'newnumber': newvotenumber
            })


@vote.route('/upvotecomment/<int:commentid>', methods=['POST'])
@login_required
def upvote_comment(commentid):
    """
    upvote post
    """
    # get the post by its id

    if request.method == 'POST':

        # get the comment
        getcomment = db.session.query(Comments) \
            .filter_by(id=commentid) \
            .first()

        # get the post
        post = db.session.query(CommonsPost) \
            .filter_by(id=getcomment.commons_post_id) \
            .first()

        # see if user voted
        seeifvoted = db.session.query(CommentsUpvotes) \
            .filter(CommentsUpvotes.user_id == current_user.id,
                    CommentsUpvotes.comment_id == getcomment.id) \
            .first()

        # get the current sub
        getcurrentsub = db.session.query(SubForums) \
            .filter(SubForums.subcommon_name == post.subcommon_name) \
            .first()

        # get comment user stats
        comment_owner_stats = db.session.query(UserStats) \
            .filter(UserStats.user_id == getcomment.user_id) \
            .first()

        # see if banned or if private
        seeifbanned = db.session.query(Banned) \
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == getcurrentsub.id) \
            .first()

        # set easy variables
        subid = getcurrentsub.id
        subtype = getcurrentsub.type_of_subcommon
        str_comment_id = str(commentid)

        if post is None:
            return jsonify({
                'result': 'Post has been removed or not found.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcomment is None:
            return jsonify({
                'result': 'Comment does not exist.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if post.hidden == 1:
            return jsonify({
                'result': 'Post has been deleted.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if post.locked == 1:
            return jsonify({
                'result': 'Post has been locked.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcomment.user_id == current_user.id:
            return jsonify({
                'result': 'You can not vote on your own comments.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if seeifvoted is not None:
            return jsonify({
                'result': 'You have already voted.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        if getcurrentsub is None:
            return jsonify({
                'result': 'Room does not exist',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        # if user on banned list turn him away
        if seeifbanned is not None:
            return jsonify({
                'result': 'You are banned from this room.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })

        # if sub is private
        if subtype == 1:
            seeifuserinvited = db.session.query(PrivateMembers).filter(
                current_user.id == PrivateMembers.user_id,
                PrivateMembers.subcommon_id == subid).first()
            # if user is not on the list turn him away
            if seeifuserinvited is None:
                return jsonify({
                    'result': 'Room is a private community!',
                    'thecommentid': str_comment_id,
                    'newnumber': None
                })

        currentupvotes = getcomment.upvotes_on_comment
        # add the vote to current votes
        newvotes_up = currentupvotes + 1
        # set post variable to this new post number
        getcomment.upvotes_on_comment = newvotes_up
        # add  downvotes
        newvotes_down = getcomment.downvotes_on_comment
        getcommentexp = newvotes_up + newvotes_down
        # set exp number to exp_commonts
        getcomment.total_exp_commons = getcommentexp

        # number used to show ajax response
        # It takes the current exp (upvotes - downvotes) then adds 1
        # upvote comment
        newvotenumber = getcomment.total_exp_commons

        # get comments of this comment and raise
        # there thread upvotes for sorting purposes
        if getcomment.comment_parent_id is None:
            getrelativecomments = db.session.query(Comments) \
                .filter(Comments.path.like(getcomment.path + '%'))

            for comment in getrelativecomments:
                comment.thread_upvotes = newvotes_up

                db.session.add(comment)
            getcomment.thread_upvotes = newvotes_up
            db.session.add(getcomment)

        # add to user stats
        current_upvotes_comment = comment_owner_stats.comment_upvotes
        new_upvotes_comment = current_upvotes_comment + 1
        comment_owner_stats.comment_upvotes = new_upvotes_comment

        # add exp points
        exppoint(user_id=current_user.id, category=8)
        exppoint(user_id=getcomment.user_id, category=3)

        # add user_id to vote so user doesnt double vote
        create_new_vote = CommentsUpvotes(
            user_id=current_user.id,
            comment_id=getcomment.id,
        )

        db.session.add(comment_owner_stats)
        db.session.add(getcomment)
        db.session.add(create_new_vote)
        db.session.commit()
        if seeifvoted is not None:
            return jsonify({
                'result': 'You have already voted.',
                'thecommentid': str_comment_id,
                'newnumber': None
            })
        else:
            return jsonify({
                'result': 'Upvoted!',
                'thecommentid': str_comment_id,
                'newnumber': newvotenumber
            })


@vote.route('/upvotepost/<int:postid>', methods=['POST'])
@login_required
def upvote_post(postid):
    """
    upvote post
    """
    # get the post by its id
    str_post_id = str(postid)

    if request.method == 'POST':

        getpost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()

        getcurrentsub = db.session.query(SubForums) \
            .filter(SubForums.id == getpost.subcommon_id) \
            .first()

        subid = getcurrentsub.id
        subtype = getcurrentsub.type_of_subcommon

        # see if user already voted or not
        seeifvoted = db.session.query(PostUpvotes) \
            .filter(PostUpvotes.user_id == current_user.id,
                    PostUpvotes.post_id == postid) \
            .first()

        seeifbanned = db.session.query(Banned) \
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == subid) \
            .first()

        # post owner stats
        post_owner_stats = db.session.query(UserStats) \
            .filter(UserStats.user_id == getpost.user_id) \
            .first()

        if subtype == 1:
            seeifuserinvited = db.session.query(PrivateMembers) \
                .filter(current_user.id == PrivateMembers.user_id,
                        PrivateMembers.subcommon_id == subid) \
                .first()
        else:
            seeifuserinvited = 0

        if getpost is None:
            return jsonify({
                'result': 'Post has been deleted or doesnt exist',
                'thepostid': str_post_id,
                'newnumber': 0
            })

        elif getpost.hidden == 1:
            return jsonify({
                'result': 'Post has been deleted',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif getpost.locked == 1:
            return jsonify({
                'result': 'Post has been locked.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif getpost.user_id == current_user.id:
            return jsonify({
                'result': 'You cannot upvote your own posts.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif seeifvoted is not None:
            return jsonify({
                'result': 'You already voted',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        # if user on banned list turn him away
        elif seeifbanned is not None:
            return jsonify({
                'result': 'You were banned from this room.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })
        # if sub is private
        elif subtype == 1:
            # if user is not on the list turn him away
            if seeifuserinvited is None:

                return jsonify({
                    'result': 'Room Is a private Community.',
                    'thepostid': str_post_id,
                    'newnumber': getpost.hotness_rating_now
                })
        else:
            currentupvotes = getpost.upvotes_on_post
            # add the vote to current votes
            newvotes_up = currentupvotes + 1
            # set post variable to this new post number
            getpost.upvotes_on_post = newvotes_up
            # subtract from downvotes
            getpostexp = newvotes_up + getpost.downvotes_on_post
            # set exp number to exp_commons
            getpost.total_exp_commons = getpostexp

            # current hotness rating
            currenthotness = getpost.hotness_rating_now
            newhotness = currenthotness + 1
            getpost.hotness_rating_now = newhotness

            # number used to show ajax response
            # It takes the current exp (upvotes - downvotes) then adds 1
            # upvote post
            newvotenumber = getpost.highest_exp_reached + 1

            # add exp points
            exppoint(user_id=current_user.id, category=8)
            exppoint(user_id=getpost.user_id, category=3)

            # add to user stats
            current_upvotes_posts = post_owner_stats.post_upvotes
            new_upvotes_posts = current_upvotes_posts + 1
            post_owner_stats.post_upvotes = new_upvotes_posts

            create_new_vote = PostUpvotes(
                user_id=current_user.id,
                post_id=getpost.id,
            )
            # see if user already voted or not
            seeifvoted = db.session.query(PostUpvotes) \
                .filter(PostUpvotes.user_id == current_user.id,
                        PostUpvotes.post_id == postid) \
                .first()

            # add and commit
            db.session.add(create_new_vote)
            db.session.add(getpost)
            db.session.add(post_owner_stats)
            db.session.commit()

            if seeifvoted is None:
                return jsonify({
                    'result': 'Upvoted!',
                    'thepostid': str_post_id,
                    'newnumber': newvotenumber
                })
            else:
                return jsonify({
                    'result': 'You already voted',
                    'thepostid': str_post_id,
                    'newnumber': getpost.hotness_rating_now
                })


@vote.route('/downvotepost/<int:postid>', methods=['POST'])
@login_required
def downvote_post(postid):
    """
    downvote post
    """
    # get the post by its id
    str_post_id = str(postid)

    if request.method == 'POST':

        getpost = db.session.query(CommonsPost).filter(CommonsPost.id == postid).first()

        getcurrentsub = db.session.query(SubForums) \
            .filter(SubForums.id == getpost.subcommon_id) \
            .first()

        subid = getcurrentsub.id
        subtype = getcurrentsub.type_of_subcommon

        # see if user already voted or not
        seeifvoted = db.session.query(PostUpvotes) \
            .filter(PostUpvotes.user_id == current_user.id,
                    PostUpvotes.post_id == postid) \
            .first()

        seeifbanned = db.session.query(Banned) \
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == subid) \
            .first()

        # add to user stats
        post_owner_stats = db.session.query(UserStats) \
            .filter(UserStats.user_id == getpost.user_id) \
            .first()

        if subtype == 1:
            seeifuserinvited = db.session.query(PrivateMembers) \
                .filter(current_user.id == PrivateMembers.user_id,
                        PrivateMembers.subcommon_id == subid) \
                .first()
        else:
            seeifuserinvited = 0

        if getpost is None:
            return jsonify({
                'result': 'Post has been deleted or doesnt exist',
                'thepostid': str_post_id,
                'newnumber': 0
            })

        elif getpost.hidden == 1:
            return jsonify({
                'result': 'Post has been deleted',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif getpost.locked == 1:
            return jsonify({
                'result': 'Post has been locked.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif getpost.user_id == current_user.id:
            return jsonify({
                'result': 'You cannot upvote your own posts.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        elif seeifvoted is not None:
            return jsonify({
                'result': 'You already voted',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })

        # if user on banned list turn him away
        elif seeifbanned is not None:
            return jsonify({
                'result': 'You were banned from this room.',
                'thepostid': str_post_id,
                'newnumber': getpost.hotness_rating_now
            })
        # if sub is private
        elif subtype == 1:
            # if user is not on the list turn him away
            if seeifuserinvited is None:

                return jsonify({
                    'result': 'Room Is a private Community.',
                    'thepostid': str_post_id,
                    'newnumber': getpost.hotness_rating_now
                })
            else:
                pass
        else:
            currentdownvotes = getpost.downvotes_on_post
            # add the vote to current votes
            newvotes_down = currentdownvotes - 1
            # set post variable to this new post number
            getpost.downvotes_on_post = newvotes_down
            # subtract from downvotes
            getpostexp = getpost.upvotes_on_post + newvotes_down
            # set exp number to exp_commons
            getpost.total_exp_commons = getpostexp

            # current hotness rating
            currenthotness = getpost.hotness_rating_now
            newhotness = currenthotness - 1
            getpost.hotness_rating_now = newhotness

            # add stats to voter
            exppoint(user_id=current_user.id, category=8)
            exppoint(user_id=getpost.user_id, category=4)

            # add to user stats
            current_downvotes_posts = post_owner_stats.post_downvotes
            new_downvotes_posts = current_downvotes_posts + 1
            post_owner_stats.post_downvotes = new_downvotes_posts

            # add user_id to vote
            create_new_vote = PostUpvotes(
                user_id=current_user.id,
                post_id=getpost.id,
            )

            newvotenumber = getpost.highest_exp_reached - 1

            # add and commit
            db.session.add(create_new_vote)
            db.session.add(getpost)
            db.session.add(post_owner_stats)
            db.session.commit()

            if seeifvoted is None:
                return jsonify({
                    'result': 'Downvoted!',
                    'thepostid': str_post_id,
                    'newnumber': newvotenumber
                })
            else:
                return jsonify({
                    'result': 'You already voted',
                    'thepostid': str_post_id,
                    'newnumber': getpost.hotness_rating_now
                })