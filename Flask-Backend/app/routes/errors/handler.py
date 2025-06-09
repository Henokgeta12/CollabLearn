from flask import Blueprint, jsonify

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An internal error occurred."}), 500
    
@errors_bp.app_errorhandler(403)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "you dont have permission to do that "}), 500
    