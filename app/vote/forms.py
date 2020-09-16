from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length,  Regexp, Optional
from app.common.validation import btcamount, general, onlynumbers, bitcoin


class VoteForm(FlaskForm):

    submit = SubmitField('')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False
