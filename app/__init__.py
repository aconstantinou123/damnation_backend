import os
from flask import Flask
from .routes import main
from .db import mongo


def create_app():
    application = Flask(__name__)
    application.config['MONGO_URI'] = ('mongodb://' + os.environ['MONGODB_USERNAME'] +
        ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] +
        ':27017/' + os.environ['MONGODB_DATABASE'])

    mongo.init_app(application)

    from .routes.login import auth as auth_blueprint
    application.register_blueprint(auth_blueprint)

    from .routes.main import main as main_blueprint
    application.register_blueprint(main_blueprint)


    return application