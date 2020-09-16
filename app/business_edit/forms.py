from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    TextAreaField, \
    FileField, BooleanField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp, \
    Optional

from app.common.validation import user_names, general, urllink, phonenumber, allowspace
from flask_wtf.file import FileAllowed
from wtforms.fields.html5 import EmailField


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


class AcceptsCurrency(FlaskForm):
    """
    Used for creating an image post
    """

    accepts_btc = BooleanField(default=False)
    accepts_bch = BooleanField(default=False)
    accepts_xmr = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class DeleteRoomForm(FlaskForm):
    """
    Deletes the sub
    """

    page_name = StringField(validators=[
        DataRequired(),
        Length(3, 50, message='Names are between 3 and 25 characters long'),
        Regexp(user_names, message='Names must have only letters, numbers, dots or underscores')
    ])
    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class ProfilePicForm(FlaskForm):

    imageprofile = FileField(validators=[Optional(),
                                         FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                                     'Images only')
                                         ])

    submit = SubmitField()
    delete = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class BannerPicForm(FlaskForm):

    imageprofile = FileField(validators=[Optional(),
                                         FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                                     'Images only')
                                         ])

    submit = SubmitField()
    delete = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class MyAccountForm(FlaskForm):
    business_name = StringField(validators=[
        Optional(),
        Length(3, 150, message='Business name is between 3 and 150 characters long'),

    ])
    about = TextAreaField(validators=[
        Optional(),
        Length(3, 180, message='Profile is between 10 and 1000 characters long'),

    ])
    email = EmailField(validators=[
        Optional(),
        Length(3, 350),

    ])
    phone = StringField(validators=[
        Optional(),
        Length(3, 50),

    ])

    website = StringField(validators=[
        Optional(),
        Length(3, 1000),


    ])
    facebook = StringField(validators=[
        Optional(),
        Length(3, 1000),


    ])
    twitter = StringField(validators=[
        Optional(),
        Length(3, 1000),


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


class MyLocationForm(FlaskForm):

    theaddress = StringField(validators=[
        Optional(),
        Length(1, 250, message='Profile is between 10 and 1000 characters long'),


    ])
    thetown = StringField(validators=[
        Optional(),
        Length(1, 250),


    ])
    thestate = StringField(validators=[
        Optional(),
        Length(1, 250),


    ])
    thecountry = StringField(validators=[
        Optional(),
        Length(1, 250),


    ])
    thezipcode = StringField(validators=[
        Optional(),
        Length(3, 25),


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
