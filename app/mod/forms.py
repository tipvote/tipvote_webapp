
from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    TextAreaField, \
    RadioField, \
    BooleanField, FileField
from wtforms.validators import DataRequired, \
    Length, \
    Regexp,\
    Optional
from flask_wtf.file import FileAllowed
from app.common.validation import\
    subcommon_name, \
    onlynumbers, \
    user_names


class DeleteRoomForm(FlaskForm):
    """
    Deletes the sub
    """

    sub_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])
    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False

# ------------------------------------------------------------------------------------
class AddModForm(FlaskForm):
    """
    Adds a mod to a subforum
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class RemoveModForm(FlaskForm):
    """
    Removes a mod from a subforum
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# ------------------------------------------------------------------------------------
class BanUserModForm(FlaskForm):
    """
    Bans a user from a subforum
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class UnBanUserModForm(FlaskForm):
    """
    Unban a user from a subforum
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# -----------------------------------------------------
class InviteUserForm(FlaskForm):
    """
    Invites a user from a form
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# -----------------------------------------------------
class NSFWForm(FlaskForm):
    """
    Marks a post as NSFW
    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False

class RemoveUserForm(FlaskForm):
    """
    Removes a user from a sub
    """
    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 25, message='user_names are between 3 and 25 characters long'),
        Regexp(user_names, message='user_names must have only letters, numbers, dots or underscores')
    ])

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# -----------------------------------------------------
class ChangeSubInfo(FlaskForm):
    """
    Update subs basic info
    """
    subcommondescription = TextAreaField(validators=[
        DataRequired(),
        Length(1, 500, message='Description is between 1 and 500 characters long'),
        Regexp(subcommon_name, message='Descriptions must have only letters, numbers, or underscores')
    ])
    typeofsub = RadioField('Label', choices=[('0', 'Public'),
                                             ('1', 'Private'),
                                             ('2', 'Censored')])
    age = BooleanField(default=False)
    exprequiredtopost = StringField(validators=[
        Optional(),
        Regexp(onlynumbers, message='Numbers only'),
        Length(1, 100, message='Level required is between 1 and 100'),
    ])
    allowtextposts = BooleanField(default=True)
    allowurlposts = BooleanField(default=True)
    allowimageposts = BooleanField(default=True)

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# -----------------------------------------------------
class ChangeSubInfoBoxOne(FlaskForm):
    """
    Update subs basic info
    """
    description = TextAreaField(validators=[
        DataRequired(),
        Length(1, 25000, message='Description is between 1 and 25000 characters long'),

    ])

    enabled = BooleanField(default=False)


    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# ---------------------------------------------------------------------------------------
class QuickLock(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class QuickDelete(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class QuickBanDelete(FlaskForm):
    """

    """
    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class QuickMute(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class UnReport(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# ---------------------------------------------------------------------------------------
class AcceptUserForm(FlaskForm):
    """
    Adds a private user to a private sub
    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class AcceptSpecificUserForm(FlaskForm):
    """
    Adds a private user to a private sub
    """

    user_name = StringField(validators=[
        DataRequired(),
        Length(3, 40),
        Regexp(user_names,
               message='user_names must have only letters, numbers, dots or underscores')
    ])
    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


# ---------------------------------------------------------------------------------------
class SubCustomForm(FlaskForm):

    subbannerimage = FileField(validators=[Optional(),
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


class SubCustomThumbnailForm(FlaskForm):

    subthumbnailimage = FileField(validators=[Optional(),
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


class StickyPostForm(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False


class UnStickyPostForm(FlaskForm):
    """

    """

    submit = SubmitField()

    def validate(self):

        rv = FlaskForm.validate(self)
        if rv:
            return True
        else:
            return False