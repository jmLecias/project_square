from flask import Flask, current_app
from flask_login import LoginManager
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Users, seed_cameras, seed_status
import secrets
from dotenv import load_dotenv
from celery import Celery, Task

from flask_redis import FlaskRedis
from celery_app import make_celery
from utils.socket_utils import socketio

from blueprints.auth_blueprint import auth_blueprint, oauth
from blueprints.face_blueprint import face_blueprint
from blueprints.groups_blueprint import groups_blueprint
from blueprints.locations_blueprint import locations_blueprint
from blueprints.bucket_blueprint import bucket_blueprint
from blueprints.identity_blueprint import identity_blueprint
from blueprints.records_blueprint import records_blueprint
from blueprints.cameras_blueprint import cameras_blueprint

# Load env variables from ENV file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost:3306/project_square'
    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@172.26.127.26:3306/project_square' # Zero tier
    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.137.224:3306/project_square' # LNU lan
    app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.254.100:3306/project_square' # Globe router
    # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.1.13:3306/project_square' # APT
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'

    login_manager = LoginManager(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    @app.cli.command('seed-cameras')
    @with_appcontext
    def seed_cameras_command():
        """Seed the cameras data"""
        seed_cameras()

    @app.cli.command('seed-detection-status')
    @with_appcontext
    def seed_detection_status_command():
        """Seed the cameras data"""
        seed_status()
    
    return (app)

app = create_app()
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379", 
        result_backend="redis://localhost:6379", 
    ),
    # CELERY=dict(
    #     broker_url="redis://172.26.127.26:6379", 
    #     result_backend="redis://172.26.127.26:6379", # Using Zerotier
    # ),
)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)


# CORS(app)
CORS(app, resources={
    r"/*": {
        "origins": ["https://official-square.site", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

socketio.init_app(app)
db.init_app(app) 
oauth.init_app(app)
migrate = Migrate(app, db)
redis_client = FlaskRedis(app)

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

celery = celery_init_app(app)


app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(face_blueprint, url_prefix='/face')
app.register_blueprint(groups_blueprint, url_prefix='/groups')
app.register_blueprint(locations_blueprint, url_prefix='/locations')
app.register_blueprint(bucket_blueprint, url_prefix='/bucket')
app.register_blueprint(identity_blueprint, url_prefix='/identity')
app.register_blueprint(records_blueprint, url_prefix='/records')
app.register_blueprint(cameras_blueprint, url_prefix='/cameras')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
