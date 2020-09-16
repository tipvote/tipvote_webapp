from flask_wtf import\
    FlaskForm
from wtforms import\
    StringField,\
    PasswordField,\
    SubmitField
from wtforms.validators import\
    DataRequired,\
    Length,\
    Regexp,\
    Optional
from app.common.validation import\
    btcamount,\
    general,\
    onlynumbers, bitcoin


class WalletSendcoin(FlaskForm):
    sendto = StringField(validators=[DataRequired(),
                                     Length(24, 44,
                                            message='BCH address length is incorrect'),
                                     Regexp(bitcoin,
                                            message='BCH address is incorrect format')
                                     ])

    description = StringField(validators=[Optional(),
                                          Length(2, 100,
                                                 message='Description length is between 1 and 11 characters long'),
                                          Regexp(general,
                                                 message='Description length must have no special characters')
                                          ])

    amount = StringField(validators=[DataRequired(),
                                     Length(1, 11,
                                            message='BCH Amount is between 1 and 11 characters long'),
                                     Regexp(btcamount,
                                            message='BCH Amount Incorrect bitcoin amount')
                                     ])
    pin = PasswordField(validators=[
        DataRequired(),
        Regexp(onlynumbers),
        Length(6, 6),
    ])

    submit = SubmitField('')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self, *args, **kwargs):

        rv = FlaskForm.validate(self)

        if rv:
            return True
        else:
            return False
