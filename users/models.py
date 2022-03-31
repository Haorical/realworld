from database import db
from flask_bcrypt import Bcrypt


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(32))
    bio = db.Column(db.String(128))
    image = db.Column(db.String(256))
    token: str = ''

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = Bcrypt().generate_password_hash(password)

    def check_password(self, value):
        return Bcrypt().check_password_hash(self.password, value)

    def check_follow(self, au):
        following = Follow.query.filter_by(id1=self.id, id2=au).first()
        if not following:
            return False
        return following.following


class Follow(db.Model):
    __tablename__ = 'follows'
    id1 = db.Column(db.Integer, primary_key=True)
    id2 = db.Column(db.Integer, primary_key=True)
    following = db.Column(db.Boolean, default=False)
