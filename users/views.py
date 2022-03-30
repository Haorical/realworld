from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Author, Follow
from database import db
from sqlalchemy.exc import IntegrityError
from exc import InvalidUsage

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


def gen_profile(username=None, bio=None, image=None, following=False):
    return {
        "profile": {
            "username": username,
            "bio": bio,
            "image": image,
            "following": following
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
    else:
        raise InvalidUsage.user_not_found()


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
    except IntegrityError:
        db.session.rollback()
        raise InvalidUsage.user_already_registered()
    # except:
    #     db.session.rollback()
    #     return jsonify({
    #         "errors": {
    #             "body": [
    #                 "do",
    #                 "aliqua id"
    #             ]
    #         }}), 422, {"status": "Unprocessable Entity (WebDAV) (RFC 4918)"}
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


@blueprint.route('/api/profiles/<username>', methods=['GET'])
@jwt_required()
def get_profile(username):  # 获取用户信息
    current_user_email = get_jwt_identity()
    current_user = Author.query.filter_by(email=current_user_email).first()
    user = Author.query.filter_by(username=username).first()
    if not user:
        raise InvalidUsage.user_not_found()
    following = Follow.query.filter_by(id1=current_user.id, id2=user.id).first()
    return jsonify(gen_profile(username=user.username, bio=user.bio, image=user.image, following=following.following))


@blueprint.route('/api/profiles/<username>/follow', methods=['POST', 'DELETE'])
@jwt_required()
def follow(username):
    if request.method == 'POST':  # 关注用户
        current_user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=current_user_email).first()
        print(current_user.id)
        user = Author.query.filter_by(username=username).first()
        if not user:
            raise InvalidUsage.user_not_found()
        try:
            f = Follow.query.filter_by(id1=current_user.id, id2=user.id).first()
            f.following = True
        except:
            f = Follow(id1=current_user.id, id2=user.id, following=True)
            db.session.add(f)
        db.session.commit()
        return jsonify(
            gen_profile(username=user.username, bio=user.bio, image=user.image, following=f.following))
    elif request.method == 'DELETE':  # 取消关注
        current_user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=current_user_email).first()
        user = Author.query.filter_by(username=username).first()
        if not user:
            raise InvalidUsage.user_not_found()
        following = Follow.query.filter_by(id1=current_user.id, id2=user.id).first()
        following.following = False
        db.session.commit()
        return jsonify(
            gen_profile(username=user.username, bio=user.bio, image=user.image, following=following.following))
