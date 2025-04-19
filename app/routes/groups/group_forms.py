from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, FileField,HiddenField ,EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp,InputRequired
from flask_wtf.file import FileField, FileAllowed

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

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
    
class UpdateProfileForm(FlaskForm):
    profile_img = FileField('Profile Image', validators=[
    FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),
    ])
    submit = SubmitField('Update')

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

class VerifyEmailForm(FlaskForm):
    submit = SubmitField('Verify Email')

# ##
# class UpdateProfileForm(FlaskForm):
#     profile_img = FileField('Profile Image', validators=[
#         FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),
#     ])
#     submit = SubmitField('Update')
#     def validate_profile_img(self, field):
#         if not allowed_file(field.data.filename):
#             raise ValidationError('Allowed image types are jpg, jpeg, png, gif')

# ##