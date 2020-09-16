from flask_wtf import FlaskForm
from wtforms import SubmitField


class FriendForm(FlaskForm):
    """
    The subscribe button on the side
    """
    follow = SubmitField("Subscribe")
    unfollow = SubmitField("Subscribe")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class DeleteFollowerForm(FlaskForm):
    """
    The subscribe button on the side
    """
    submit = SubmitField("")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True