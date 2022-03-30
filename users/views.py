from datetime import datetime
from hmac import compare_digest
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt_identity
from .models import Author
from database import db
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import pymysql

pymysql.install_as_MySQLdb()

blueprint = Blueprint('user', __name__)


def gen_user(username=None, email=None, bio=None, image=None, token=None):
    return {
        "user": {
            "email": email,
            "username": username,
            "bio": bio,
            "image": image,
            "token": token
        }
    }


@blueprint.route('/api/users/login', methods=['POST'])  # 认证
def login():
    data = request.get_json()
    email = data['user']['email']
    password = data['user']['password']
    user = Author.query.filter_by(email=email).first()
    if user is not None and user.check_password(password):
        user.token = create_access_token(identity=email)
    return jsonify(
        gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token))


@blueprint.route('/api/users', methods=['POST'])  # 注册
def sign():
    data = request.get_json()
    email = data['user']['email']
    username = data['user']['username']
    password = data['user']['password']
    # user = Author(username=username, password=password, email=email)
    # user.token = create_access_token(identity=user)
    # db.session.add(user)
    # db.session.commit()
    try:
        user = Author(username=username, password=password, email=email)
        user.token = create_access_token(identity=email)
        db.session.add(user)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({
            "errors": {
                "body": [
                    "do",
                    "aliqua id"
                ]
            }}), 422, {"status": "Unprocessable Entity (WebDAV) (RFC 4918)"}
    return jsonify(
        gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token)), 201, {
               "status": "Created"}


# 获取当前用户
@blueprint.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    user_email = get_jwt_identity()
    # print(user_email)
    user = Author.query.filter_by(email=user_email).first()
    user.token = request.headers.get('Authorization').split()[1]
    return jsonify(
        gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token))


# 更新用户信息
@blueprint.route('/api/user', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.get_json()['user']
    user_email = get_jwt_identity()
    user = Author.query.filter_by(email=user_email).first()
    if 'email' in data:
        user.email = data['email']
        user.token = create_access_token(identity=user.email)
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.set_password(data['password'])
    if 'image' in data:
        user.image = data['image']
    if 'bio' in data:
        user.bio = data['bio']
    db.session.commit()
    return jsonify(
        gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token))
