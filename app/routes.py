from flask import render_template, redirect, url_for, flash,request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm
from app.models.user_models import db, Users

def register_routes(app):
    @app.route('/')
    def welcome():
        return render_template('welcome.html')

    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = Users(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)   
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():  
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)  # Properly log the user in
                flash(f'Login successful! {form.username.data} you are now logged in.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))
    @app.route('/create_group', methods=['POST', 'GET'])
    @login_required
    def create_group():
        if request.method == 'POST':
            group_name = request.form['group_name']
            description = request.form['description']
            privacy = request.form['privacy']  # 'public' or 'private'
            user_id = current_user.id  # Current user's ID

            if not group_name or not privacy:
                flash('Group name and privacy are required.', 'danger')
                return redirect(url_for('create_group'))

            # Create the group
            new_group = StudyGroups(
                name=group_name,
                description=description,
                privacy=privacy,
                created_by=user_id
            )
            # Generate referral code
            new_group.generate_referral_code()

            db.session.add(new_group)
            db.session.commit()

            # Add the creator as an admin
            new_membership = GroupMemberships(
                group_id=new_group.id,
                user_id=user_id,
                role='admin'
            )
            db.session.add(new_membership)
            db.session.commit()
            flash('Group created successfully!', 'success')
            return redirect(url_for('group_detail', group_id=new_group.id))

        return render_template('create_group.html')


    @app.route('/join_group', methods=['GET', 'POST'])
    @login_required
    def join_group():
        if request.method == 'POST':
            referral_code = request.form.get('referral_code')

            # Ensure referral code is provided
            if not referral_code:
                flash('Referral code is required to join a group.', 'danger')
                return redirect(url_for('join_group'))

            group = StudyGroups.query.filter_by(referral_code=referral_code).first()

            if not group:
                flash('Group not found with the provided referral code.', 'danger')
                return redirect(url_for('join_group'))

            if group.privacy == 'private':
                flash('This group is private and cannot be joined without an invitation.', 'danger')
                return redirect(url_for('join_group'))

            # Check if user is already a member
            existing_membership = GroupMemberships.query.filter_by(group_id=group.id, user_id=current_user.id).first()
            if existing_membership:
                flash('You are already a member of this group.', 'info')
                return redirect(url_for('group_detail', group_id=group.id))

            # Add the user to the group
            new_membership = GroupMemberships(group_id=group.id, user_id=current_user.id, role='member')
            db.session.add(new_membership)
            db.session.commit()
            flash('You have successfully joined the group!', 'success')
            return redirect(url_for('group_detail', group_id=group.id,))

        return render_template('join_group.html')  # Render form for GET requests   
    @app.route('/group_detail/<int:group_id>', methods=['GET'])
    @login_required
    def group_detail(group_id):
        # Fetch the group from the database using the group ID
        group = StudyGroups.query.get_or_404(group_id)
        
        # Check if the user is a member of the group
        membership = GroupMemberships.query.filter_by(group_id=group.id, user_id=current_user.id).first()

        # If the group is private and the user is not a member, restrict access
        if group.privacy == 'private' and not membership:
            flash('You do not have access to this private group.', 'danger')
            return redirect(url_for('home'))  # Redirect to home or another accessible page

        # Fetch all members of the group to display
        members = GroupMemberships.query.filter_by(group_id=group.id).all()

        # Pass the referral code to the template
        referral_code = group.referral_code

        # Render the group details template with the group and member information
        return render_template('group_details.html', group=group, members=members, referral_code=referral_code)
