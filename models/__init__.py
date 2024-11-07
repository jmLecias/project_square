from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import Users, UserInfos
from .face_image import FaceImages
from .group import Groups, group_user
from .location import Locations
from .camera import Cameras
