import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.models import Notifications, Users  
from app.extensions import db  

class TestNotificationsModel(unittest.TestCase):

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

    def test_notification_creation(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        db.session.add(user)
        db.session.commit()

        notification = Notifications(user_id=user.id, message='Test notification', read=False)
        db.session.add(notification)
        db.session.commit()

        self.assertEqual(Notifications.query.count(), 1)
        self.assertEqual(Notifications.query.first().message, 'Test notification')
        self.assertFalse(Notifications.query.first().read)
        self.assertIsNotNone(Notifications.query.first().created_at)

    def test_notification_read_update(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        db.session.add(user)
        db.session.commit()

        notification = Notifications(user_id=user.id, message='Test notification', read=False)
        db.session.add(notification)
        db.session.commit()

        notification.read = True
        db.session.commit()

        self.assertTrue(Notifications.query.first().read)

    def test_notification_deletion(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        db.session.add(user)
        db.session.commit()

        notification = Notifications(user_id=user.id, message='Test notification', read=False)
        db.session.add(notification)
        db.session.commit()

        db.session.delete(notification)
        db.session.commit()

        self.assertEqual(Notifications.query.count(), 0)

    def test_notification_relationship(self):
        user = Users(username='testuser', email='test@example.com', password='Password1')
        db.session.add(user)
        db.session.commit()

        notification1 = Notifications(user_id=user.id, message='Test notification 1', read=False)
        notification2 = Notifications(user_id=user.id, message='Test notification 2', read=False)
        db.session.add(notification1)
        db.session.add(notification2)
        db.session.commit()

        self.assertEqual(len(user.notifications), 2)
        self.assertEqual(user.notifications[0].message, 'Test notification 1')
        self.assertEqual(user.notifications[1].message, 'Test notification 2')

if __name__ == '__main__':
    unittest.main()
