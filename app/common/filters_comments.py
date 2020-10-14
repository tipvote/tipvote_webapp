from app import app


@app.template_filter('subcommentsofcomment')
def subcommentsofcomment(commentid):
    """
    returns all subcomments of a comment in order of date posted...
    """
    from app.models import Comments
    from app import db

    getsubcomments = db.session.query(Comments)
    getsubcomments = getsubcomments.filter(Comments.comment_parent_id ==commentid)
    getsubcomments.all()
    for f in getsubcomments:
        yield f
