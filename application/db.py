from pymongo import MongoClient

from werkzeug.security import generate_password_hash

import click

import datetime


def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test_database']
    # print("Connected to the MongoDB database!")

    return db


def init_db():
    client = MongoClient('mongodb://localhost:27017/')
    client.drop_database('test_database')

    database = get_database()
    users_coll = database['users']
    posts_coll = database['posts']

    user_id = users_coll.insert_one({
        'username': 'DG266',
        'password': generate_password_hash('password')
    }).inserted_id

    posts_coll.insert_one({
        'postedAt': datetime.datetime.now(),
        'body': 'Hi there, I\'m testing this feature.',
        'user': {
            'name': 'DG266'
        }
    })


@click.command('init-db')
def init_db_command():
    """Clear the existing data and add example data."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)