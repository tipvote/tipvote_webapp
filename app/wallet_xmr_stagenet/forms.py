from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length,  Regexp, Optional
from app.common.validation import btcamount, general, onlynumbers, monero


class WalletSendCoin(FlaskForm):
    sendto = TextAreaField(validators=[DataRequired(),
                                       Length(94, 106),
                                       Regexp(monero)
                                       ])

    description = StringField(validators=[Optional(),
                                          Length(2,100),
                                          Regexp(general)
                                          ])

    amount = StringField(validators=[DataRequired(),
                                     Length(1,20),
                                     Regexp(btcamount)
                                     ])
    pin = PasswordField(validators=[
        DataRequired(),
        Regexp(onlynumbers),
        Length(6, 6),
    ])
    submit = SubmitField('')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False
