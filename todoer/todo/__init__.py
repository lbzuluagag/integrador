import os

from flask import Flask
from .extensions import mongo
def create_app(config_object='todo.settings'):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='mykey'
    )
    app.config.from_object(config_object)

    mongo.init_app(app)

    from . import auth
    from . import todo

    app.register_blueprint(auth.bp)
    app.register_blueprint(todo.bp)

    @app.route('/hola')
    def hola():
        return "hola"
    
    return app
