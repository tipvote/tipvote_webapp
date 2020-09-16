from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, \
    FileField



class SubscribeForm(FlaskForm):
    """
    The subscribe button on the side
    """
    subscribe = SubmitField("Subscribe")
    unsubscribe = SubmitField("Unsubscribe")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class ReportForm(FlaskForm):
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


class ReportCommentForm(FlaskForm):
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


# ----- Customize

class CreateBanner(FlaskForm):
    """
    Used for creating an image post
    """

    imagebanner = FileField('Primary Image',
                          validators=[FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                          message='Images only or wrong format.  Size must be not greater than 5mb.')
                                      ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class Description(FlaskForm):
    """
    Used for creating an image post
    """

    imagebanner = FileField('Primary Image',
                          validators=[FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                          message='Images only or wrong format.  Size must be not greater than 5mb.')
                                      ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True
