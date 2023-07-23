from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask import current_app, g
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash

import click

import datetime


def get_db():
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = PyMongo(current_app).db

    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


""" USERS """


def add_user(email, username, password):
    user_doc = {
        'email': email,
        'username': username,
        'password': password
    }

    return db.users.insert_one(user_doc)


def get_user_by_id(user_id):
    user = db.users.find_one({
        '_id': user_id
    })

    return user


def get_user_by_email(email):
    user = db.users.find_one({
        'email': email
    })

    return user


def get_user_by_username(username):
    user = db.users.find_one({
        'username': username
    })

    return user


""" POSTS """


def get_posts():
    posts = db.posts.find({}).sort('postedAt', -1)
    return posts


def get_post(post_id):
    post = db.posts.find_one(post_id)
    return post


def add_post(posted_at, body, likes, tags, creator):
    post_doc = {
        'postedAt': posted_at,
        'body': body,
        'likes': likes,
        'tags': tags,
        'creator': creator
    }
    return db.posts.insert_one(post_doc)


def update_post(post_id, body, tags):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$set': {
            'body': body,
            'tags': tags
        }
    })

    return response


def like_post(post_id, user_id):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$addToSet': {
            'likes': user_id
        }
    })

    return response


def unlike_post(post_id, user_id):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$pull': {
            'likes': user_id
        }
    })

    return response


def delete_post(post_id):
    response = db.posts.delete_one({
        '_id': post_id
    })

    return response


def init_db():
    db.users.drop()
    db.posts.drop()

    user_ids = db.users.insert_many([
        {
            'email': 'dg266@mail.com',
            'username': 'DG266',
            'password': generate_password_hash('password')
        },
        {
            'email': 'mariorossi@mail.com',
            'username': 'MarioRossi',
            'password': generate_password_hash('password')
        },
        {
            'email': 'lucaverdi@mail.com',
            'username': 'LucaVerdi',
            'password': generate_password_hash('password')
        }
    ]).inserted_ids

    db.posts.insert_many([
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Hi there, I\'m testing this feature.',
            'likes': [],
            'tags': ['NewUser', 'Test'],
            'creator': {
                'username': 'DG266'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buongiorno da Mario!',
            'likes': [],
            'tags': ['NewUser', 'Buongiorno'],
            'creator': {
                'username': 'MarioRossi'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buonasera da Luca!',
            'likes': [],
            'tags': ['NewUser', 'Buonasera'],
            'creator': {
                'username': 'LucaVerdi'
            }
        }
    ])


@click.command('init-db')
def init_db_command():
    """Clear the existing data and add example data."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)