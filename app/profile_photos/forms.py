from flask_wtf import FlaskForm
from wtforms import SubmitField, \
    FileField
from wtforms.validators import Optional

from flask_wtf.file import FileAllowed


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