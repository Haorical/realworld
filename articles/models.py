from database import db
import datetime as dt


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(128))
    title = db.Column(db.String(128))
    description = db.Column(db.String(128))
    body = db.Column(db.String(512))
    createdAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    updatedAt = db.Column(db.DateTime, default=dt.datetime.utcnow())
    favoritesCount = db.Column(db.Integer, default=0)
    authorid = db.Column(db.Integer)

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


class Article2Tag(db.Model):
    __tablename__ = 'article_tags'
    article_id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, primary_key=True)


class User2Article(db.Model):
    __tablename__ = 'user_article'
    user_id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, primary_key=True)
    fav = db.Column(db.Boolean, default=False)
