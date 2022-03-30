from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Article, Comment, Tag
from users.models import Author, Follow
from database import db
from exc import InvalidUsage

blueprint = Blueprint('article', __name__)


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
    if 'tag' in data:
        pass
        # articles = Article.query.filtr_by(data['tag'] in tags).all()
    # params:tag author favorited limit offset
    return 'articles'


@blueprint.route('/api/articles/feed', methods=['GET'])
@jwt_required()
def feed_article():
    # 返回关注用户创建文章 按更新顺序排列
    # limit offset
    return 'articles'


@blueprint.route('/api/articles/<slug>', methods=['GET'])
def get_article(slug):  # 获取文章
    try:
        article = Article.query.filter_by(slug=slug).first()
        author = Author.query.filter_by(id=article.authorid).first()
        tmp_favor = False
        return jsonify(gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.tags,
                                   f=article.createdAt, g=article.updatedAt, h=tmp_favor, i=article.favoritesCount,
                                   j=author.username, k=author.bio, l=author.image))
    except:
        raise InvalidUsage.article_not_found()


@blueprint.route('/api/articles/<slug>', methods=['PUT', 'DELETE'])  # 更新文章
@jwt_required()
def update_article(slug):
    if request.method == 'PUT':
        article = Article.query.filter_by(slug=slug).first()
        data = request.get_json()['article']
        if 'title' in data:
            article.title = data['title']
            article.slug = data['title']
        if 'description' in data:
            article.description = data['description']
        if 'body' in data:
            article.body = data['body']
        db.session.commit()
        author = Author.query.filter_by(id=article.authorid).first()
        tmp_favor = False
        return jsonify(
            gen_article(a=article.slug, b=article.title, c=article.description, d=article.body, e=article.tags,
                        f=article.createdAt, g=article.updatedAt, h=tmp_favor, i=article.favoritesCount,
                        j=author.username, k=author.bio, l=author.image))
    elif request.method == 'DELETE':  # 删除文章
        try:
            article = Article.query.filter_by(slug=slug).first()
            db.session.delete(article)
            db.session.commit()
        except:
            raise InvalidUsage.article_not_found()


@blueprint.route('/api/articles', methods=['POST'])
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
    data = request.get_json()['article']
    article = Article(slug=data['title'],)
    return 'article'


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
        comments = Comment.query.filter_by(slug=slug).all()
        tcm = []
        for cmt in comments:
            author = Author.query.filter_by(id=cmt.authorid).first()
            is_follow = Follow.query.filter_by(id1=current_user.id, id2=author.id).first().following
            tcm.append(gen_comments(a=cmt.id, b=cmt.createdAt, c=cmt.updatedAt, d=cmt.body, e=author.username,
                                    f=author.bio, g=author.image, h=is_follow))
        return jsonify(comments=tcm)


# 删除评论
@blueprint.route('/api/articles/<slug>/comments/<cid>', methods=['DELETE'])
@jwt_required()
def delete_comments(slug, cid):
    cm = Comment.query.filter_by(id=cid)
    db.session.delete(cm)
    db.session.commit()


# （不）喜欢文章
@blueprint.route('/api/articles/<slug>/favorite', methods=['POST', 'DELETE'])
@jwt_required()
def favorite_articles(slug):
    if request.method == 'POST':
        return 'favorite article'
    elif request.method == 'DELETE':
        return 'unfavorite article'


# 获取标签
@blueprint.route('/api/tags', methods=['GET'])
def get_tags():
    """{
        "tags": [
            "reactjs",
            "angularjs"
        ]
    }"""
    return 'tags'
