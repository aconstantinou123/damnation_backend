import os
import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, make_response, request

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=21),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        elif 'damnation_token' in request.cookies:
            token = request.cookies['damnation_token']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        except:
            return jsonify({'message': 'token is invalid'})
    
        return f(decoded_token, *args, **kwargs)
    return decorator