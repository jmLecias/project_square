import json
from models import db, Users

def test_register(client):
    # Register a new user
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': '@password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_register_existing_user(client):
    # Register the same user twice
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'User already exists'

def test_login(client, app):
    # Register a user first
    with app.app_context():
        user = Users(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Test valid login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid credentials'

def test_logout(client, app):
    with app.app_context():
        user = Users(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Log in first
    client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Log out
    response = client.post('/auth/logout')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Log out successful'
