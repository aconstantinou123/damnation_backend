import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId
application = Flask(__name__)

application.config['MONGO_URI'] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(application)
db = mongo.db

@application.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Flask MongoDB app!'
    )

@application.route('/article')
def article():
    _articles = db.article.find()

    item = {}
    data = []
    for article in _articles:
        try:
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
        except KeyError as ke:
            print(article)

    return jsonify(
        status=True,
        data=data
    )

@application.route('/article', methods=['POST'])
def createarticle():
    data = request.get_json(force=True)
    article = data['article']

    if article['is_main']:
        db.article.find_one_and_update(
            {
                'is_main' : True
            },
            {
                '$set': {
                    'is_main': False
                }
            },
        )


    db.article.insert_one(article)

    return jsonify(
        status=True,
        message='Article saved successfully!'
    ), 201

@application.route('/article', methods=['PUT'])
def editarticle():
    data = request.get_json(force=True)
    article = data['article']

    if article['is_main']:
        db.article.find_one_and_update(
            {
                'is_main' : True
            },
            {
                '$set': {
                    'is_main': False
                }
            },
        )

    db.article.find_one_and_update(
        {
            '_id' : ObjectId(article['id'])
        },
        {
            '$set': article
        },
        upsert=True
    )

    return jsonify(
        status=True,
        message='Article edited successfully!'
    ), 201

if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get('APP_DEBUG', True)
    ENVIRONMENT_PORT = os.environ.get('APP_PORT', 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
