# import necessary packages
from wtforms import Form, StringField, PasswordField, validators, SelectField
from wtforms.validators import ValidationError
from models import Admin

# define the login form model
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

# define create job form model
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

# define set alarm form model
class SetAlarmForm(Form):
    threshold_key = SelectField('Your threshold type', validators=[
        validators.DataRequired()
    ], choices=[
        ('humidity', 'Humidity'),
        ('temperature', 'Temperature'),
        ('pressure', 'Pressure')
    ])

    threshold_opt = SelectField('Your operation type', validators=[
        validators.DataRequired()
    ], choices=[
        ('<', 'Less than'),
        ('=', 'Equal to'),
        ('>', 'More than')
    ])

    threshold_val = StringField('Your threshold value', validators=[
        validators.DataRequired()
    ])

