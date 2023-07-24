from flask import Flask


def create_app(test_config=None):
    # App creation & configuration
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    app.config["MONGO_URI"] = "mongodb://localhost:27017/test-database"

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import post
    app.register_blueprint(post.bp)
    app.add_url_rule('/', endpoint='index')

    return app
