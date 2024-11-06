from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import Users
from .group import Groups, group_user
from .location import Locations
from .camera import Cameras
