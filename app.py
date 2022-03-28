from datetime import datetime
from hmac import compare_digest

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager
from flask_migrate import Migrate
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


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(32))
    bio = db.Column(db.String(128))
    image = db.Column(db.String(256))

    # following = db.Column(db.Integer, nullable=False)
    def check_password(self, pwd):
        return compare_digest(pwd, self.password)


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


@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['user']['email']
    password = data['user']['password']
    print(email, password)
    return jsonify(email=email, password=password)


@app.route('/api/users', methods=['POST'])
def sign():
    data = request.get_json()
    email = data['user']['email']
    username = data['user']['username']
    password = data['user']['password']
    return 'Hello World!'


if __name__ == 'app':
    db.drop_all()
    db.create_all()
    app.run()
