
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
class ApplyToPrivate(FlaskForm):
    """
    Apply to a private forum
    """
    reasonforapplying = TextAreaField(validators=[
        DataRequired(),
        Length(1, 500, message='Message length is between 1 and 500 characters long'),
        Regexp(subcommon_name,
               message='Words must have only letters, numbers,'
                       ' or underscores')
    ])
    submit = SubmitField()


class CreateUpdateForm(FlaskForm):
    """
    Form for adding an update.  Usuable by admin only
    """
    title = StringField()
    version = StringField()
    description = TextAreaField()
    giturl = TextAreaField()

    submit = SubmitField()

