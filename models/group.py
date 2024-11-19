from . import db
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
import secrets
import string

group_user = Table(
    'group_user', db.Model.metadata,
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE')),
    Column('user_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
)

class Groups(db.Model):
    id = db.Column(Integer, primary_key=True)
    group_name = db.Column(String(100), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id'))
    group_code = db.Column(String(6), unique=True, nullable=False)
    
    owner = relationship('Users', back_populates='created_groups')
    members = relationship('Users', secondary='group_user')
    locations = relationship('Locations', backref='group', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Group {self.group_name}>'

    def __init__(self, group_name, user_id):
        self.group_name = group_name
        self.user_id = user_id
        self.generate_group_code()

    def generate_group_code(self):
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Groups.query.filter_by(group_code=code).first():
                self.group_code = code
                break
            
    def is_user_in_group(self, user_id):
        """
        Check if a user is the owner of the group or a member of the group.

        :param user_id: The ID of the user to check
        :return: True if the user is the owner or a member, otherwise False
        """
        # Check if the user is the owner
        if self.user_id == user_id:
            return True

        # Check if the user is in the members list
        return any(member.id == user_id for member in self.members)
