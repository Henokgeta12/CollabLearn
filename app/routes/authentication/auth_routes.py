from flask import Blueprint, render_template, redirect, url_for, flash
from app.routes.authentication.auth_forms import RegistrationForm, LoginForm
from app.models.user_models import Users
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
        The login route handles user authentication.

        This route is accessible to unauthenticated users and allows them to log in using their credentials.
        If the user is already authenticated, they are redirected to the home page.

        The route uses the LoginForm to validate the user's input. If the input is valid and the username and 
        password are correct, the user is logged in and redirected to the home page. Otherwise, an error 
        message is displayed.

        returns: The rendered login template or a redirect to the home page
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Login successful! {form.username.data} you are now logged in.', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
        The logout route handles user logout.

        This route is accessible to authenticated users and logs them out. The user is redirected to the home page.

        :returns: A redirect to the home page
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
        The register route renders the registration template.

        This route is only accessible to unauthenticated users.

        The route uses the RegistrationForm to validate the user's input.
        If the input is valid, the user's information is stored in the database.

        :returns: The rendered registration template
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)