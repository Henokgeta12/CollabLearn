from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config
from user_models import Users , db # Import Users model here

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config.DevelopmentConfig):
    """
    Creates a Flask application instance with the specified configuration.

    Args:
        config_class (Config): The configuration class to use for the application.
            Defaults to Config.DevelopmentConfig.

    Returns:
        Flask: The created Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user by ID.

        This function is used by Flask-Login to retrieve a user object 
        from the database given the user's ID.

        Args:
            user_id (int): The ID of the user to load.

        Returns:
            Users: The user object corresponding to the provided user ID.
        """
        return Users.query.get(int(user_id))

    # Register routes
    with app.app_context():
        from .routes import register_routes
        register_routes(app)

    return app
