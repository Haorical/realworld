from database import db
from datetime import datetime

article_favorite_user = db.Table("article_favoritor_user",
                                 db.Column("user", db.Integer, db.ForeignKey("users.id")),
                                 db.Column("article", db.Integer, db.ForeignKey("articles.id")))
tag_article = db.Table("tag_article",
                       db.Column("tag", db.Integer, db.ForeignKey("tags.id")),
                       db.Column("article", db.Integer, db.ForeignKey("articles.id")))


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(128))
    title = db.Column(db.String(128))
    description = db.Column(db.String(128))
    body = db.Column(db.String(512))
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # favorited = db.Column(db.Boolean)
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
