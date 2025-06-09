from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,current_app
from app.models.user_models import db, Users
from app.routes.groups.group_forms import CreateGroupForm, JoinGroupForm,UpdateProfileForm, Update_Acc_Form, GroupNotesForm, MessageForm, TaskForm, UploadResourceForm, UpdateTaskStatusForm, VerifyEmailForm
from app.models.group_models import StudyGroups, GroupMemberships, GroupResources
from app.models.notification_models import Notifications
from app.models.collaboration_models import Messages, GroupNotes, GroupTasks, GroupMessages
from flask_login import login_required,current_user

group_bp = Blueprint('group', __name__)


@group_bp.route('/create_group', methods=['POST', 'GET'])
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

        if not group_name or not privacy or not description:
            flash('Group name and privacy and description are required.', 'danger')
            return redirect(url_for('group.create_group'))

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
            current_app.logger.error(f"Error creating group: {str(e)}")
            return redirect(url_for('group.create_group'))

    return render_template('create_group.html',form=form)


@group_bp.route('/join_group', methods=['GET', 'POST'])
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
    pagination = StudyGroups.query.paginate(page=page, per_page=per_page, error_out=False)
    groups = pagination.items

    if request.method == 'POST':
        group_id = request.form.get('group_id')  # Ensure the group_id is set in the form data
        if group_id:
            group = StudyGroups.query.get_or_404(group_id)

            if group.privacy == 'private':
                referral_code = request.form.get('referral_code')
                if referral_code != group.referral_code:
                    flash("Invalid referral code. Please try again.", "danger")
                    return redirect(url_for('group.join_group'))

            existing_membership = GroupMemberships.query.filter_by(user_id=current_user.id, group_id=group.id).first()
            if existing_membership:
                flash("You are already a member of this group.", "info")
                return redirect(url_for('group.group', group_id=group.id))
            else:
                membership = GroupMemberships(user_id=current_user.id, group_id=group.id)
                db.session.add(membership)
                db.session.commit()
                flash(f"You have successfully joined the group: {group.name}.", "success")
                return redirect(url_for('group.group', group_id=group.id))
        else:
            flash("There were errors in your submission. Please try again.", "danger")

    return render_template('join_group.html', form=form, groups=groups, pagination=pagination)

@group_bp.route('/leave_group/<int:group_id>', methods=['POST'])
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
        return redirect(url_for('group.group', group_id=group_id))

    return redirect(url_for('home'))
@group_bp.route('/group/<int:group_id>/send_message', methods=['POST'])
@login_required
def send_message(group_id):
    return redirect(url_for("group.group", group_id=group_id))


@group_bp.route('/group/<int:group_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('group.join_group'))

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
        return redirect(url_for('group.group', group_id=group_id))

    if group_notes_form.validate_on_submit():
            group_notes = GroupNotes(
            group_id=group_id,
            last_updated_by=current_user.id,
            content=group_notes_form.content.data
        )
            db.session.add(group_notes)
            db.session.commit()
            flash('Group notes saved successfully!', 'success')
            return redirect(url_for('group.group', group_id=group_id))

    if message_form.validate_on_submit():
        new_message = Messages(content=message_form.content.data, user_id=current_user.id, group_id=group_id)
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('group', group_id=group_id))

    return render_template('group.html', group=group, update_task_status_form=update_task_status_form, group_notes_form=group_notes_form, message_form=message_form, upload_form=upload_form, task_form=task_form,
                        messages=messages, tasks=tasks, latest_notification = latest_notification, resources=resources, group_notes=group_notes)