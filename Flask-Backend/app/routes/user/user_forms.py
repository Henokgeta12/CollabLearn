from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField,StringField,FileField
from wtforms.validators import InputRequired, Email,Length,EqualTo,ValidationError,Regexp,DataRequired
from flask_wtf.file import FileRequired,FileAllowed


class Update_Acc_Form(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required"), 
        Length(min=4, max=20, message="Username must be between 4 and 20 characters"),
        Regexp('^\w+$', message="Username must contain only letters, numbers, or underscores")
    ])
    
    email = EmailField('Email', validators=[
        InputRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = Users.query.filter_by(email=email.data.lower()).first() 
            if user:
                raise ValidationError('Email is already registered. Please use a different email address.')

class UpdateProfileForm(FlaskForm):
    profile_img = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),
    ])
    submit = SubmitField('Update')

class VerifyEmailForm(FlaskForm):
    submit = SubmitField('Verify Email')

class ConfirmPasswordForm(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')