from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm
from user_models import db, Users

def register_routes(app):
    @app.route('/')
    def welcome():
        return render_template('welcome.html')
    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html')
    # Route for user registration
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = Users(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            user.set_password(form.password.data)   
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    @login_required
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                # Log the user in (this is where you would set the user session)
                flash(f'Login successful! {form.username.data} you are now logged in.', 'success')
                return redirect(url_for('home'))  # Example redirect after login
            else:
                flash('Invalid username or password', 'danger')

        return render_template('login.html', form=form)

    # Route for user logout
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

