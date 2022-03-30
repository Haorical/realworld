from database import db
from datetime import datetime
from hmac import compare_digest
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(32))
    bio = db.Column(db.String(128))
    image = db.Column(db.String(256))
    token: str = ''

    # following = db.Column(db.Integer, nullable=False)
    def __init__(self, username, email, password=None, **kwargs):
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

    # def update(self, **kwargs):
    #     for attr, value in kwargs.items():
    #         setattr(self, attr, value)
