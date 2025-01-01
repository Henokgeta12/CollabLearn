import pytest
from app import create_app
from app.models.user_models import db, Users
from app.models.group_models import StudyGroups, GroupMemberships

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'os.getenv('DATABASE_URL'),
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def create_user(app):
    with app.app_context():
        user = Users(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user
