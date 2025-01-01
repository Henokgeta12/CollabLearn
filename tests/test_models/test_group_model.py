import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.models import StudyGroups, GroupMemberships, GroupResources, Users  
from app.extensions import db  
class TestStudyGroupsModel(unittest.TestCase):

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

    def test_study_group_creation(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        study_group = StudyGroups(name='Test Group', description='This is a test group', created_by=user.id)
        db.session.add(study_group)
        db.session.commit()

        self.assertEqual(StudyGroups.query.count(), 1)
        self.assertEqual(StudyGroups.query.first().name, 'Test Group')
        self.assertEqual(StudyGroups.query.first().description, 'This is a test group')
        self.assertIsNotNone(StudyGroups.query.first().created_at)
        self.assertIsNotNone(StudyGroups.query.first().referral_code)

    def test_study_group_referral_code(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        study_group = StudyGroups(name='Test Group', description='This is a test group', created_by=user.id)
        db.session.add(study_group)
        db.session.commit()

        self.assertIsNotNone(study_group.referral_code)
        self.assertEqual(len(study_group.referral_code), 11)  # secrets.token_urlsafe(8) generates an 11-character string

    def test_study_group_deletion(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        study_group = StudyGroups(name='Test Group', description='This is a test group', created_by=user.id)
        db.session.add(study_group)
        db.session.commit()

        db.session.delete(study_group)
        db.session.commit()

        self.assertEqual(StudyGroups.query.count(), 0)

    def test_group_membership_creation(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        study_group = StudyGroups(name='Test Group', description='This is a test group', created_by=user.id)
        db.session.add(study_group)
        db.session.commit()

        membership = GroupMemberships(group_id=study_group.id, user_id=user.id, role='member')
        db.session.add(membership)
        db.session.commit()

        self.assertEqual(GroupMemberships.query.count(), 1)
        self.assertEqual(GroupMemberships.query.first().role, 'member')
        self.assertIsNotNone(GroupMemberships.query.first().joined_at)

    def test_group_resources_creation(self):
        user = Users(username='testuser', email='test@example.com')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()

        study_group = StudyGroups(name='Test Group', description='This is a test group', created_by=user.id)
        db.session.add(study_group)
        db.session.commit()

        resource = GroupResources(group_id=study_group.id, uploaded_by=user.id, filename='test.pdf', file_url='http://example.com/test.pdf')
        db.session.add(resource)
        db.session.commit()

        self.assertEqual(GroupResources.query.count(), 1)
        self.assertEqual(GroupResources.query.first().filename, 'test.pdf')
        self.assertEqual(GroupResources.query.first().file_url, 'http://example.com/test.pdf')
        self.assertIsNotNone(GroupResources.query.first().uploaded_at)

if __name__ == '__main__':
    unittest.main()
