from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import url_for, render_template, flash
from flask_migrate import Migrate
from flask_socketio import SocketIO
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import timedelta

import os 

load_dotenv()

serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
mail = Mail()

def send_verification_email(email):
    try:
        token = serializer.dumps(email, salt='email-verification-salt')
        link = url_for('user.verify_email', token=token, _external=True)
        msg = Message('Welcome Confirm Your Email', recipients=[email])
        msg.body = f"Hello,\n\nPlease confirm your email by clicking the link below:\n{link}\n\nIf you didn’t request this, please ignore this email."
        msg.html = render_template('email_template.html', link=link)
        mail.send(msg)
        flash('Verification email sent!', 'success')
    except Exception as e:
        print(f"Error sending email: {e}")  # Log the error for debugging
    
def verifyEmail(token):
    try:
        # Decode the token
        email = serializer.loads(token, salt='email-verification-salt',max_age=3600)
        return str(email)
    except Exception as e:
        if isinstance(e, SignatureExpired):
            return flash('Invalid or expired token','error')
        else :
            return flash('Invalid token','error')

def send_password_reset(email):
    try:
        token = serializer.dumps(email, salt='password-reset-salt')
        link = url_for('user.verfiy_token', token=token, _external=True)
        msg = Message('Password Reset Request ', recipients=[email])
        msg.body = f"Hello,\n\nPlease confirm your email to reset your password :\n{link}\n\nIf you didn’t request this, please ignore this email."
        msg.html = render_template('reset_email.html', link=link)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")  # Log the error for debugging

def token_verfiy(token):
    try:
        # Decode the token
        email = serializer.loads(token, salt='password-reset-salt',max_age=3600)
        return str(email)
    except Exception as e:
        if isinstance(e, SignatureExpired):
            return flash('Invalid or expired token','error')
        else :
            return flash('Invalid token','error')

def allowed_file(filename):
    """
    Checks if the given filename is allowed for upload.

    The allowed filetypes are .png, .jpg, .jpeg, and .gif.

    :param filename: The filename to check.
    :return: True if the file is allowed, False otherwise.
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 