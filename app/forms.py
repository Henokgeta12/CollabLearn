from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, TextAreaField, SelectField,HiddenField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, Regexp,DataRequired
from .models import Users  # Import your Users model to check for existing users

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
        user = Users.query.filter_by(email=email.data.lower()).first() 
        if user:
            raise ValidationError('Email is already registered. Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required")
    ], render_kw={'autofocus': True ,'autocomplete': 'off'})
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required")
    ],render_kw={'autocomplete': 'off'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

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

class JoinGroupForm(FlaskForm):
    group_identifier = StringField('Group Name or Referral Code', validators=[DataRequired()])
    submit = SubmitField('Join Group')


class CreateGroupForm(FlaskForm):
    group_name = StringField(
        "Group Name",
        validators=[
            DataRequired(message="Group Name is required."),
            Length(max=100, message="Group Name must be less than 100 characters.")
        ],
        render_kw={"class": "form-control", "id": "group-name", "required": True}
    )
    group_description = TextAreaField(
        "Group Description",
        render_kw={"class": "form-control", "id": "group-description"}
    )
    group_visibility = SelectField(
        "Group Visibility",
        choices=[
            ("", "Select Visibility"),  # Default disabled option
            ("public", "Public"),
            ("private", "Private")
        ],
        validators=[DataRequired(message="Group Visibility is required.")],
        render_kw={"class": "form-control", "id": "group-visibility"}
    )
    submit = SubmitField(
        "Create Group",
        render_kw={"class": "btn btn-primary"}
    )

class JoinGroupForm(FlaskForm):
    group_id = HiddenField('Group ID')
    referral_code = HiddenField('Referral Code')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class UploadResourceForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class TaskForm(FlaskForm):
    task_description = StringField('Task Description', validators=[DataRequired()])
    submit = SubmitField('Add Task')

class UpdateTaskStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    submit = SubmitField('Update Status')

class GroupNotesForm(FlaskForm):
    content = TextAreaField('Group Notes', validators=[DataRequired()])
    submit = SubmitField('Save Notes')

class JoinGroupForm(FlaskForm):
    group_id = HiddenField('Group ID', validators=[DataRequired()])
    referral_code = StringField('Referral Code', validators=[DataRequired()])
    submit = SubmitField('Join Group')
