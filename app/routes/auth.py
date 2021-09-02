from flask import Blueprint
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import ObjectId
from app.db import mongo
from app.authentication import encode_auth_token, token_required

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    user = mongo.db.user
    data = request.get_json(force=True)
    email = data['email']
    password = data['password']

    authenticated_user = user.find_one({ 'email': email})
    if not authenticated_user or not check_password_hash(authenticated_user['password'], password):
        return 'Incorrect credentials', 401

    token = encode_auth_token(str(authenticated_user['_id']))

    body = jsonify(
        status=True,
        user={
            'id': str(authenticated_user['_id']),
            'email': str(authenticated_user['email']),
        },
        token=token,
    )

    res = make_response(body, 200)
    res.headers['Authorization'] = f'Bearer {token}'
    res.set_cookie('token', token, httponly=True)
    return res


@auth.route('/signup', methods=['POST'])
@token_required
def signup(decoded_token):
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

@auth.route('/persist-login', methods=['POST'])
@token_required
def index(decoded_token):
    user = mongo.db.user
    _id = decoded_token['sub']

    authenticated_user = user.find_one({'_id': ObjectId(_id)})
    if not authenticated_user:
        return 'Unknown user', 401

    token = encode_auth_token(str(authenticated_user['_id']))

    body = jsonify(
        status=True,
        user={
            'id': str(authenticated_user['_id']),
            'email': str(authenticated_user['email']),
        },
        token=token,
    )

    res = make_response(body, 200)
    res.headers['Authorization'] = f'Bearer {token}'
    res.set_cookie('token', token, httponly=True)
    return res

@auth.route('/logout', methods=['POST'])
def logout():
    res = make_response('Logout successful', 204)
    res.delete_cookie(key='token') 
    return res

