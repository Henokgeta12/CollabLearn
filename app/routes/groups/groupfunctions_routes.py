from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.group_models import StudyGroups, GroupMemberships, GroupResources
from app.models.user_models import Users, db
from .group_forms import UpdateTaskStatusForm,TaskForm,UploadResourceForm
from app.models.notification_models import Notifications
from app.models.collaboration_models import Messages, GroupNotes, GroupTasks, GroupMessages
from flask_login import login_required

groupfunctions_bp = Blueprint('groupfunctions', __name__)

@groupfunctions_bp.route('/group/<int:group_id>/update_task_status', methods=['POST'])
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

@groupfunctions_bp.route('/group/<int:group_id>/save_group_notes', methods=['POST'])
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
    return redirect(url_for('group.group', group_id=group_id))

@groupfunctions_bp.route('/group/<int:group_id>/create_task', methods=['POST'])
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


@groupfunctions_bp.route('/group/<int:group_id>/upload_resource', methods=['POST'])
@login_required
def upload_resource(group_id):
    """
        Upload a resource to a group.

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