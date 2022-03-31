from database import db
import datetime as dt


# # 喜欢表 多对多
# user_favorite_article = db.Table("article_favoritor_user",
#                                  db.Column("user", db.Integer, db.ForeignKey("authors.id")),
#                                  db.Column("article", db.Integer, db.ForeignKey("articles.id")))
# # 标签表 多对对
# tag_article = db.Table("tag_article",
#                        db.Column("tag", db.Integer, db.ForeignKey("tags.id")),
#                        db.Column("article", db.Integer, db.ForeignKey("articles.id")))


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(128))
    title = db.Column(db.String(128))
    description = db.Column(db.String(128))
    body = db.Column(db.String(512))
    createdAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    updatedAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    # favorited = db.Column(db.Boolean)
    favoritesCount = db.Column(db.Integer, default=0)
    authorid = db.Column(db.Integer)

    # tags = db.relationship('Tag')
    def get_tags(self):
        tagids = Article2Tag.query.filter_by(article_id=self.id).all()
        li = []
        for i in tagids:
            tag = Tag.query.filter_by(id=i.tag_id).first()
            li.append(tag.tag_name)
        return li


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    updatedAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    body = db.Column(db.String(512))
    authorid = db.Column(db.Integer)
    articleid = db.Column(db.Integer)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(128))
    # article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))  # 外键


class Article2Tag(db.Model):
    __tablename__ = 'article_tags'
    article_id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, primary_key=True)


class User2Article(db.Model):
    __tablename__ = 'user_article'
    user_id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, primary_key=True)
    fav = db.Column(db.Boolean, default=False)
