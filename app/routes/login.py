from flask import Blueprint
from app.db import mongo

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return 'Login'