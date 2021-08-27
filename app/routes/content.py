import os
from flask import Flask, request, jsonify
from flask_pymongo import ObjectId
from flask import Blueprint
from app.db import mongo
from app.authentication import token_required

content = Blueprint('content', __name__)

@content.route('/content')
def get_content():
    query = {}
    content = mongo.db.content
    _contents = content.find(query)
                        
    item = {}
    data = []
    try:
        for content in _contents:
            item = {
                'id': str(content['_id']),
                'type': content['type'],
                'title': content['title'],
                'content': content['content'],
            }
            data.append(item)
    except Exception:
        print(content)
    return jsonify(
        status=True,
        data=data
    )


@content.route('/content', methods=['PUT'])
@token_required
def editcontent(decoded_token):
    content = mongo.db.content
    data = request.get_json(force=True)
    content_to_update = data['content']
    print(content_to_update)
    content.find_one_and_update(
        {
            '_id' : ObjectId(content_to_update['id'])
        },
        {
            '$set': content_to_update
        },
        upsert=True
    )

    return jsonify(
        status=True,
        message='Content edited successfully!'
    ), 204