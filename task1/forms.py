from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError
from models import Admin

# define the login form
class LoginForm(Form):
    username = StringField('username', validators=[
        validators.DataRequired()
    ])

    password = PasswordField('password', validators=[
        validators.DataRequired()
    ])

    def validate_username(form, field):
        username = field.data
        password = form.password.data
        if Admin.is_admin(username, password) is False:
            raise ValidationError('Username Or Password Is Invalid')

class CreateJobForm(Form):
    frequency = StringField('frequency', validators=[
        validators.DataRequired()
    ])

    command = StringField('command', validators=[
        validators.DataRequired()
    ])

    comment = StringField('comment', validators=[
        validators.DataRequired()
    ])


