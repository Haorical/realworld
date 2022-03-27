from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# 数据库配置
app.secret_key = '1+1=3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3307/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 连接数据库
db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(32))
    bio = db.Column(db.String(128))
    image = db.Column(db.String(256))
    following = db.Column(db.Integer, nullable=False)


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
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == 'app':
    db.drop_all()
    db.create_all()
    app.run()
