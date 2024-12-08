from flask import Flask
from models import db


def initialize_db():
    app = Flask(__name__)

    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.1.11:3306/project_square' # APT
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@192.168.254.105:3306/project_square'
    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.1.47:3306/project_square' # APT
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

