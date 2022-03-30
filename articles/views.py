from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Article, Comment, Tag
from database import db

blueprint = Blueprint('article', __name__)


@blueprint.route('/api/articles', methods=['GET'])
@jwt_required()
def get_articles():  # 获取文章 多个查询参数
    data = request.args
    if 'tag' in data:
        articles = Article.query.filtr_by(data['tag'] in tags).all()
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
    return 'one article'


@blueprint.route('/api/articles/<slug>', methods=['PUT', 'DELETE'])  # 更新文章
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
    data = request.get_json()
    return 'article'


# 添加、获取 评论
@blueprint.route('/api/articles/<slug>/comments', methods=['POST', 'GET'])
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
@blueprint.route('/api/articles/<slug>/comments/<cid>', methods=['DELETE'])
@jwt_required()
def delete_comments(slug, cid):
    return 'delete comments'


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
