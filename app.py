from datetime import datetime
from hmac import compare_digest
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# 数据库配置
app.secret_key = '1+1=3'
app.config["JWT_SECRET_KEY"] = "1+1=4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3307/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 连接数据库
db = SQLAlchemy(app)
jwt = JWTManager(app)


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


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(128))
    title = db.Column(db.String(128))
    description = db.Column(db.String(128))
    body = db.Column(db.String(512))
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    favorited = db.Column(db.Boolean)
    favoritesCount = db.Column(db.Integer)
    authorid = db.Column(db.Integer)
    tags = db.relationship('Tag')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    body = db.Column(db.String(512))
    authorid = db.Column(db.Integer)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(16))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))  # 外键


class Follow(db.Model):
    __tablename__ = 'follows'
    id1 = db.Column(db.Integer, primary_key=True)
    id2 = db.Column(db.Integer, primary_key=True)
    following = db.Column(db.Boolean, default=False)


"""
{
  "user":{
    "email": "jake@jake.jake",
    "password": "jakejake"
  }
}
"""


@app.route('/api/users/login', methods=['POST'])  # 认证
def login():
    data = request.get_json()
    email = data['user']['email']
    password = data['user']['password']
    user = Author.query.filter_by(email=email).first()
    if user is not None and user.check_password(password):
        user.token = create_access_token(identity=email, fresh=True)
    return jsonify(
        gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token))


@app.route('/api/users', methods=['POST'])  # 注册
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


@app.route('/api/user', methods=['GET', 'PUT'])
@jwt_required()
def get_user():
    if request.method == 'GET':  # 获取当前用户
        user_email = get_jwt_identity()
        # print(user_email)
        user = Author.query.filter_by(email=user_email).first()
        user.token = request.headers.get('Authorization').split()[1]
        return jsonify(
            gen_user(username=user.username, email=user.email, bio=user.bio, image=user.image, token=user.token))
    elif request.method == 'PUT':  # 更新用户信息
        data = request.get_json()
        # email username password image bio
        return 'update user'


@app.route('/api/profiles/<username>', methods=['GET'])
@jwt_required()
def get_profile(username):  # 获取用户信息
    """{
  "profile": {
    "username": "jake",
    "bio": "I work at statefarm",
    "image": "https://api.realworld.io/images/smiley-cyrus.jpg",
    "following": false
  }
}"""
    return 'user'


@app.route('/api/profiles/<username>/follow', methods=['POST', 'DELETE'])
@jwt_required()
def follow(username):
    """{
      "profile": {
        "username": "jake",
        "bio": "I work at statefarm",
        "image": "https://api.realworld.io/images/smiley-cyrus.jpg",
        "following": false
      }
    }"""
    if request.method == 'POST':  # 关注用户
        return 'follow'
    elif request.method == 'DELETE':  # 取消关注
        return 'unfollow'


@app.route('/api/articles', methods=['GET'])
@jwt_required()
def get_articles():  # 获取文章 多个查询参数
    # params:tag author favorited limit offset
    return 'articles'


@app.route('/api/articles/feed', methods=['GET'])
@jwt_required()
def feed_article():
    # 返回关注用户创建文章 按更新顺序排列
    # limit offset
    return 'articles'


@app.route('/api/articles/<slug>', methods=['GET'])
def get_article(slug):  # 获取文章
    return 'one article'


@app.route('/api/articles/<slug>', methods=['PUT', 'DELETE'])  # 更新文章
@jwt_required()
def update_article():
    if request.method == 'PUT':
        """{
            "article": {
                "title": "Did you train your dragon?"
            }
            title description body
            slug 自动会更新
        }"""
        data = request.get_json()
        return 'update article'
    elif request.method == 'DELETE':
        return 'delete article'


@app.route('/api/articles', methods=['POST'])
@jwt_required()
def creat_article():  # 创建文章
    """{
        "article": {
            "title": "How to train your dragon",
            "description": "Ever wonder how?",
            "body": "You have to believe",
            "tagList": ["reactjs", "angularjs", "dragons"]  可选参数
        }
    }"""
    data = request.get_json()
    return 'article'


# 添加、获取 评论
@app.route('/api/articles/<slug>/comments', methods=['POST', 'GET'])
@jwt_required()
def op_comments(slug):
    if request.method == 'POST':
        data = request.get_json()
        """{
            "comment": {
                "body": "His name was my name too."
            }
        }"""
        return 'add comments'
    elif request.method == 'GET':  # 获取评论
        """{
            "comments": [{
                "id": 1,
                "createdAt": "2016-02-18T03:22:56.637Z",
                "updatedAt": "2016-02-18T03:22:56.637Z",
                "body": "It takes a Jacobian",
                "author": {
                    "username": "jake",
                    "bio": "I work at statefarm",
                    "image": "https://i.stack.imgur.com/xHWG8.jpg",
                    "following": false
                }
            }]
        }"""
        return 'comments'


# 删除评论
@app.route('/api/articles/<slug>/comments/<cid>', methods=['DELETE'])
@jwt_required()
def delete_comments(slug, cid):
    return 'delete comments'


# （不）喜欢文章
@app.route('/api/articles/<slug>/favorite', methods=['POST', 'DELETE'])
@jwt_required()
def favorite_articles(slug):
    if request.method == 'POST':
        return 'favorite article'
    elif request.method == 'DELETE':
        return 'unfavorite article'


# 获取标签
@app.route('/api/tags', methods=['GET'])
def get_tags():
    """{
        "tags": [
            "reactjs",
            "angularjs"
        ]
    }"""
    return 'tags'


if __name__ == 'app':
    db.drop_all()
    db.create_all()
    app.run()
