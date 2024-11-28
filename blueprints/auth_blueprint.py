from flask import Flask, flash, render_template, Response, request, send_file, redirect, url_for, jsonify, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Users
from authlib.integrations.flask_client import OAuth
import os

auth_blueprint = Blueprint('auth', __name__)

oauth = OAuth()

# Google Oauth
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
)

@auth_blueprint.route('/login/google',  methods=['POST', 'GET'])
def login_google():
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_blueprint.route('/authorize/google', methods=['GET'])
def authorize_google():
    try:
        token = google.authorize_access_token()

        if token:
            resp = google.get('userinfo')
            
            if resp.status_code == 200:
                user_info = resp.json()
                email = user_info['email']
                
                # Find or create the user
                user = Users.query.filter_by(email=email).first()
                if not user:
                    user = Users(email=email)
                    db.session.add(user)
                    db.session.commit()

                login_user(user)

                user_dict = {"id": user.id, "email": user.email}

                return jsonify({'user': user_dict}), 200
                # return redirect('http://localhost:3000')
            else:
                return jsonify({'error': 'Failed to fetch user info'}), 500
        else:
            return jsonify({'error': 'No token received'}), 400
    
    except Exception as e:
        print(f"Error in authorize_google: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Default auth 
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = Users.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Add security token: JWT
    login_user(user)
    
    user_dict = {
        "id": user.id, 
        "email": user.email,
        "name": user.user_info.full_name if user.user_info else None,
        "image": user.identity_image if user.has_identity else None
    }
    
    return jsonify({'user': user_dict}), 200


@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    new_user = Users(
        email=email
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)

    user_dict = {"id": new_user.id, "email": new_user.email}

    return jsonify({'user': user_dict}), 201


@auth_blueprint.route('/logout', methods=['POST'])
# @login_required // needs authorization token something...
def logout():
    logout_user()
    return jsonify({'message': 'Log out successful'}), 200