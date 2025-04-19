import os
from dotenv import load_dotenv
import logging


load_dotenv()

class Config:
    """Base configuration."""
    LOGGING_LEVEL = logging.ERROR
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = False
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit, for example
    UPLOAD_FOLDER = 'static/user_profile-pic'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
    MAIL_SERVER='smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_DEFAULT_SENDER= os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_SUPPRESS_SEND = False


    # Custom MIME type mapping
    MIME_TYPES = {
        '.ico': 'image/x-icon'
    }

    @staticmethod
    def init_app(app):
        # Initialize logging
        logging.basicConfig(level=Config.LOGGING_LEVEL)
        logger = logging.getLogger(__name__)
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)

        # Initialize the app with custom MIME types
        app.config['MIME_TYPES'] = Config.MIME_TYPES

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log all SQL statements, useful for debugging


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL')  # Use a separate database for testing



