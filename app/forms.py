from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, Regexp
from .models.user_models import Users  # Import your Users model to check for existing users

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required"), 
        Length(min=4, max=20, message="Username must be between 4 and 20 characters"),
        Regexp('^\w+$', message="Username must contain only letters, numbers, or underscores")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required"), 
        Length(min=6, message="Password must be at least 6 characters"),
        Regexp('^(?=.*)(?=.*[a-z])(?=.*[A-Z]).{6,}$', 
               message="Password must contain at least one uppercase letter, one lowercase letter, and one digit")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(message="Please confirm your password"), 
        EqualTo('password', message="Passwords must match")
    ])
    email = EmailField('Email', validators=[
        InputRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required")
    ], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
