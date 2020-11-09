from flask_wtf import FlaskForm
from wtforms import StringField, \
    PasswordField, \
    SubmitField, \
    BooleanField, \
    RadioField, \
    SelectField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp, \
    EqualTo, \
    Optional
from app.models import User
from flask import flash
from sqlalchemy import func
from app.common.validation import user_names, general, onlynumbers
from wtforms.fields.html5 import EmailField


class DeleteAllForm(FlaskForm):
    """
    Deletes the sub
    """
    user_name = StringField(validators=[
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


class DeleteUserForm(FlaskForm):
    """
    Deletes the sub
    """

    user_name = StringField(validators=[
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


class LoginForm(FlaskForm):
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 18),
        Regexp(user_names,
               message='user_names must have only letters, numbers, dots or underscores')
    ])
    password_hash = PasswordField(validators=[
        DataRequired(),
        Length(7, 124),
        Regexp(general),
    ])
    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class RegistrationForm(FlaskForm):
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 18, message='user_names must be between 3 and 18 characters long'),
        Regexp(user_names,message='user_names must have only letters, numbers, dots or underscores')
    ])

    password = PasswordField(validators=[
        DataRequired(),
        Length(6, 128, message='Password must be between 7 and 128 characters long'),
        Regexp(general, message='Password must not have special characters or spaces'),
        EqualTo('passwordtwo',
                message='Passwords must match.')
    ])
    passwordtwo = PasswordField(validators=[
        DataRequired(),
        Regexp(general, message='Password must not have special characters or spaces'),
    ])
    email = EmailField('Email address', [DataRequired()])
    agreetotos = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        bad_usernames = ['delete', 'admin', 'bitcoin', 'bitcoincash', 'tipvote', 'username', 'user_name', 'room',
                         'business', 'tipvote_bot', 'all', 'rooms', 'people', 'followers', 'monero', 'btc', 'btccash',
                         'null', 'query', 'session'
                         ]

        rv = FlaskForm.validate(self)

        if rv is True:
            if self.user_name.data.lower() in bad_usernames:
                flash('User name is not allowed.', category="danger")
                return False

            user_name = User.query.filter(func.lower(User.user_name) == func.lower(self.user_name.data)).first()
            email = User.query.filter(func.lower(User.email) == func.lower(self.email.data)).first()

            if user_name:
                flash('User name is already taken.', category="danger")
                return False
            elif email:
                flash('Email has been used already for another user.', category="danger")
                return False
            else:
                return True


class ChangePinForm(FlaskForm):
    currentpin = PasswordField('', validators=[
        DataRequired(),
        Length(6, 6, message='Pin must be only numbers.  6 digits long'),
        Regexp(onlynumbers, message='Pin must be only numbers.  6 digits long'),

    ])
    newpin1 = PasswordField('', validators=[
        DataRequired(),
        Length(6, 6, message='Pin must be only numbers.  6 digits long'),
        Regexp(onlynumbers, message='Pin must be only numbers.  6 digits long'),
        EqualTo('newpin2',
                message='Pins must match. Pin is 6 digits long')
    ])
    newpin2 = PasswordField('', validators=[
        DataRequired(),
        Regexp(onlynumbers, message='Pin must be only numbers.  6 digits long'),
    ])

    submit = SubmitField('Update Pin')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class NewPinForm(FlaskForm):

    newpin1 = PasswordField('', validators=[
        DataRequired(),
        Length(6, 6, message='Pin must be only numbers.  6 digits long'),
        Regexp(onlynumbers, message='Pin must be only numbers.  6 digits long'),
        EqualTo('newpin2',
                message='Pins must match. Pin is 6 digits long')
    ])
    newpin2 = PasswordField('', validators=[
        DataRequired(),
        Regexp(onlynumbers, message='Pin must be only numbers.  6 digits long'),
    ])

    submit = SubmitField('Update Pin')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class ChangePasswordForm(FlaskForm):
    currentpassword = PasswordField('', validators=[
        DataRequired(),
        Regexp(general, message='Password must not have special characters or spaces'),
        Length(7, 124, message='Password must be between 7 and 124 characters long')
    ])
    newpassword = PasswordField('', validators=[
        DataRequired(),
        Regexp(general, message='Password must not have special characters or spaces'),
        Length(7, 124, message='Password must be between 7 and 124 characters long'),
        EqualTo('newpasswordtwo',
                message='Passwords must match')
    ])
    newpasswordtwo = PasswordField('', validators=[
        DataRequired(),
        Regexp(general, message='Password must not have special characters or spaces'),
    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv is True:
            return True
        else:
            return False


class AnonForm(FlaskForm):

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
    age = BooleanField(default=False)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class LostPassword(FlaskForm):
    username = StringField(validators=[
        DataRequired(),
        Length(3, 64),
        Regexp(general,
               message='Usernames must have only letters, numbers, dots or underscores')])
    email = StringField(validators=[
        DataRequired(),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False


class ChangeEmailForm(FlaskForm):

    newemail = StringField(validators=[
        DataRequired(),

    ])
    accountpassword = PasswordField('password', validators=[
        DataRequired(),
        Length(7, 64),
        Regexp(general),

    ])
    accountpin = PasswordField('pin', validators=[
        DataRequired(),
        Length(6,6),
        Regexp(general),

    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False


class ResendConfirmationForm(FlaskForm):
    username = StringField(validators=[
        DataRequired(),
        Length(3, 64),
        Regexp(general,
               message='Usernames must have only letters, numbers, dots or underscores')])
    email = StringField(validators=[
        DataRequired(),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False


class LostPinSendEmail(FlaskForm):
    username = StringField(validators=[
        DataRequired(),
        Length(3, 64),
        Regexp(general,
               message='Usernames must have only letters, numbers, dots or underscores')])
    email = StringField(validators=[
        DataRequired(),

    ])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False


class LostPinForm(FlaskForm):

    pin = PasswordField('New Four Digit Pin', validators=[
        DataRequired(),
        Length(6, 6),
        Regexp(onlynumbers),
        EqualTo('pintwo',
                message='Passwords must match. Pin  is 4 digits long')
    ])
    pintwo = PasswordField('Confirm new pin', validators=[
        DataRequired(),
        Regexp(onlynumbers),
    ])

    submit = SubmitField('Update Pin')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)


class PasswordFormReset(FlaskForm):
    newpassword = PasswordField('New password', validators=[
        DataRequired(),
        Length(7, 64),
        Regexp(general),
        EqualTo('newpasswordtwo',
                message='Passwords must match')
    ])
    newpasswordtwo = PasswordField('Confirm new password', validators=[
        DataRequired(),
        Length(7, 64),
        Regexp(general),
    ])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False


class ThemeForm(FlaskForm):
    theme_one = RadioField(validators=[Optional()],
                           choices=[('1', 'Black'),
                                    ('2', 'Blue'),
                                    ('3', 'Gray'),
                                    ('4', 'Light'),

                                    ]
                           )

    submit = SubmitField('Submit')


