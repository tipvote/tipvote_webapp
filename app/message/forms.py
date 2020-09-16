
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    TextAreaField, \
    RadioField, \
    BooleanField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp,\
    Optional


from app.common.validation import\
    subcommon_name, \
    onlynumbers, \
    user_names


# ------------------------------------------------------------------------------------
class MarkAsRead(FlaskForm):
    """
    Adds a mod to a subforum
    """

    submit = SubmitField()


class ReplyToMsg(FlaskForm):
    """
    Replys to a message
    """
    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 3000, message='Post message is between 1 and 3000 characters long.'),

    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class CreateAMsgUser(FlaskForm):
    """
    Replys to a message
    """

    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 3000, message='Post message is between 1 and 3000 characters long.'),

    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class CreateAMsg(FlaskForm):
    """
    Replys to a message
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 50, message='Names are between 3 and 25 characters long'),
        Regexp(user_names, message='Names must have only letters, numbers, dots or underscores')
    ])
    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 3000, message='Post message is between 1 and 3000 characters long.'),

    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False
