import os
from flask import Flask, request, jsonify
from flask_pymongo import ObjectId
from flask import Blueprint
from app.db import mongo

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Flask MongoDB app!'
    )

@main.route('/article')
def article():
    article = mongo.db.article
    _articles = article.find()

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
        data=data
    )

@main.route('/article', methods=['POST'])
def createarticle():
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
def editarticle():
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
    ), 201
