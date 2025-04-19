from flask import Flask
from .extensions import db, login_manager, migrate, socketio,mail
from config import Config
from .routes.groups.group_routes import group_bp
from .routes.user.user_routes import user_bp
from .routes.authentication.auth_routes import auth_bp 
from .routes.main.main import main_bp
from .routes.groups.groupfunctions_routes import groupfunctions_bp
from .routes.errors.handler import errors_bp
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()

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

        app = Flask(__name__, template_folder="templates", static_folder="static")
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(user_bp, url_prefix='/user')
        app.register_blueprint(group_bp, url_prefix='/group')
        app.register_blueprint(groupfunctions_bp, url_prefix='/groupfunctions')
        app.register_blueprint(errors_bp, url_prefix='/error')
        
        app.config.from_object(config_class)
        Config.init_app(app)
        
        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        migrate.init_app(app, db)

        # Initialize CSRF protection
        csrf = CSRFProtect(app)
        
        # Initialize SocketIO
        socketio.init_app(app)
        
        # Initialize and configure Mail            
        mail.init_app(app)
        
        @login_manager.user_loader
        def load_user(user_id):
            from .models.user_models import Users
            return Users.query.get(int(user_id))

        return app

