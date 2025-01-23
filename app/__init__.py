from flask import Flask
from .extensions import db, login_manager, migrate
from config import Config
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv


    def create_app(config_class=Config):
        """
        Create and configure the Flask application.

        This function sets up the Flask application instance using the provided
        configuration class. It initializes various extensions, configures
        application settings, and registers routes.

        Args:
            config_class (class): The configuration class to use for setting
            application configuration variables.

        Returns:
            app (Flask): The configured Flask application instance.
        """

    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)
    Config.init_app(app)
    app.config['UPLOAD_FOLDER'] = 'static/user_profile-pic'
    app.config['STATIC_FOLDER'] = '/static'
    app.config['STATIC_URL_PATH'] = '/static'
    

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate.init_app(app, db)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user_models import Users
        return Users.query.get(int(user_id))

    # Register routes
    with app.app_context():
        from app.routes import register_routes
        register_routes(app)

    return app

