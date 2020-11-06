from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp, \
    Optional

from app.common.validation import general


class UserPGPForm(FlaskForm):

    key = TextAreaField(validators=[
        Optional(),
        Length(200, 25000, message='Key is between 200 and 10000 characters long'),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class UserBioForm(FlaskForm):

    bio = TextAreaField(validators=[
        Optional(),
        Length(3, 5000, message='Bio is between 10 and 5000 characters long'),
        Regexp(general, message="No Special characters allowed"),
    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class MyAccountForm(FlaskForm):

    Bio = TextAreaField(validators=[
        Optional(),
        Length(3, 180, message='Profile is between 10 and 1000 characters long'),
        Regexp(general, message="No Special characters allowed"),
    ])
    Shortbio = StringField(validators=[
        DataRequired(),
        Length(3, 250),
        Regexp(general,
               message='Into is 3 to 250 characters long')
    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class SaveForm(FlaskForm):
    """
    The subscribe button on the side
    """
    save = SubmitField("Subscribe")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class DeleteSaveForm(FlaskForm):
    """
    The subscribe button on the side
    """
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class DeleteSaveAllForm(FlaskForm):
    """
    The subscribe button on the side
    """
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True


class UnblockForm(FlaskForm):
    """
    The subscribe button on the side
    """
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:
            return True