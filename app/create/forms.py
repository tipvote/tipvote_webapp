
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, \
    SubmitField, \
    TextAreaField, \
    RadioField, \
    FileField, \
    BooleanField, SelectField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp, \
    Optional
from app.common.validation import subcommon_name, general

from app.classes.business import Business
from app.classes.subforum import SubForums
from flask import flash
from sqlalchemy import func


class CreateBusinessForm(FlaskForm):
    """
    Creates a subcommon
    """
    business_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='Name of the room is between 3 and 25 characters long'),
        Regexp(subcommon_name,
               message='Room names must have only letters or numbers.  No special characters or spaces')
    ])

    type_of_business = RadioField(DataRequired(),
                                  choices=[('0', 'Local Business'),
                                           ('1', 'Company, Organization, or Institution'),
                                           ('2', 'Brand or Product'),
                                           ('3', 'Crypto Trader'),

                                           ]
                                  )

    age = BooleanField(default=False)

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        bad_names = ['delete', 'admin', 'bitcoin', 'bitcoincash', 'tipvote', 'username', 'user_name', 'room',
                     'business', 'tipvote_bot', 'all', 'rooms', 'people', 'followers', 'monero', 'btc', 'btccash'
                     ]

        rv = FlaskForm.validate(self)

        if rv is True:
            if self.business_name.data.lower() in bad_names:
                flash('Name is not allowed.', category="danger")
                return False

            biz_name = Business.query.filter(func.lower(Business.business_name) == func.lower(self.business_name.data)).first()

            if biz_name:
                flash('Name is already taken.', category="danger")
                return False

            else:
                return True


class CreateShareTextForm(FlaskForm):
    """
    Edit a post text
    """
    postmessage = TextAreaField(validators=[
        Optional(),
        Length(1, 10000, message='Post message is between 1 and 10000 characters long.'),
        Regexp(general,
               message='M have only letters or numbers.  No special characters or spaces')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class CreateSubcommonForm(FlaskForm):
    """
    Creates a subcommon
    """
    subcommonname = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='Name of the room is between 3 and 25 characters long'),
        Regexp(subcommon_name,
               message='Room names must have only letters or numbers.  No special characters or spaces')
    ])
    subcommondescription = TextAreaField(validators=[
        DataRequired(),
        Length(10, 500, message='Room description is between 10 and 500 characters long'),


    ])

    typeofsub = RadioField(DataRequired(),
                           choices=[('0', 'Public'), ('1', 'Private'), ('2', 'Censored')])
    age = BooleanField(default=False)

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        bad_names = ['delete', 'admin', 'bitcoin', 'bitcoincash', 'tipvote', 'username', 'user_name', 'room',
                     'business', 'tipvote_bot', 'all', 'rooms', 'people', 'followers', 'monero', 'btc', 'btccash'
                     ]

        rv = FlaskForm.validate(self)

        if rv is True:
            if self.subcommonname.data.lower() in bad_names:
                flash('Name is not allowed.', category="danger")
                return False

            biz_name = SubForums.query.filter(func.lower(SubForums.subcommon_name) == func.lower(self.subcommonname.data)).first()

            if biz_name:
                flash('Name is already taken.', category="danger")
                return False

            else:
                return True


class CreateCommentForm(FlaskForm):
    """
    Used for creating a reply to a post
    """

    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 10000, message='Comments are between 1 and 10000 characters long'),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class CreateCommentQuickForm(FlaskForm):
    """
    Used for creating a reply to a post
    """

    postmessage = TextAreaField(validators=[
        DataRequired(),
        Length(1, 5000, message='Comments are between 1 and 1000 characters long'),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class RoomPostForm(FlaskForm):
    """
    Used for creating an image post
    """

    post_title = StringField(validators=[
        DataRequired(),
        Length(1, 150, message='Title must be between 1 and 150 characters long'),
    ])

    post_message = TextAreaField(validators=[
        Optional(),
        Length(1, 10000, message='Text must be between 1 and 10000 characters long'),
    ])

    image_one = FileField(validators=
                          [FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                       message='Images only or wrong format.  Size must be not greater than 5mb.')
                           ])
    age = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class BusinessPostForm(FlaskForm):
    """
    Used for creating an image post
    """

    post_message = TextAreaField(validators=[
        Optional(),
        Length(1, 10000, message='Text must be between 1 and 10000 characters long'),
    ])

    image_one = FileField(validators=
                          [FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                       message='Images only or wrong format.  Size must be not greater than 5mb.')
                           ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


class MainPostForm(FlaskForm):
    """
    Used for creating an image post
    """

    roomname = SelectField(Optional())

    post_title = StringField(validators=[
        DataRequired(),
        Length(1, 150, message='Title must be between 1 and 150 characters long'),
    ])

    post_message = TextAreaField(validators=[
        Optional(),
        Length(1, 10000, message='Text must be between 1 and 10000 characters long'),
    ])

    image_one = FileField(validators=
                          [FileAllowed(['jpg', 'png', 'gif', 'png', 'jpeg', 'webp'],
                                       message='Images only or wrong format.  Size must be not greater than 5mb.')
                           ])
    age = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv is True:

            return True


