import datetime

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from .models import Article, Comment, Tag, Article2Tag, User2Article
from users.models import Author, Follow
from database import db
from exc import InvalidUsage

blueprint = Blueprint('article', __name__)


def check_fav(us, ar):
    f = User2Article.query.filter_by(user_id=us, article_id=ar).first()
    if not f:
        return False
    return f.fav


def gen_article(a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=False, i=0, j=None, k=None, l=None, m=False):
    return {
        "article": {
            "slug": a,
            "title": b,
            "description": c,
            "body": d,
            "tagList": e,
            "createdAt": f,
            "updatedAt": g,
            "favorited": h,
            "favoritesCount": i,
            "author": {
                "username": j,
                "bio": k,
                "image": l,
                "following": m
            }
        }
    }


@blueprint.route('/api/articles', methods=['GET'])
@jwt_required()
def get_articles():  # 获取文章 多个查询参数
    data = request.args
    li = []
    if 'tag' in data:
        tag = Tag.query.filter_by(tag_name=data['tag']).first()
        if not tag:
            raise InvalidUsage.unknown_error()
        articleids = Article2Tag.query.filter_by(tag_id=tag.id).all()
        for id in articleids:
            article = Article.query.filter_by(id=id.article_id).first()
            author = Author.query.filter_by(id=article.authorid).first()
            li.append(gen_article(a=article.slug, b=article.title, c=article.description, d=article.body,
                                  e=article.get_tags(),
                                  f=article.createdAt, g=article.updatedAt, h=check_fav(author.id, article.id),
                                  i=article.favoritesCount,
                                  j=author.username, k=author.bio, l=author.image)['article'])
    if 'author' in data:
        author = Author.query.filter_by(username=data['author']).first()
        articles = Article.query.filter_by(authorid=author.id).all()
        for article in articles:
            li.append(gen_article(a=article.slug, b=article.title, c=article.description, d=article.body,
                                  e=article.get_tags(),
                                  f=article.createdAt, g=article.updatedAt, h=check_fav(author.id, article.id),
                                  i=article.favoritesCount,
                                  j=author.username, k=author.bio, l=author.image)['article'])
    if 'favorited' in data:
        user = Author.query.filter_by(username=data['favorited']).first()
        articleids = User2Article.query.filter_by(user_id=user.id, fav=True).all()
        article = Article.query.filter_by(id=id.article_id).first()
        author = Author.query.filter_by(id=article.authorid).first()
        li.append(gen_article(a=article.slug, b=article.title, c=article.description, d=article.body,
                              e=article.get_tags(),
                              f=article.createdAt, g=article.updatedAt, h=check_fav(author.id, article.id),
                              i=article.favoritesCount,
                              j=author.username, k=author.bio, l=author.image)['article'])
    li = list(set(li))
    limit = 20
    offset = 0
    if 'limit' in data:
        limit = int(data['limit'])
    if 'offset' in data:
        offset = int(data['offset'])
    ti = []
    cnt = 0
    r = min(offset + limit, len(li))
    for i in range(offset, r):
        ti.append(li[i])
        cnt += 1
    return jsonify(articles=ti, articlesCount=cnt)


@blueprint.route('/api/articles/feed', methods=['GET'])
@jwt_required()
def feed_article():
    # 返回关注用户创建文章 按更新顺序排列
    # limit offset
    data = request.args
    limit = 20
    offset = 0
    if 'limit' in data:
        limit = int(data['limit'])
    if 'offset' in data:
        offset = int(data['offset'])
    user_em = get_jwt_identity()
    user = Author.query.filter_by(email=user_em).first()
    authors = Follow.query.filter_by(id1=user.id).all()
    li = []
    for i in authors:
        articles = Article.query.filter_by(authorid=i.id2).order_by(desc(Article.updatedAt)).all()
        author = Author.query.filter_by(id=i.id2).first()
        for article in articles:
            li.append(gen_article(a=article.slug, b=article.title, c=article.description, d=article.body,
                                  e=article.get_tags(),
                                  f=article.createdAt, g=article.updatedAt, h=check_fav(author.id, article.id),
                                  i=article.favoritesCount,
                                  j=author.username, k=author.bio, l=author.image)['article'])
    ti = []
    cnt = 0
    r = min(offset + limit, len(li))
    for i in range(offset, r):
        ti.append(li[i])
        cnt += 1
    return jsonify(articles=ti, articlesCount=cnt)


@blueprint.route('/api/articles/<slug>', methods=['GET'])
def get_article(slug):  # 获取文章
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        raise InvalidUsage.article_not_found()
    author = Author.query.filter_by(id=article.authorid).first()
    return jsonify(
        gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.get_tags(),
                    f=article.createdAt, g=article.updatedAt, h=False, i=article.favoritesCount,
                    j=author.username, k=author.bio, l=author.image))


@blueprint.route('/api/articles/<slug>', methods=['PUT', 'DELETE'])  # 更新文章
@jwt_required()
def update_article(slug):
    if request.method == 'PUT':
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            raise InvalidUsage.article_not_found()
        data = request.get_json()['article']
        if 'title' in data:
            article.title = data['title']
            article.slug = data['title']
        if 'description' in data:
            article.description = data['description']
        if 'body' in data:
            article.body = data['body']
        article.updatedAt = datetime.datetime.utcnow()
        db.session.commit()
        author = Author.query.filter_by(id=article.authorid).first()
        return jsonify(
            gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.get_tags(),
                        f=article.createdAt, g=article.updatedAt, h=check_fav(author.id, article.id),
                        i=article.favoritesCount,
                        j=author.username, k=author.bio, l=author.image))
    elif request.method == 'DELETE':  # 删除文章
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            raise InvalidUsage.article_not_found()
        db.session.delete(article)
        db.session.commit()
        return jsonify(None)


@blueprint.route('/api/articles', methods=['POST'])
@jwt_required()
def creat_article():  # 创建文章
    author_em = get_jwt_identity()
    author = Author.query.filter_by(email=author_em).first()
    data = request.get_json()['article']
    article = Article(slug=data['title'], title=data['title'], description=data['description'], body=data['body'],
                      authorid=author.id)
    db.session.add(article)
    db.session.commit()
    if 'tagList' in data:
        for i in data['tagList']:
            tag = Tag.query.filter_by(tag_name=i).first()
            if not tag:
                tag = Tag(tag_name=i)
                db.session.add(tag)
                db.session.commit()
            a2t = Article2Tag(article_id=article.id, tag_id=tag.id)
            db.session.add(a2t)
            db.session.commit()
    print(article.get_tags())
    return jsonify(
        gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.get_tags(),
                    f=article.createdAt, g=article.updatedAt, h=False, i=article.favoritesCount,
                    j=author.username, k=author.bio, l=author.image))


def gen_comments(a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=False):
    return {
        "comment": {
            "id": a,
            "createdAt": b,
            "updatedAt": c,
            "body": d,
            "author": {
                "username": e,
                "bio": f,
                "image": g,
                "following": h
            }
        }
    }


# 添加、获取 评论
@blueprint.route('/api/articles/<slug>/comments', methods=['POST', 'GET'])
@jwt_required()
def op_comments(slug):
    if request.method == 'POST':  # 添加评论
        data = request.get_json()['comment']['body']
        user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=user_email).first()
        article = Article.query.filter_by(slug=slug).first()
        cmt = Comment(body=data, authorid=current_user.id, articleid=article.id)
        db.session.add(cmt)
        db.session.commit()
        return jsonify(gen_comments(a=cmt.id, b=cmt.createdAt, c=cmt.updatedAt, d=cmt.body, e=current_user.username,
                                    f=current_user.bio, g=current_user.image))
    elif request.method == 'GET':  # 获取评论
        user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=user_email).first()
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            raise InvalidUsage.article_not_found()
        comments = Comment.query.filter_by(articleid=article.id).all()
        tcm = []
        for cmt in comments:
            author = Author.query.filter_by(id=cmt.authorid).first()
            tcm.append(gen_comments(a=cmt.id, b=cmt.createdAt, c=cmt.updatedAt, d=cmt.body, e=author.username,
                                    f=author.bio, g=author.image, h=current_user.check_follow(author.id)))
        return jsonify(comments=tcm)


# 删除评论
@blueprint.route('/api/articles/<slug>/comments/<cid>', methods=['DELETE'])
@jwt_required()
def delete_comments(slug, cid):
    cm = Comment.query.filter_by(id=cid).first()
    if not cm:
        raise InvalidUsage.comment_not_owned()
    db.session.delete(cm)
    db.session.commit()
    return jsonify(None)


# （不）喜欢文章
@blueprint.route('/api/articles/<slug>/favorite', methods=['POST', 'DELETE'])
@jwt_required()
def favorite_articles(slug):
    if request.method == 'POST':
        current_user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=current_user_email).first()
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            raise InvalidUsage.article_not_found()
        article.favoritesCount += 1
        author = Author.query.filter_by(id=article.authorid).first()
        try:
            f = User2Article.query.filter_by(user_id=current_user.id, article_id=article.id).first()
            f.fav = True
        except:
            f = User2Article(user_id=current_user.id, article_id=article.id)
            db.session.add(f)
        db.session.commit()
        return jsonify(
            gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.get_tags(),
                        f=article.createdAt, g=article.updatedAt, h=True, i=article.favoritesCount,
                        j=author.username, k=author.bio, l=author.image, m=current_user.check_follow(author.id)))
    elif request.method == 'DELETE':
        current_user_email = get_jwt_identity()
        current_user = Author.query.filter_by(email=current_user_email).first()
        article = Article.query.filter_by(slug=slug).first()
        if not article:
            raise InvalidUsage.article_not_found()
        article.favoritesCount -= 1
        author = Author.query.filter_by(id=article.authorid).first()
        f = User2Article.query.filter_by(user_id=current_user.id, article_id=article.id).first()
        f.fav = False
        db.session.commit()
        return jsonify(
            gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.get_tags(),
                        f=article.createdAt, g=article.updatedAt, h=False, i=article.favoritesCount,
                        j=author.username, k=author.bio, l=author.image, m=current_user.check_follow(author.id)))


# 获取标签
@blueprint.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.filter_by().all()
    li = []
    for i in tags:
        li.append(i.tag_name)
    return jsonify(tags=li)
