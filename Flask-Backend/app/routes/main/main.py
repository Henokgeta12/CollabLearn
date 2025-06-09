from flask import Flask, render_template,Blueprint, request,jsonify,url_for
from flask_login import login_required,current_user
from app.models.group_models import StudyGroups
from app.models.user_models import Users
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def welcome():
    """
        The welcome route renders the welcome template.

        This route is accessible to unauthenticated users.

        :returns: The rendered welcome template
    """
    return render_template('welcome.html')

@main_bp.route('/home',methods=['GET', 'POST'])
@login_required
def home():
    """
        The home route renders the home template.

        This route is only accessible to authenticated users.

        :returns: The rendered home template
    """
    return render_template('home.html')

@main_bp.route('/search', methods=['GET'])
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

@main_bp.route('/get_account_info', methods=['GET'])
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