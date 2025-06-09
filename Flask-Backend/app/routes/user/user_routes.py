from flask import render_template, request, redirect, url_for, flash, Blueprint
from app.models.user_models import Users,db
from werkzeug.utils import secure_filename
from .user_forms import UpdateProfileForm, Update_Acc_Form, VerifyEmailForm, ConfirmPasswordForm, ResetPasswordForm,  RequestResetForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from flask import current_app
from app.extensions import send_verification_email,verifyEmail,token_verfiy,send_password_reset,allowed_file

user_bp = Blueprint('user', __name__)

@user_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
        Allows users to update their profile picture and account information.

        GET:
            Displays the current user's profile picture and account information.

        POST:
            Updates the current user's profile picture and/or account information if the
            submitted form is valid.
    """
    img_file = url_for('static', filename='user_profile-pic/' + current_user.profile_img)
    profile_form = UpdateProfileForm()
    account_form = Update_Acc_Form()
    verify_form = VerifyEmailForm()
        
    if request.method == 'GET':
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email

    if request.method == 'POST' and profile_form.validate_on_submit():
        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                current_user.update_profile_img(unique_filename)
                db.session.commit()
                flash('Profile image updated successfully!', 'success')
                return redirect(url_for('user.account'))
            else:
                flash('Invalid file type. Please upload a valid image file.', 'error')
        else:
            flash('No file selected. Please select a file to upload.', 'error')

    return render_template('account.html', img_file=img_file, profile_form=profile_form, account_form=account_form,verify_form = verify_form,verified=current_user.is_verified)

@user_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """
        Updates the current user's profile information if the submitted form is valid.

        GET:
            Displays the current user's profile information in the account form.

        POST:
            Updates the current user's profile information if the submitted form is valid.
    """
    img_file = url_for('static', filename='user_profile-pic/' + current_user.profile_img)

    account_form = Update_Acc_Form()
    profile_form = UpdateProfileForm()
    verify_form = VerifyEmailForm()
        
    if request.method == 'GET':
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email

    if request.method == 'POST' and account_form.validate_on_submit():
        if account_form.email.data != current_user.email:
            email = account_form.email.data
            send_verification_email(email)
            flash('A verification email has been sent to your new email address.', 'info')
            return redirect(url_for('confirm_email_change', new_email=email))
        elif account_form.username.data != current_user.username:
            new_username = Users.query.filter_by(username=account_form.username.data).first()
            if new_username:
                flash('Username is already taken. Please choose a different one.', 'danger')
                return redirect(url_for('update_profile'))
            else:
                current_user.username = account_form.username.data 
                flash('Account information updated successfully!', 'success')
            return redirect(url_for('update_profile'))
        else:
            flash('No changes were made to your profile.','info')
            return redirect(url_for('update_profile'))

    return render_template('account.html',img_file = img_file,verified=current_user.is_verified, account_form=account_form, profile_form = profile_form ,verify_form = verify_form)

@user_bp.route('/send-verification', methods=['POST'])
@login_required
def send_verification():
    """
        Sends a verification email to the current user's email address if it is not already verified.

        POST:
            - Checks if the user's email exists. If not, flashes an error message and redirects to the account page.
            - If the user's email is already verified, flashes a success message and redirects to the account page.
            - Sends a verification email to the user's email address using the send_verification_email function.
            - Redirects to the account page after attempting to send the verification email.
    """
    email = current_user.email
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('user.account')) 

    if current_user.is_verified:
        flash('Email already verified', 'success')
        return redirect(url_for('user.account'))
        
    send_verification_email(email)

    return redirect(url_for('user.account'))
            

@user_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """
        Verifies a user's email address using a token sent in an email.

        GET:
            - Verifies the token and checks if it is valid.
            - If the token is invalid, flashes an error message and redirects to the account page.
            - Queries the user with the email address associated with the token.
            - If the user is not found, flashes an error message and redirects to the account page.
            - Marks the user as verified and commits the changes to the database.
            - Redirects to the account page after verifying the user's email address. If an error occurs during the commit, rolls back the changes and flashes an error message.
    """
    email = verifyEmail(token)
    if not email:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('user.account'))
        
    user = Users.query.filter_by(email=email).first()
    if not user:
        flash('User not found','error')
        return redirect(url_for('user.account'))

        # Mark the user as verified
    try:
        user.is_verified = True
        db.session.commit()
        flash('Your email has been successfully verified!', 'success')
        return redirect(url_for('user.account'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred : {str(e)}', 'danger')

@user_bp.route('/confirm_email_change/<new_email>', methods=['GET', 'POST'])
@login_required
def confirm_email_change(new_email):
    form =  ConfirmPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=current_user.username).first()
        if user.check_password(form.password.data):
            try:
                current_user.email = new_email
                current_user.is_verified = False
                db.session.commit()
                flash('Your email has been updated. Please verify your new email address.', 'success')
                return redirect(url_for('account'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred : {str(e)}', 'danger')
        else:
            flash('Incorrect password.', 'danger')
    return render_template('confirm_email_change.html', form=form, new_email=new_email)
    
@user_bp.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    form = RequestResetForm()
    if form.validate_on_submit():
        # If the user is authenticated, check their email
        if current_user.is_authenticated:
            if form.email.data == current_user.email:
                send_password_reset(current_user.email)
                flash('A password reset link has been sent to your email.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('You can only request a password reset for your own email.', 'danger')
        else:
        # Check if the email exists in the database
            user = Users.query.filter_by(email=form.email.data).first()
            if user:  # Only send email if user exists!
                send_password_reset(user.email)
                flash('A password reset link has been sent to your email.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('No account found with that email.', 'danger')
    return render_template('request_reset.html', form=form)


@user_bp.route('/verfiy_token/<token>', methods=['GET', 'POST'])
def verfiy_token(token):
    email = token_verfiy(token)
    if email:
        return redirect(url_for('user.reset_password', email= email))
    else:
        return flash('Invalid or expired token', 'error')
    
    
@user_bp.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=email).first()
        if user :
            if user.email != email:
                flash('You can only request a password reset for your own email.', 'danger')
                return redirect(url_for('user.request_reset'))
            try:
                user.set_password(form.password.data)
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('user.reset_success'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred : {str(e)}', 'danger')
        else:
            flash('The password reset link is invalid or has expired.', 'danger')
    return render_template('reset_password.html', form=form)
    
@user_bp.route('/reset_success', methods=['GET', 'POST'])
def reset_success():
    return render_template('reset_success.html')