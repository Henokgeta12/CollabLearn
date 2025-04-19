from flask import Flask, request, redirect, url_for, flash, render_template, jsonify,send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegistrationForm, LoginForm, UpdateProfileForm, Update_Acc_Form, JoinGroupForm, CreateGroupForm, MessageForm, UploadResourceForm, TaskForm, UpdateTaskStatusForm, GroupNotesForm,JoinGroupForm,VerifyEmailForm, ConfirmPasswordForm,ResetPasswordForm,RequestResetForm
from .models.user_models import db, Users
from .models.group_models import StudyGroups, GroupMemberships, GroupResources
from .models.collaboration_models import Messages, GroupNotes, GroupTasks, GroupMessages
from .models.notification_models import Notifications
from .extensions import allowed_file,socketio,send_verification_email,verifyEmail,reset_password,send_password_reset
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import hashlib

"""
    Registers routes for the application.

    The routes include:
    - Homepage
    - Login
    - Logout
    - Register
    - Create group
    - Join group
    - Search
    - Group detail
    - Update profile
    - Update account
    - Get account information

    The functions are decorated with route, login_required, and methods.
"""
def register_routes(app):
    @app.route('/')
    def welcome():
        """
        The welcome route renders the welcome template.

        This route is accessible to unauthenticated users.

        :returns: The rendered welcome template
        """
        return render_template('welcome.html')

    @app.route('/home',methods=['GET', 'POST'])
    @login_required
    def home():
        """
        The home route renders the home template.

        This route is only accessible to authenticated users.

        :returns: The rendered home template
        """
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        The register route renders the registration template.

        This route is only accessible to unauthenticated users.

        The route uses the RegistrationForm to validate the user's input.
        If the input is valid, the user's information is stored in the database.

        :returns: The rendered registration template
        """
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
        """
        The login route handles user authentication.

        This route is accessible to unauthenticated users and allows them to log in using their credentials.
        If the user is already authenticated, they are redirected to the home page.

        The route uses the LoginForm to validate the user's input. If the input is valid and the username and 
        password are correct, the user is logged in and redirected to the home page. Otherwise, an error 
        message is displayed.

        :returns: The rendered login template or a redirect to the home page
        """
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Login successful! {form.username.data} you are now logged in.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        """
        The logout route handles user logout.

        This route is accessible to authenticated users and logs them out. The user is redirected to the home page.

        :returns: A redirect to the home page
        """
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/create_group', methods=['POST', 'GET'])
    @login_required
    def create_group():
        """
        Handle the creation of a new study group.

        This route is accessible only to authenticated users and allows them to create a new study group by
        filling out a form with the group's name, description, and privacy settings. Upon successful creation,
        the group is saved to the database, the current user is added as an admin member, and a referral code is
        generated if the group is private.

        POST:
            - Validates and processes the group creation form.
            - Creates a new group instance with the provided details.
            - Adds the group to the database.
            - Assigns the current user as an admin of the new group.
            - Renders the group detail page upon success or redirects back to the creation page on failure.

        GET:
            - Renders the group creation form.

        :returns: The rendered group detail template on success or redirect to the creation form on failure.
        """
        form = CreateGroupForm()
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
                return redirect(url_for('create_group'))

        return render_template('create_group.html',form=form)
    
    @app.route('/join_group_api', methods=['POST'])
    @login_required
    def join_group_api():
        """
        Handles POST requests to join a study group via its name or referral code. If the group is found, the user is added to the group and a success message is returned. If the user is already a member, a failure message is returned. If the group is not found, a 404 error is returned.

        :param group_identifier: The name or referral code of the group to join.
        :returns: A JSON object containing a success message and a redirect URL if the group was found and the user was added, a failure message if the user is already a member, or a 404 error if the group was not found.
        """
        group_identifier = request.form.get('group_identifier')
        group = StudyGroups.query.filter_by(name=group_identifier).first()  # Adjust this to use name or referral code

        if not group:
            return jsonify({'success': False, 'message': 'Group not found.'}), 404

        # Check if the user is already a member
        membership = GroupMemberships.query.filter_by(group_id=group.id, user_id=current_user.id).first()
        if membership:
            return jsonify({'success': False, 'message': 'You are already a member of this group.'})

        # Add user to the group
        new_membership = GroupMemberships(group_id=group.id, user_id=current_user.id)
        db.session.add(new_membership)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully joined {group.name}.',
            'redirect_url': url_for('group', group_id=group.id)  # Construct the URL for the group details page
        })

    @app.route('/join_group', methods=['GET', 'POST'])
    @login_required
    def join_group():
        """
        Renders the join group page and handles the logic for joining a study group.

        GET requests display a paginated list of public study groups that the user can join.
        POST requests handle the user attempting to join a specific group by its ID. If the group
        is private, a valid referral code is required. Checks are performed to ensure the user
        is not already a member before adding them to the group.

        Returns:
            - On GET: Renders 'join_group.html' template with a form, list of groups, and pagination details.
            - On POST:
                - Redirects to the group page if the user successfully joins the group.
                - Redirects to the join group page with a flash message if the referral code is invalid
                or if the user is already a member.
                - Displays an error flash message if submission fails.

        Raises:
            - 404 if the group ID is invalid or not found.
        """
        form = JoinGroupForm()
        page = request.args.get('page', 1, type=int)
        per_page = 5
        pagination = StudyGroups.query.filter_by(privacy='public').paginate(page=page, per_page=per_page, error_out=False)
        groups = pagination.items

        if request.method == 'POST':
            group_id = request.form.get('group_id')  # Ensure the group_id is set in the form data
            if group_id:
                group = StudyGroups.query.get_or_404(group_id)

                if group.privacy == 'private':
                    referral_code = request.form.get('referral_code')
                    if referral_code != group.referral_code:
                        flash("Invalid referral code. Please try again.", "danger")
                        return redirect(url_for('join_group'))

                existing_membership = GroupMemberships.query.filter_by(user_id=current_user.id, group_id=group.id).first()
                if existing_membership:
                    flash("You are already a member of this group.", "info")
                    return redirect(url_for('group', group_id=group.id))
                else:
                    membership = GroupMemberships(user_id=current_user.id, group_id=group.id)
                    db.session.add(membership)
                    db.session.commit()
                    flash(f"You have successfully joined the group: {group.name}.", "success")
                    return redirect(url_for('group', group_id=group.id))
            else:
                flash("There were errors in your submission. Please try again.", "danger")

        return render_template('join_group.html', form=form, groups=groups, pagination=pagination)
                
    @app.route('/search', methods=['GET'])
    def search():
        """
        Handles GET requests to search for users and study groups by name.
        
        Returns a JSON object with two keys: 'users' and 'groups'. The values are lists of dictionaries
        containing the user/group details. If the search query is empty, returns a 400 error with a JSON
        object containing an 'error' key with a descriptive message.
        
        Example response: {
            'users': [
                {'id': 1, 'username': 'johnDoe', 'email': 'john@example.com'},
                {'id': 2, 'username': 'janeDoe', 'email': 'jane@example.com'}
            ],
            'groups': [
                {'id': 1, 'name': 'Math Study Group', 'description': 'A group for math students.'},
                {'id': 2, 'name': 'Science Study Group', 'description': 'A group for science students.'}
            ]
        }
        """
        search_query = request.args.get('search', '').strip()

        if not search_query:
            return jsonify({"error": "Search query cannot be empty"}), 400
        
        search_results = {'users': [], 'groups': []}

        if search_query:
            search_results['users'] = [
                user.to_dict() for user in Users.query.filter(Users.username.ilike(f'%{search_query}%')).all()
            ]

            # Search for groups by name
            search_results['groups'] = [
                group.to_dict() for group in StudyGroups.query.filter(StudyGroups.name.ilike(f'%{search_query}%')).all()
            ]
        return jsonify(search_results)

    
    @app.route('/leave_group/<int:group_id>', methods=['POST'])
    @login_required
    def leave_group(group_id):
        """
        Handles POST requests to leave a study group. If the user is not a member of the group, a danger flash message is displayed and the user is redirected to the group details page. If the user is a member, their membership is deleted, and a success flash message is displayed. If an error occurs while deleting the membership, an error message is displayed and the user is redirected to the group details page.

        Returns:
            - Redirects to the home page if the user successfully leaves the group.
            - Redirects to the group details page with a flash message if the user is not a member or if an error occurs.

        Raises:
                - 404 if the group ID is invalid or not found.
        """
        group = StudyGroups.query.get_or_404(group_id)
        membership = GroupMemberships.query.filter_by(group_id=group_id, user_id=current_user.id).first()

        if not membership:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('group_detail', group_id=group_id))

        try:
            db.session.delete(membership)
            db.session.commit()
            flash('You have successfully left the group.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while leaving the group: {str(e)}', 'danger')
            return redirect(url_for('group_detail', group_id=group_id))

        return redirect(url_for('home'))
    @app.route('/group/<int:group_id>/send_message', methods=['POST'])
    @login_required
    def send_message(group_id):
        """
        Handles POST requests to send a message in a study group. If the user is not a member of the group, a danger flash message is displayed and the user is redirected to the group details page. If the user is a member, the message is saved to the database, and a success flash message is displayed. If an error occurs while saving the message, an error message is displayed and the user is redirected to the group details page.

        Returns:
            - Redirects to the home page if the user successfully sends a message.
            - Redirects to the group details page with a flash message if the user is not a member or if an error occurs.

        Raises:
            - 404 if the group ID is invalid or not found.
        """
        message_form = MessageForm()
        if message_form.validate_on_submit():
            content = message_form.content.data
            if not content:
                flash("Message content cannot be empty.", "error")
                return redirect(url_for('group', group_id=group_id))

            new_message = Messages(
                group_id = group_id,
                user_id = current_user.id,
                content = content
            )
            db.session.add(new_message)
            db.session.commit()

            socketio.emit('receive_message', 
            {
                'user': current_user.username,
                'content': content,
                'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=str(group_id))

            flash('Message sent successfully!', 'success')
            return redirect(url_for('group', group_id=group_id))

        return render_template('group.html', message_form=message_form)

    @app.route('/group/<int:group_id>', methods=['GET', 'POST'])
    @login_required
    def group(group_id):
        """
        Handles GET and POST requests to view and interact with a study group. If the user is not a member of the group, a danger flash message is displayed and the user is redirected to the home page.

        GET requests render the group.html template with the group details, messages, tasks, latest notification, resources, and group notes.

        POST requests handle the submission of the following forms:

        - UpdateTaskStatusForm: Updates the status of a task in the group.
        - GroupNotesForm: Updates the group notes.
        - MessageForm: Sends a new message in the group.
        - UploadResourceForm: Uploads a new resource to the group.
        - TaskForm: Creates a new task in the group.
        If the form is valid, the appropriate action is taken and a success flash message is displayed. If the form is invalid or an error occurs, an error message is displayed and the user is redirected to the group details page.

        Returns:
            - Redirects to the home page if the user is not a member of the group.
            - Redirects to the group details page with a flash message if the form is invalid or an error occurs.
            - Renders the group.html template with the group details and form data if the form is valid.

        Raises:
            - 404 if the group ID is invalid or not found.
        """

        group = StudyGroups.query.get_or_404(group_id)
        membership = GroupMemberships.query.filter_by(group_id=group_id, user_id=current_user.id).first()

        if not membership:
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('join_group'))

        messages = Messages.query.filter_by(group_id=group_id).order_by(Messages.created_at.asc()).all()
        tasks = GroupTasks.query.filter_by(group_id=group_id).all()
        latest_notification = Notifications.query.filter_by(user_id=current_user.id).order_by(Notifications.id.desc()).first()
        resources = GroupResources.query.filter_by(group_id=group_id).all()
        group_notes = GroupNotes.query.filter_by(group_id=group_id).first()

        update_task_status_form = UpdateTaskStatusForm()
        group_notes_form = GroupNotesForm()
        message_form = MessageForm()
        upload_form = UploadResourceForm()
        task_form = TaskForm()

        if update_task_status_form.validate_on_submit():
            task_id = request.form.get('task_id')
            new_status = update_task_status_form.status.data
            task = GroupTasks.query.get(task_id)
            task.status = new_status
            db.session.commit()
            flash('Task status updated successfully!', 'success')
            return redirect(url_for('group', group_id=group_id))

        if group_notes_form.validate_on_submit():
                group_notes = GroupNotes(
                group_id=group_id,
                last_updated_by=current_user.id,
                content=group_notes_form.content.data
            )
                db.session.add(group_notes)
                db.session.commit()
                flash('Group notes saved successfully!', 'success')
                return redirect(url_for('group', group_id=group_id))

        if message_form.validate_on_submit():
            new_message = Messages(content=message_form.content.data, user_id=current_user.id, group_id=group_id)
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent successfully!', 'success')
            return redirect(url_for('group', group_id=group_id))

        return render_template('group.html', group=group, update_task_status_form=update_task_status_form, group_notes_form=group_notes_form, message_form=message_form, upload_form=upload_form, task_form=task_form,
                            messages=messages, tasks=tasks, latest_notification = latest_notification, resources=resources, group_notes=group_notes)

        
    @app.route('/group/<int:group_id>/update_task_status', methods=['POST'])
    @login_required
    def update_task_status(group_id):
        """
        Update the status of a specific task within a group.

        This route handles the form submission for updating the status of a task.
        It validates the presence of a task ID and fetches the corresponding task
        from the database. If the task is found, its status is updated with the new
        status provided in the form, and the changes are committed to the database.
        Success or error messages are flashed accordingly.

        Args:
            group_id (int): The ID of the group to which the task belongs.

        Returns:
            A redirect to the group's page with a flash message indicating the
            success or failure of the operation.
        """
        task_id = request.form.get('task_id')
        new_status = request.form.get('status')
        if not task_id:
            flash('Task ID is missing.', 'danger')
            return redirect(url_for('group', group_id=group_id))

        task = GroupTasks.query.get(task_id)
        
        if not task:
            flash('Task not found.', 'danger')
            return redirect(url_for('group', group_id=group_id))
            
        task.status = new_status
        db.session.commit()
        flash('Task status updated successfully!', 'success')
        return redirect(url_for('group', group_id=group_id))

    @app.route('/group/<int:group_id>/save_group_notes', methods=['POST'])
    @login_required
    def save_group_notes(group_id):
        """
        Save the content of a group's notes.

        This route handles the submission of a form from the group page
        containing the updated content of the group's notes. It fetches the
        corresponding GroupNotes object from the database, updates its
        content, and commits the changes. Success or error messages are
        flashed accordingly.

        Args:
            group_id (int): The ID of the group whose notes are being updated.

        Returns:
            A redirect to the group's page with a flash message indicating the
            success or failure of the operation.
        """
        group_notes = GroupNotes.query.filter_by(group_id=group_id).first()
        group_notes.content = request.form.get('content')
        db.session.commit()
        flash('Group notes saved successfully!', 'success')
        return redirect(url_for('group', group_id=group_id))

    @app.route('/group/<int:group_id>/create_task', methods=['POST'])
    @login_required
    def create_task(group_id):
        """
        Handles the submission of the task creation form on the group page.
        
        Fetches the corresponding group from the database and validates the
        form data. If the form is valid, a new GroupTasks object is created with
        the provided task description, assigned to the current user, and added
        to the database. Success or error messages are flashed accordingly.
        
        Args:
            group_id (int): The ID of the group to which the task belongs.
        
        Returns:
            A redirect to the group's page with a flash message indicating the
            success or failure of the operation.
        """
        task_form = TaskForm()
        group = StudyGroups.query.get_or_404(group_id)

        if task_form.validate_on_submit():
            task_description = task_form.task_description.data
            new_task = GroupTasks(group_id=group_id, task_description=task_description, status='pending')
            try:
                db.session.add(new_task)
                db.session.commit()
                flash('Task added successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred : {str(e)}', 'danger')

            # Notify other group members
            for member in group.members:
                if member.id != current_user.id:
                    notification = Notifications(
                        user_id=member.id,
                        message=f"{current_user.username} added a new task in {group.name}: {task_description}"
                    )
                    try:
                        db.session.add(notification)
                        db.session.commit()
                        return redirect(url_for('group', group_id=group_id))
                    except Exception as e:
                        db.session.rollback()
                        flash(f'An error occurred : {str(e)}', 'danger')
                            
        return render_template('group.html', task_form=task_form)


    @app.route('/group/<int:group_id>/upload_resource', methods=['POST'])
    @login_required
    def upload_resource(group_id):
        """Upload a resource to a group.

        This view accepts a POST request from the "Upload Resource" form in the group
        page. It validates the form data using the UploadResourceForm object. If the
        form is valid, a new GroupResources object is created with the provided file
        details and added to the database. Success or error messages are flashed
        accordingly.

        Args:
            group_id (int): The ID of the group to which the resource belongs.

        Returns:
            A redirect to the group's page with a flash message indicating the
            success or failure of the operation.
        """

        upload_form = UploadResourceForm()

        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('group', group_id=group_id))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('group', group_id=group_id))

        if upload_form.validate_on_submit():
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)

            new_resource = GroupResources(
                group_id=group_id,
                uploaded_by=current_user.id,
                filename=filename,
                file_url=filepath
            )
            db.session.add(new_resource)
            db.session.commit()

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('group', group_id=group_id))

        return render_template('group.html', upload_form=upload_form)


    @app.route('/account', methods=['GET', 'POST'])
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
                    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, unique_filename)
                    file.save(filepath)
                    current_user.update_profile_img(unique_filename)
                    db.session.commit()
                    flash('Profile image updated successfully!', 'success')
                    return redirect(url_for('account'))
                else:
                    flash('Invalid file type. Please upload a valid image file.', 'error')
            else:
                flash('No file selected. Please select a file to upload.', 'error')

        return render_template('account.html', img_file=img_file, profile_form=profile_form, account_form=account_form,verify_form = verify_form,verified=current_user.is_verified)

    @app.route('/update_profile', methods=['GET', 'POST'])
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
                current_user.username = account_form.username.data 
                flash('Account information updated successfully!', 'success')
                return redirect(url_for('update_profile'))
            else:
                flash('No changes were made to your profile.','info')
                return redirect(url_for('update_profile'))

        return render_template('account.html',img_file = img_file,verified=current_user.is_verified, account_form=account_form, profile_form = profile_form ,verify_form = verify_form)

    @app.route('/get_account_info', methods=['GET'])
    @login_required
    def get_account_info():
        """
        Returns the current user's account information, including profile picture and
        groups created, in JSON format.

        GET:
            Returns the current user's account information in JSON format.
        """
        img_file = url_for('static', filename='user_profile_pic/' + current_user.profile_img)
        
        # Query the groups created by the current user
        group = StudyGroups.query.filter_by(created_by=current_user.id).all()
        
        # Convert the groups to a dictionary format for JSON response
        groups_info = [{'id': group.id, 'name': group.name, 'description': group.description, 'privacy': group.privacy} for group in group]
        
        account_info = {
            'username': current_user.username,
            'email': current_user.email,
            'img_file': img_file,
            'created_groups': groups_info  # Add the created groups
        }
        return jsonify(account_info)


    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'static/images/favicon-16x16.ico', mimetype='image/x-icon')
    
    @app.route('/send-verification', methods=['POST'])
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
            return redirect(url_for('account')) 

        if current_user.is_verified:
            flash('Email already verified', 'success')
            return redirect(url_for('account'))
        
        send_verification_email(email)

        return redirect(url_for('account'))
            

    @app.route('/verify-email/<token>', methods=['GET'])
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
            return redirect(url_for('account'))
        
        user = Users.query.filter_by(email=email).first()
        if not user:
            flash('User not found','error')
            return redirect(url_for('account'))

        # Mark the user as verified
        try:
            user.is_verified = True
            db.session.commit()
            flash('Your email has been successfully verified!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred : {str(e)}', 'danger')

    @app.route('/confirm_email_change/<new_email>', methods=['GET', 'POST'])
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
    
    @app.route('/request_reset', methods=['GET', 'POST'])
    def request_reset():
        form = RequestResetForm()
        if form.validate_on_submit():
            # If the user is authenticated, check their email
            if current_user.is_authenticated:
                if form.email.data == current_user.email:
                    send_password_reset(current_user.email)
                    flash('A password reset link has been sent to your email.', 'info')
                    return redirect(url_for('login'))
                else:
                    flash('You can only request a password reset for your own email.', 'danger')
            else:
                # Check if the email exists in the database
                user = Users.query.filter_by(email=form.email.data).first()
                if user:  # Only send email if user exists!
                    send_password_reset(user.email)
                    flash('A password reset link has been sent to your email.', 'info')
                    return redirect(url_for('login'))
                else:
                    flash('No account found with that email.', 'danger')
        return render_template('request_reset.html', form=form)

    
    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        form = ResetPasswordForm()
        if form.validate_on_submit():
            try:
                email = reset_password(token)
                user = User.query.filter_by(email=email).first()
                if user and email:
                    user.set_password(email)
                    db.session.commit()
                    flash('Your password has been updated!', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('The password reset link is invalid or has expired.', 'danger')
            except:
                flash('The password reset link is invalid or has expired.', 'danger')
        return render_template('reset_password.html', form=form)
    
    @app.route('/reset_success', methods=['GET', 'POST'])
    def reset_success():
        return render_template('reset_success.html')
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "message": "An internal error occurred."}), 500

    