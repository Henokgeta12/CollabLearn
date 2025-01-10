from flask import Flask
from .extensions import db, login_manager, migrate
from config import Config
from flask_wtf.csrf import CSRFProtect



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
    app.config.from_object(config_class)
    Config.init_app(app)
    app.config['UPLOAD_FOLDER'] = 'static/user_profile-pic'
    # app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit upload size to 2MB
    CSRFProtect(app)


    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user_models import Users
        return Users.query.get(int(user_id))

    # Register routes
    with app.app_context():
        from app.routes import register_routes  # Import and register routes
        register_routes(app)

    return app
