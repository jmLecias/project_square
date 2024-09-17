from flask import Flask, flash, render_template, Response, request, send_file, redirect, url_for, jsonify, Blueprint, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_migrate import Migrate
from models import *
import secrets
from dotenv import load_dotenv

from blueprints.auth import auth_blueprint, oauth
from blueprints.face import face_blueprint

# Load env variables from ENV file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1:3306/project_square'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
CORS(app, origins=["http://localhost:3000"])

db.init_app(app) 
oauth.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(face_blueprint, url_prefix='/face')

# @app.route('/auth/login/google')
# def login_google():
#     try:
#         redirect_uri = url_for('authorize_google', _external=True)
#         return google.authorize_redirect(redirect_uri)
#     except Exception as e:
#         app.logger.error(f"Error during login: {str(e)}")
#         return "Error occured during login", 500
    
# @app.route('/auth/authorize/google')
# def authorize_google():
#     token = google.authorize_access_token()
#     userinfo_endpoint = google.server_metadata('userinfo_endpoint')
#     resp = google.get(userinfo_endpoint)
#     user_info = resp.json()
#     email = user_info['email']
    
#     user = Users.query.filter_by(email=email).first()
#     if not user:
#         user = Users(email=email)
#         db.session.add(user)
#         db.session.commit()
    
#     session['email'] = email
#     session['oauth_token'] = token
    
#     return "User authorized", 200
    

@app.route('/')
def index():
    return "index"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
