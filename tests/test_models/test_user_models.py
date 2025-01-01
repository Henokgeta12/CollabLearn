import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.models import Users  
from app.extensions import db  

class TestUsersModel(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(Users.query.count(), 1)
        self.assertEqual(Users.query.first().username, 'testuser')
        self.assertEqual(Users.query.first().email, 'test@example.com')
        self.assertIsNotNone(Users.query.first().created_at)
        self.assertTrue(Users.query.first().check_password('Password1'))

    def test_user_password_hashing(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.check_password('Password1'))
        self.assertFalse(user.check_password('WrongPassword'))

    def test_user_update_profile_img(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        user.update_profile_img('new_image.jpg')
        db.session.commit()

        self.assertEqual(Users.query.first().profile_img, 'new_image.jpg')

    def test_user_deletion(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        db.session.delete(user)
        db.session.commit()

        self.assertEqual(Users.query.count(), 0)

    def test_user_unique_constraints(self):
        user1 = Users(username='testuser', email='test@example.com')
        user1.set_password('Password1')
        db.session.add(user1)
        db.session.commit()

        user2 = Users(username='testuser', email='test2@example.com')
        user2.set_password('Password1')
        db.session.add(user2)
        with self.assertRaises(Exception):  # Adjust the exception type based on your validation
            db.session.commit()

        user3 = Users(username='testuser2', email='test@example.com')
        user3.set_password('Password1')
        db.session.add(user3)
        with self.assertRaises(Exception):  # Adjust the exception type based on your validation
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
