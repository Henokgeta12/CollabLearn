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



