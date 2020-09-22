# flask imports
from flask import \
    redirect, \
    url_for, \
    flash, \
    request, \
    jsonify

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


@vote.route('/comment_vote/<string:subname>/<int:votetype>/<int:postid>/<int:commentid>', methods=['POST'])
@login_required
def comment_vote(votetype, postid, commentid, subname):
    """
    # comment - down/up vote
    # votetype = type of voted
    # postid = the id of the main post
    # commentid = id of comment
    """
    if request.method == 'POST':
        getcomment = db.session.query(Comments).filter_by(id=commentid).first_or_404()
        post = db.session.query(CommonsPost).filter_by(id=postid).first()

        if post is None:
            flash("The post has been removed or doesnt exist", category='danger')
            return redirect((request.args.get('next', request.referrer)))
        if getcomment is None:
            flash("Comment doesnt exist or has been removed", category='danger')
            return redirect((request.args.get('next', request.referrer)))
        if post.hidden == 1:
            flash("Post Has been deleted", category='danger')
            return redirect((request.args.get('next', request.referrer)))
        if post.locked == 1:
            flash("Post Has been locked", category='danger')
            return redirect((request.args.get('next', request.referrer)))
        if getcomment.user_id != current_user.id:
            seeifvoted = db.session.query(CommentsUpvotes).filter(CommentsUpvotes.user_id == current_user.id,
                                                                  CommentsUpvotes.comment_id == getcomment.id).first()
            if seeifvoted is None:
                # get comment user stats
                comment_owner_stats = db.session.query(UserStats).filter(UserStats.user_id == getcomment.user_id).first()
                # Query the sub
                # see if this sub exists
                try:
                    getcurrentsub = db.session.query(SubForums).filter(SubForums.subcommon_name == subname).first()
                    if getcurrentsub is None:
                        return redirect((request.args.get('next', request.referrer)))
                except Exception:
                    flash("Sub Doesnt Exist.", category="danger")
                    return redirect((request.args.get('next', request.referrer)))

                subid = getcurrentsub.id
                subtype = getcurrentsub.type_of_subcommon

                # see if banned or if private
                seeifbanned = db.session.query(Banned).filter(current_user.id == Banned.user_id,
                                                              Banned.subcommon_id == subid).first()
                # if user on banned list turn him away
                if seeifbanned is not None:
                    flash("You were banned from this sub.", category="success")
                    return redirect(url_for('banned', subname=subname))
                # if sub is private
                if subtype == 1:
                    seeifuserinvited = db.session.query(PrivateMembers).filter(current_user.id == PrivateMembers.user_id,
                                                                               PrivateMembers.subcommon_id == subid).first()
                    # if user is not on the list turn him away
                    if seeifuserinvited is None:
                        flash("Sub Is a private Community.", category="success")
                        return redirect(url_for('private', subname=subname))

                currentupvotes = getcomment.upvotes_on_comment
                currentdownvotes = getcomment.downvotes_on_comment

                # voted up
                if votetype == 1:
                    # add the vote to current votes
                    newvotes_up = currentupvotes + 1
                    # set post variable to this new post number
                    getcomment.upvotes_on_comment = newvotes_up
                    # add  downvotes
                    newvotes_down = getcomment.downvotes_on_comment
                    getcommentexp = newvotes_up + newvotes_down
                    # set exp number to exp_commonts
                    getcomment.total_exp_commons = getcommentexp
                    # add and commit
                    db.session.add(getcomment)

                    # add to user stats
                    current_upvotes_comment = comment_owner_stats.comment_upvotes
                    new_upvotes_comment = current_upvotes_comment + 1
                    comment_owner_stats.comment_upvotes = new_upvotes_comment

                    if getcomment.comment_parent_id is None:
                        # get comments of this comment and raise
                        # there thread upvotes for sorting purposes
                        getrelativecomments = db.session.query(Comments)\
                            .filter(Comments.path.like(getcomment.path + '%'))
                        for comment in getrelativecomments:
                            comment.thread_upvotes = newvotes_up

                            db.session.add(comment)
                        getcomment.thread_upvotes = newvotes_up
                        db.session.add(getcomment)

                    # add exp points
                    exppoint(user_id=current_user.id, type=8)
                    exppoint(user_id=getcomment.user_id, type=3)

                    # commit
                    db.session.add(comment_owner_stats)
                    flash("Upvoted", category='success')

                # voted down
                elif votetype == 2:
                    # add the vote to current votes
                    newvotes_down = currentdownvotes - 1
                    # set post variable to this new post number
                    getcomment.downvotes_on_comment = newvotes_down
                    # subtract from downvotes
                    newvotes_up = getcomment.upvotes_on_comment
                    getcommentexp = newvotes_up + newvotes_down
                    # set exp number to exp_commons
                    getcomment.total_exp_commons = getcommentexp
                    # add and commit
                    db.session.add(getcomment)

                    # add to user stats
                    current_downvotes_comment = comment_owner_stats.comment_downvotes
                    new_downvotes_comment = current_downvotes_comment + 1
                    comment_owner_stats.comment_downvotes = new_downvotes_comment

                    # raise all in path for thread votes down
                    if getcomment.comment_parent_id is None:
                        # get comments of this comment and raise there thread downvotes for sorting purposes
                        getrelativecomments = db.session.query(Comments).filter(Comments.path.like(getcomment.path + '%'))
                        for comment in getrelativecomments:
                            comment.thread_downvotes = newvotes_down

                            db.session.add(comment)
                        getcomment.thread_downvotes = newvotes_down
                        db.session.add(getcomment)

                    # add exp points
                    exppoint(user_id=current_user.id, type=8)
                    exppoint(user_id=getcomment.user_id, type=4)

                    db.session.add(comment_owner_stats)

                    flash("Downvoted", category='danger')
                else:
                    flash("Vote was incorrect", category='danger')
                    return redirect((request.args.get('next', request.referrer)))

                # add user_id to vote so user doesnt double vote
                create_new_vote = CommentsUpvotes(
                    user_id=current_user.id,
                    comment_id=getcomment.id,
                )
                # update post to active
                # see if post is old/cannot commit
                db.session.add(create_new_vote)
                db.session.commit()

                return redirect((request.args.get('next', request.referrer)))
            else:
                flash("Already voted", category='danger')
                return redirect((request.args.get('next', request.referrer)))
        else:
            flash("You can not vote on your own comments", category='danger')
            return redirect((request.args.get('next', request.referrer)))


@vote.route('/upvotepost/<int:postid>', methods=['POST'])
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

        seeifbanned = db.session.query(Banned)\
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == subid)\
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

            # add exp points
            exppoint(user_id=current_user.id, type=8)
            exppoint(user_id=getpost.user_id, type=3)
            # add to user stats

            post_owner_stats = db.session.query(UserStats)\
                .filter(UserStats.user_id == getpost.user_id)\
                .first()
            current_upvotes_posts = post_owner_stats.post_upvotes
            new_upvotes_posts = current_upvotes_posts + 1
            post_owner_stats.post_upvotes = new_upvotes_posts

            create_new_vote = PostUpvotes(
                user_id=current_user.id,
                post_id=getpost.id,
            )

            postrating = getpost.highest_exp_reached + 1

            # add and commit
            db.session.add(create_new_vote)
            db.session.add(getpost)
            db.session.add(post_owner_stats)
            db.session.commit()

            return jsonify({
                'result': 'Upvoted!',
                'thepostid': str_post_id,
                'newnumber': postrating
            })


@vote.route('/downvotepost/<int:postid>', methods=['POST'])
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

        seeifbanned = db.session.query(Banned)\
            .filter(current_user.id == Banned.user_id,
                    Banned.subcommon_id == subid)\
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
            exppoint(user_id=current_user.id, type=8)
            exppoint(user_id=getpost.user_id, type=4)

            # add to user stats
            post_owner_stats = db.session.query(UserStats)\
                .filter(UserStats.user_id == getpost.user_id)\
                .first()

            current_downvotes_posts = post_owner_stats.post_downvotes
            new_downvotes_posts = current_downvotes_posts + 1
            post_owner_stats.post_downvotes = new_downvotes_posts

            # add user_id to vote
            create_new_vote = PostUpvotes(
                user_id=current_user.id,
                post_id=getpost.id,
            )

            postrating = getpost.highest_exp_reached - 1

            # add and commit
            db.session.add(create_new_vote)
            db.session.add(getpost)
            db.session.add(post_owner_stats)
            db.session.commit()

            return jsonify({
                'result': 'Downvoted!',
                'thepostid': str_post_id,
                'newnumber': postrating
            })