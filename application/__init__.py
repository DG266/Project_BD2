import os

from flask import Flask, flash, request, render_template, redirect, url_for
from pymongo import MongoClient

from werkzeug.security import check_password_hash, generate_password_hash


def create_app(test_config=None):
    # App creation & configuration
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # Just a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return render_template('index.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
