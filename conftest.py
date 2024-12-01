import pytest
from flask import Flask
from models import db, Users
from blueprints.auth_blueprint import auth_blueprint  

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for testing
    app.config['SECRET_KEY'] = 'test-secret'
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
