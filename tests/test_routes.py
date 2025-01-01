import pytest
from flask import url_for

def test_welcome_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_register_user(client, app):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password',
        'confirm': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your account has been created!' in response.data

def test_login_user(client, create_user):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful!' in response.data

def test_logout_user(client, create_user):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })
    response = client.post('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data

def test_create_group(client, create_user, app):
    with client:
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        response = client.post('/create_group', data={
            'group_name': 'Study Group 1',
            'group_description': 'A test group',
            'group_visibility': 'public'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Group created successfully!' in response.data

def test_join_group(client, create_user, app):
    with app.app_context():
        # Create a public group
        group = StudyGroups(name="Public Group", privacy="public", created_by=1)
        db.session.add(group)
        db.session.commit()

    with client:
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        response = client.post('/join_group', data={
            'group_identifier': 'Public Group'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'You have successfully joined the group!' in response.data
