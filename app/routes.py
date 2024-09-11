from flask import render_template, redirect, url_for, flash,request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm
from app.models.user_models import db , Users
from app.models.group_models import StudyGroups, GroupMemberships,GroupResources
from app.models.collaboration_models import  Messages, GroupNotes,GroupTasks,GroupMessages
from app.models.notification_models import Notifications
import os

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
            group_name = request.form.get('group_name')
            description = request.form.get('group_description')
            privacy = request.form.get('group_visibility')
            user_id = current_user.id

            if not group_name or not privacy:
                flash('Group name and privacy are required.', 'danger')
                return redirect(url_for('create_group'))

            try:
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

                # Fetch the group details from the database
                group = StudyGroups.query.get(new_group.id)

                # Fetch the group members
                members = GroupMemberships.query.filter_by(group_id=new_group.id).all()

                # Fetch the referral code for the group (if it's private)
                referral_code = group.referral_code if group.privacy == 'private' else None

                flash('Group created successfully!', 'success')
                return render_template('group_detail.html', group=group, members=members, referral_code=referral_code)

            except Exception as e:
                # An error occurred during the commit, rollback the session
                db.session.rollback()
                # Log the error for debugging purposes
                app.logger.error(f"Error creating group: {str(e)}")
                flash('An error occurred while creating the group.', 'danger')
                return redirect(url_for('create_group'))

        return render_template('create_group.html')


    
    @app.route('/join_group', methods=['GET', 'POST'])
    @login_required
    def join_group():
        if request.method == 'POST':
            # Retrieve the form inputs
            group_identifier = request.form.get('group_identifier')  # This could be the group name (public) or referral code (private)

            # Ensure that the user provided the required input
            if not group_identifier:
                flash('Group name or referral code is required to join a group.', 'danger')
                return redirect(url_for('join_group'))

            # Search for the group by name or referral code
            group = StudyGroups.query.filter(
                (StudyGroups.name == group_identifier) | (StudyGroups.referral_code == group_identifier)
            ).first()

            if not group:
                flash('Group not found with the provided name or referral code.', 'danger')
                return redirect(url_for('join_group'))

            # Handle joining based on the group's privacy
            if group.privacy == 'public':
                # Public group: allow joining by group name
                if group.name != group_identifier:
                    flash('Invalid group name for a public group.', 'danger')
                    return redirect(url_for('join_group'))

            elif group.privacy == 'private':
                # Private group: ensure referral code is used
                if group.referral_code != group_identifier:
                    flash('Invalid referral code for a private group.', 'danger')
                    return redirect(url_for('join_group'))

            # Check if the user is already a member
            existing_membership = GroupMemberships.query.filter_by(group_id=group.id, user_id=current_user.id).first()
            if existing_membership:
                flash('You are already a member of this group.', 'info')
                return redirect(url_for('group', group_id=group.id))

            # Add the user to the group
            new_membership = GroupMemberships(group_id=group.id, user_id=current_user.id, role='member')
            db.session.add(new_membership)
            db.session.commit()

            flash('You have successfully joined the group!', 'success')
            return redirect(url_for('group', group_id=group.id))

        # Handle GET request, render the join group form
        return render_template('join_group.html')


    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('search')  # Get the search query from the URL parameters
        search_results = {'users': [], 'groups': []}

        if query:
            # Search for users matching the query
            search_results['users'] = Users.query.filter(Users.username.ilike(f'%{query}%')).all()

            # Search for study groups matching the query
            search_results['groups'] = StudyGroups.query.filter(StudyGroups.name.ilike(f'%{query}%')).all()

        return render_template('search_results.html', query=query, results=search_results)

    
    @app.route('/group/<int:group_id>', methods=['GET'])
    @login_required
    def group(group_id):
        # Retrieve the group details
        group = StudyGroups.query.get_or_404(group_id)

        # Check if the current user is a member of the group
        membership = GroupMemberships.query.filter_by(group_id=group_id, user_id=current_user.id).first()
        if not membership:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('home'))

        # Retrieve the messages for the group
        messages = Messages.query.filter_by(group_id=group_id).order_by(Messages.created_at.asc()).all()

        # Retrieve tasks and group resources
        tasks = GroupTasks.query.filter_by(group_id=group_id).all()
        resources = GroupResources.query.filter_by(group_id=group_id).all()
        group_notes = GroupNotes.query.filter_by(group_id=group_id).first()

        # Render the group page with the group data
        return render_template('group.html', group=group, messages=messages, tasks=tasks, resources=resources, group_notes=group_notes)
    @app.route('/leave_group/<int:group_id>', methods=['POST'])
    @login_required
    def leave_group(group_id):
        # Retrieve the group and membership details
        group = StudyGroups.query.get_or_404(group_id)
        membership = GroupMemberships.query.filter_by(group_id=group_id, user_id=current_user.id).first()

        if not membership:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('group_detail', group_id=group_id))

        # Remove the user from the group
        db.session.delete(membership)
        db.session.commit()

        flash('You have successfully left the group.', 'success')
        return redirect(url_for('home'))  # Redirect to home or another page

    @app.route('/group/<int:group_id>/send_message', methods=['POST'])
    @login_required
    def send_message(group_id):
        """Handles posting a message to a group."""
        content = request.form.get('content')  # Get the content from the form

        if not content:
            flash("Message content cannot be empty.", "error")
            return redirect(url_for('group', group_id=group_id))

        # Save message to the database
        new_message = Messages(
            group_id=group_id,
            user_id=current_user.id,
            content=content
        )
        db.session.add(new_message)
        db.session.commit()

        # Emit message to clients in real-time using Socket.IO
        socketio.emit('receive_message', {
            'user': current_user.username,
            'content': content,
            'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=str(group_id))

        return redirect(url_for('group', group_id=group_id))

    @app.route('/group/<int:group_id>/post_message', methods=['POST'])
    @login_required
    def post_message(group_id):
        """Handles posting a message to a group (alternative endpoint)."""
        content = request.form.get('content')

        if not content:
            flash("Message content cannot be empty.", "error")
            return redirect(url_for('group', group_id=group_id))

        # Save message to the database
        new_message = Messages(
            group_id=group_id,
            user_id=current_user.id,
            content=content
        )
        db.session.add(new_message)
        db.session.commit()

        # Emit message to clients in real-time using Socket.IO
        socketio.emit('receive_message', {
            'user': current_user.username,
            'content': content,
            'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=str(group_id))

        return redirect(url_for('group', group_id=group_id))

    @app.route('/group/<int:group_id>/upload_resource', methods=['POST'])
    @login_required
    def upload_resource(group_id):
        """Handles file upload to a specific group."""
        # Check if a file was submitted
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('group', group_id=group_id))

        file = request.files['file']

        # If the user does not select a file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('group', group_id=group_id))

        # Save the file and add it to the database
        filename = secure_filename(file.filename)  # You might need to import secure_filename from werkzeug.utils
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save resource information to the database
        new_resource = GroupResources(
            group_id=group_id,
            user_id=current_user.id,
            filename=filename
        )
        db.session.add(new_resource)
        db.session.commit()

        flash('File uploaded successfully!', 'success')
        return redirect(url_for('group', group_id=group_id))

    @app.route('/group/<int:group_id>/create_task', methods=['POST'])
    @login_required
    def create_task(group_id):
        # Retrieve the group based on group_id
        group = group.query.get_or_404(group_id)

        # Get task details from the form submission
        task_title = request.form.get('task_title')
        task_description = request.form.get('task_description')

        # Create a new task
        new_task = Task(title=task_title, description=task_description, group_id=group_id)
        db.session.add(new_task)
        db.session.commit()

        # Redirect back to the group page
        return redirect(url_for('group', group_id=group_id))
