import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, Regexp
from flask_wtf.file import FileField, FileAllowed
from app.forms import forms  # Adjust the import according to your project structure
from app.models import Users  # Adjust the import according to your project structure

class TestForms(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.db = SQLAlchemy(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()

    def test_registration_form_valid(self):
        form = forms.RegistrationForm(username='testuser', password='Password1', confirm_password='Password1', email='test@example.com')
        self.assertTrue(form.validate())

    def test_registration_form_invalid_username(self):
        form = forms.RegistrationForm(username='inv', password='Password1', confirm_password='Password1', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Username must be between 4 and 20 characters', form.username.errors)

    def test_registration_form_invalid_password(self):
        form = forms.RegistrationForm(username='testuser', password='pass', confirm_password='pass', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Password must be at least 6 characters', form.password.errors)

    def test_registration_form_passwords_do_not_match(self):
        form = forms.RegistrationForm(username='testuser', password='Password1', confirm_password='Password2', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Passwords must match', form.confirm_password.errors)

    def test_registration_form_invalid_email(self):
        form = forms.RegistrationForm(username='testuser', password='Password1', confirm_password='Password1', email='invalid-email')
        self.assertFalse(form.validate())
        self.assertIn('Please enter a valid email address', form.email.errors)

    def test_registration_form_username_already_taken(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        self.db.session.add(user)
        self.db.session.commit()
        form = forms.RegistrationForm(username='testuser', password='Password1', confirm_password='Password1', email='test2@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Username is already taken. Please choose a different one.', form.username.errors)

    def test_registration_form_email_already_registered(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        self.db.session.add(user)
        self.db.session.commit()
        form = forms.RegistrationForm(username='testuser2', password='Password1', confirm_password='Password1', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Email is already registered. Please use a different email address.', form.email.errors)

    def test_login_form_valid(self):
        form = forms.LoginForm(username='testuser', password='Password1')
        self.assertTrue(form.validate())

    def test_login_form_invalid_username(self):
        form = forms.LoginForm(username='', password='Password1')
        self.assertFalse(form.validate())
        self.assertIn('Username is required', form.username.errors)

    def test_login_form_invalid_password(self):
        form = forms.LoginForm(username='testuser', password='')
        self.assertFalse(form.validate())
        self.assertIn('Password is required', form.password.errors)

    def test_update_acc_form_valid(self):
        form = forms.Update_Acc_Form(username='testuser', email='test@example.com')
        self.assertTrue(form.validate())

    def test_update_acc_form_invalid_username(self):
        form = forms.Update_Acc_Form(username='inv', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Username must be between 4 and 20 characters', form.username.errors)

    def test_update_acc_form_invalid_email(self):
        form = forms.Update_Acc_Form(username='testuser', email='invalid-email')
        self.assertFalse(form.validate())
        self.assertIn('Please enter a valid email address', form.email.errors)

    def test_update_acc_form_username_already_taken(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        self.db.session.add(user)
        self.db.session.commit()
        form = forms.Update_Acc_Form(username='testuser', email='test2@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Username is already taken. Please choose a different one.', form.username.errors)

    def test_update_acc_form_email_already_registered(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        self.db.session.add(user)
        self.db.session.commit()
        form = forms.Update_Acc_Form(username='testuser2', email='test@example.com')
        self.assertFalse(form.validate())
        self.assertIn('Email is already registered. Please use a different email address.', form.email.errors)

    def test_update_profile_form_valid(self):
        form = forms.UpdateProfileForm(profile_img='test.jpg')
        self.assertTrue(form.validate())

    def test_update_profile_form_invalid_file_type(self):
        form = forms.UpdateProfileForm(profile_img='test.pdf')
        self.assertFalse(form.validate())
        self.assertIn('Images only!', form.profile_img.errors)

if __name__ == '__main__':
    unittest.main()
