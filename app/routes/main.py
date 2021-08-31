import os
from flask import Flask, request, jsonify
from flask_pymongo import ObjectId
from flask import Blueprint
from app.db import mongo
from app.authentication import token_required

main = Blueprint('main', __name__)

@main.route('/')
@token_required
def index(decoded_token):
    return jsonify(
        status=True,
        message=decoded_token
    )


@main.route('/article')
def article():
    mongo_query = {}
    date = request.args.get('date', None)
    query = request.args.get('query', None)
    is_main = request.args.get('main', None)
    page_number = request.args.get('pageNumber')
    print(is_main)
    if is_main and not query and not date:
        mongo_query['is_main'] = True if is_main == 'true' else False
    if date:
        mongo_query['date'] = { '$regex' :  date }
    if query:
        mongo_query['$text'] = { '$search': query }
    print(mongo_query)
    skip_amount = (int(page_number) - 1) * 9
    article = mongo.db.article
    _articles = (article.find(mongo_query)
                        .sort( [['_id', -1]] )
                        .skip(skip_amount)
                        .limit(9))
    count = article.find(mongo_query).count()
    item = {}
    data = []
    for article in _articles:
        item = {
            'id': str(article['_id']),
            'img_url': article['img_url'],
            'img_alt': article['img_alt'],
            'title': article['title'],
            'author': article['author'],
            'date': article['date'],
            'summary': article['summary'],
            'content': article['content'],
            'is_main': article['is_main'],
        }
        data.append(item)
    return jsonify(
        status=True,
        data=data,
        count=count,
    )


@main.route('/article-dates')
def article_dates():
    article = mongo.db.article
    _articles = (article.find({}, { 'date': 1 }))
    
    data = []
    for article in _articles:
        date_list = article['date'].split(' ')
        month_and_year = f'{date_list[1]} {date_list[2]}'
        data.append(month_and_year)
    unique_dates = list(set(data))
    return jsonify(
        dates=unique_dates
    )


@main.route('/article/<id>')
def article_by_id(id):
    article = mongo.db.article
    _article = article.find_one({ '_id': ObjectId(id) })
    item = {
        'id': str(_article['_id']),
        'img_url': _article['img_url'],
        'img_alt': _article['img_alt'],
        'title': _article['title'],
        'author': _article['author'],
        'date': _article['date'],
        'summary': _article['summary'],
        'content': _article['content'],
        'is_main': _article['is_main'],
    }
    return jsonify(
        status=True,
        data=item
    )


@main.route('/article', methods=['POST'])
@token_required
def createarticle(decoded_token):
    article = mongo.db.article
    data = request.get_json(force=True)
    article_to_create = data['article']

    if article_to_create['is_main']:
        article.find_one_and_update(
            {
                'is_main' : True
            },
            {
                '$set': {
                    'is_main': False
                }
            },
        )


    article.insert_one(article_to_create)

    return jsonify(
        status=True,
        message='Article saved successfully!'
    ), 201


@main.route('/article', methods=['PUT'])
@token_required
def editarticle(decoded_token):
    article = mongo.db.article
    data = request.get_json(force=True)
    article_to_update = data['article']

    if article_to_update['is_main']:
        article.find_one_and_update(
            {
                'is_main' : True
            },
            {
                '$set': {
                    'is_main': False
                }
            },
        )

    article.find_one_and_update(
        {
            '_id' : ObjectId(article_to_update['id'])
        },
        {
            '$set': article_to_update
        },
        upsert=True
    )

    return jsonify(
        status=True,
        message='Article edited successfully!'
    ), 204


@main.route('/article/<id>', methods=['DELETE'])
@token_required
def deletearticle(decoded_token, id):

    article = mongo.db.article
    article.delete_one({'_id': ObjectId(id)})

    return jsonify(
        status=True,
        message='Article deleted successfully!'
    ), 204

