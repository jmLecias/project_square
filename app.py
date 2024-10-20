from flask import Flask, current_app
from flask_login import LoginManager
from flask_cors import CORS
from flask_migrate import Migrate
from models import *
import secrets
from dotenv import load_dotenv
from celery import Celery, Task
from flask_redis import FlaskRedis

from blueprints.auth_blueprint import auth_blueprint, oauth
from blueprints.face_blueprint import face_blueprint
from blueprints.groups_blueprint import groups_blueprint

# Load env variables from ENV file
load_dotenv()

app = Flask(__name__)
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
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@172.26.127.26:3306/project_square'
# app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@192.168.254.105:3306/project_square'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
CORS(app, origins=["http://localhost:3000"])


db.init_app(app) 
oauth.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)

app.config['REDIS_URL'] = 'redis://localhost:6379/0'
redis_client = FlaskRedis(app)


class ContextTask(Task):
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return super().__call__(*args, **kwargs)


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(ContextTask):
        def __call__(self, *args: object, **kwargs: object) -> object:
            return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

celery = celery_init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(face_blueprint, url_prefix='/face')
app.register_blueprint(groups_blueprint, url_prefix='/groups')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
