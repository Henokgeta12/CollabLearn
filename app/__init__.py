from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .extensions import db, login_manager, migrate
from .models.user_models import Users
from CollabLearn.config import Config  



def create_app(config_class=Config):
    """
    Creates a Flask application instance with the specified configuration.

    Args:
        config_class (Config): The configuration class to use for the application.
            Defaults to Config.

    Returns:
        Flask: The created Flask application instance.
    """
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    # Register routes
    with app.app_context():
        from .routes import register_routes  # Import and register routes
        register_routes(app)

    return app
