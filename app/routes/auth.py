from flask import Blueprint
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import ObjectId
from app.db import mongo
from app.authentication import encode_auth_token

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    user = mongo.db.user
    data = request.get_json(force=True)
    email = data['email']
    password = data['password']

    existing_user = user.find_one({ 'email': email})
    if not existing_user or not check_password_hash(existing_user['password'], password):
        return 'Incorrect credentials', 401

    token = encode_auth_token(str(existing_user['_id']))

    body = jsonify(
        status=True,
        data={
            'id': str(existing_user['_id']),
            'email': str(existing_user['email']),
        },
    )

    res = make_response(body, 200)
    res.headers['Authorization'] = f'Bearer {token}'

    return res


@auth.route('/signup', methods=['POST'])
def signup():
    user = mongo.db.user
    data = request.get_json(force=True)
    new_user = data['user']

    existing_user = user.find_one({ 'email': new_user['email']})
    if existing_user:
        return 'Email address already exists', 400

    _id = user.insert_one({
        'email': new_user['email'],
        'password': generate_password_hash(new_user['password'], method='sha256')
    }).inserted_id

    inserted_user = user.find_one({ '_id': ObjectId(_id) })
    
    return jsonify(
        status=True,
        data={
            'id': str(inserted_user['_id']),
            'email': str(inserted_user['email']),
        },
    ), 201

