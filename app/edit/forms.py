
from flask_wtf import FlaskForm
from wtforms import SubmitField, \
    TextAreaField, \
    FileField
from wtforms.validators import DataRequired, \
    Length, \
    Optional
from flask_wtf.file import FileAllowed



# ------------------------------------------------------------------------------------
class EditPostTextForm(FlaskForm):
    """
    Edit a post text
    """
    postmessage = TextAreaField(validators=[
        Optional(),
        Length(1, 3000, message='Post message is between 1 and 3000 characters long.'),

    ])

    image_one = FileField(validators=
                          [FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                       message='Images only or wrong format.  Size must be not greater than 5mb.')
                           ])
    submit = SubmitField()
    delete = SubmitField()
    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class EditCommentForm(FlaskForm):
    """
    Edit a comment
    """

    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 3000, message='Post message is between 1 and 3000 characters long.'),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class DeletePostTextForm(FlaskForm):
    """
    Delete post text
    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class DeleteCommentTextForm(FlaskForm):
    """
    Delete post text
    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False