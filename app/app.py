import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

application = Flask(__name__)

application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

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
        item = {
            'id': str(article['_id']),
            'article': article['title']
        }
        data.append(item)

    return jsonify(
        status=True,
        data=data
    )

@application.route('/article', methods=['POST'])
def createarticle():
    data = request.get_json(force=True)
    item = {
        'article': data['article']
    }
    db.article.insert_one(item)

    return jsonify(
        status=True,
        message='To-do saved successfully!'
    ), 201

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
