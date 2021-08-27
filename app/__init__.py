import os
from flask import Flask
from .routes import main
from .db import mongo
from flask_cors import CORS


def create_app():
    application = Flask(__name__)

    CORS(application)
    application.config['CORS_ORIGINS'] = ['localhost', 'thedamnation']

    application.config['MONGO_URI'] = ('mongodb://' + os.environ['MONGODB_USERNAME'] +
        ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] +
        ':27017/' + os.environ['MONGODB_DATABASE'])

    mongo.init_app(application)

    from .routes.auth import auth as auth_blueprint
    application.register_blueprint(auth_blueprint)

    from .routes.main import main as main_blueprint
    application.register_blueprint(main_blueprint)

    from .routes.content import content as content_blueprint
    application.register_blueprint(content_blueprint)

    return application