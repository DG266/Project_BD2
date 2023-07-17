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

    user_ids = users_coll.insert_many([
        {
            'username': 'DG266',
            'password': generate_password_hash('password')
        },
        {
            'username': 'MarioRossi',
            'password': generate_password_hash('password')
        },
        {
            'username': 'LucaVerdi',
            'password': generate_password_hash('password')
        }
    ]).inserted_ids

    posts_coll.insert_many([
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Hi there, I\'m testing this feature.',
            'creator': {
                'username': 'DG266'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buongiorno da Mario!',
            'creator': {
                'username': 'MarioRossi'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buonasera da Luca!',
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