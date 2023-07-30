from flask_pymongo import PyMongo
from flask import current_app, g
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash
from ast import literal_eval
from datetime import datetime, tzinfo, timezone

import pandas as pd
import click
import datetime
import os
import json
import pymongo

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
        'password': password,
        'joinedAt': datetime.datetime.now()
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


""" POSTS AND LIKES """


# def get_posts():
#     posts = db.posts.find({}).sort('postedAt', -1)
#     return posts


def get_posts(page_num, posts_per_page):
    posts = db.posts.find({})\
        .sort('postedAt', -1)\
        .skip(page_num * posts_per_page)\
        .limit(posts_per_page)
    return posts


def get_posts_with_last_date(posts_per_page, last_date):
    posts = db.posts.find({
        'postedAt': {
            '$lt': last_date
        }
    })\
        .sort('postedAt', -1)\
        .limit(posts_per_page)

    return posts


def get_posts_by_tags(query_tags):
    query_tags = [x.lower() for x in query_tags]
    tagged_posts = db.posts.find({
        'tags_lc': {
            '$in': query_tags
        }
    }).sort('postedAt', -1)

    return tagged_posts


def get_post(post_id):
    post = db.posts.find_one(post_id)
    return post


def add_post(posted_at, body, likes, tags, creator):
    post_doc = {
        'postedAt': posted_at,
        'body': body,
        'likes': likes,
        'tags': tags,
        'tags_lc': [x.lower() for x in tags],
        'creator': creator
    }
    return db.posts.insert_one(post_doc)


def update_post(post_id, body, tags):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$set': {
            'body': body,
            'tags': tags,
            'tags_lc': [x.lower() for x in tags],
        }
    })

    return response


def delete_post(post_id):
    response = db.posts.delete_one({
        '_id': post_id
    })

    return response


def like_post(post_id, current_num_of_likes):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$set': {
            'likes': current_num_of_likes + 1
        }
    })

    return response


def unlike_post(post_id, current_num_of_likes):
    response = db.posts.update_one({
        '_id': post_id
    }, {
        '$set': {
            'likes': current_num_of_likes - 1
        }
    })

    return response


def add_like(post_id, user_id):
    like_doc = {
        'postId': post_id,
        'userId': user_id,
        'likedAt': datetime.datetime.now()
    }

    return db.likes.insert_one(like_doc)


def delete_like(post_id, user_id):
    response = db.likes.delete_one({
        'postId': post_id,
        'userId': user_id
    })

    return response


def delete_all_likes(post_id):
    response = db.likes.delete_many({
        'postId': post_id,
    })

    return response


def get_user_likes(user_id):
    user_likes = db.likes.find({
        'userId': user_id
    })

    return user_likes


def get_most_liked_last_hour(limit):
    now = datetime.datetime.now()
    last_hour_date_time = now - datetime.timedelta(hours=1)

    trending_posts = db.likes.aggregate([
        {
            '$match': {
                'likedAt': {
                    '$gte': last_hour_date_time,
                    '$lte': now
                }
            }
        }, {
            '$group': {
                '_id': '$postId',
                'totalLikes': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'totalLikes': -1
            }
        }, {
            '$limit': limit
        }, {
            '$lookup': {
                'from': 'posts',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'post'
            }
        }
    ])

    return trending_posts


def get_latest_posts():
    now = datetime.datetime.now()
    last_15min_date_time = now - datetime.timedelta(minutes=15)

    posts = db.posts.find({
        'postedAt': {
            '$gte': last_15min_date_time
        }
    }).sort('postedAt', -1)

    return posts


def get_post_number(author_username):
    num = db.posts.count_documents({
        'creator': {
            'username': author_username
        }
    })

    return num


""" DATABASE INITIALIZATION """


def init_db():
    # Delete everything
    db.users.drop()
    db.posts.drop()
    db.likes.drop()

    # Insert data
    project_path = os.getcwd()
    insert_csv_values(os.path.join(project_path, "covid19_tweets.csv"), 5000)
    insert_other_csv_values(os.path.join(project_path, "0401_UkraineCombinedTweetsDeduped_0.csv"), 5000)
    insert_example_values()

    # Create indices
    db.posts.create_index([('postedAt', pymongo.DESCENDING)])
    db.likes.create_index([('likedAt', pymongo.DESCENDING)])

    duplicates = db.users.aggregate([
        {
            '$group': {
                '_id': {
                    'username': '$username'
                },
                'dups': {
                    '$addToSet': '$_id'
                },
                'count': {
                    '$sum': 1
                }
            }
        },
        {
            '$match': {
                'count': {
                    '$gt': 1
                }
            }
        }
    ])

    for duplicate in duplicates:
        username = duplicate['_id']['username']
        print(f"Duplicate user: { username }")
        db.users.delete_many({'username': username})
        db.posts.delete_many({
            'creator': {
                'username': username
            }
        })


def insert_example_values():
    user_ids = db.users.insert_many([
        {
            'email': 'dg266@mail.com',
            'username': 'DG266',
            'password': generate_password_hash('password'),
            'joinedAt': datetime.datetime.now()
        },
        {
            'email': 'mariorossi@mail.com',
            'username': 'MarioRossi',
            'password': generate_password_hash('password'),
            'joinedAt': datetime.datetime.now()
        },
        {
            'email': 'lucaverdi@mail.com',
            'username': 'LucaVerdi',
            'password': generate_password_hash('password'),
            'joinedAt': datetime.datetime.now()
        }
    ]).inserted_ids

    post_ids = db.posts.insert_many([
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Hi there, I\'m testing this feature.',
            'likes': 1,
            'tags': ['NewUser', 'Test'],
            'tags_lc': ['newuser', 'test'],
            'creator': {
                'username': 'DG266'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buongiorno da Mario!',
            'likes': 0,
            'tags': ['NewUser', 'Buongiorno'],
            'tags_lc': ['newuser', 'buongiorno'],
            'creator': {
                'username': 'MarioRossi'
            }
        },
        {
            'postedAt': datetime.datetime.now(),
            'body': 'Buonasera da Luca!',
            'likes': 0,
            'tags': ['NewUser', 'Buonasera'],
            'tags_lc': ['newuser', 'buonasera'],
            'creator': {
                'username': 'LucaVerdi'
            }
        }
    ]).inserted_ids

    db.likes.insert_one({
        'postId': post_ids[0],
        'userId': user_ids[0],
        'likedAt': datetime.datetime.now()
    })


def insert_csv_values(csv_name, num):
    # Clean dataset
    df = pd.read_csv(csv_name)

    df = df.drop(
        columns=['user_location',
                 'user_description',
                 'user_followers',
                 'user_friends',
                 'user_favourites',
                 'user_verified',
                 'source',
                 'is_retweet']
    )

    df = df.drop_duplicates(subset=['user_name'], keep='first')

    df = df.head(num)

    # Replace 'NaN' with '[]'
    df['hashtags'] = df['hashtags'].apply(lambda d: d if isinstance(d, str) else '[]')
    df['hashtags'] = df['hashtags'].apply(literal_eval)

    # Insert values
    users_coll = db['users']
    posts_coll = db['posts']

    i = 0

    for row in df.itertuples():
        post_date = pd.to_datetime(row.date, format="%Y-%m-%d %H:%M:%S")
        join_date = pd.to_datetime(row.user_created, format="%Y-%m-%d %H:%M:%S")

        email = "email" + str(i) + "@mail.com"
        i = i + 1

        users_coll.insert_one({
            'email': email,
            'username': row.user_name,
            'password': generate_password_hash('password'),
            'joinedAt': join_date
        })

        posts_coll.insert_one({
            'postedAt': post_date,
            'body': row.text,
            'likes': 0,
            'tags': row.hashtags,
            'tags_lc': [x.lower() for x in row.hashtags],
            'creator': {
                'username': row.user_name
            }
        })


def clean_json(x):
    return json.loads(x)


def insert_other_csv_values(csv_name, num):
    # Clean dataset
    df = pd.read_csv(csv_name)
    df = df.replace({'\'': '"'}, regex=True)

    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df = df.drop(
        columns=['userid',
                 'acctdesc',
                 'location',
                 'following',
                 'followers',
                 'totaltweets',
                 'tweetid',
                 'retweetcount',
                 'language',
                 'coordinates',
                 'favorite_count',
                 'extractedts']
    )

    df = df.drop_duplicates(subset=['username'], keep='first')
    df = df.drop_duplicates(subset=['tweetcreatedts'], keep='first')

    df = df.head(num)

    df['hashtags'] = df['hashtags'].apply(clean_json)

    # Insert values
    users_coll = db['users']
    posts_coll = db['posts']

    i = num

    for row in df.itertuples():
        hashtags = []
        for json_elem in row.hashtags:
            hashtags.append(json_elem['text'])

        post_date = pd.to_datetime(row.tweetcreatedts, format="%Y-%m-%d %H:%M:%S.%f")
        join_date = pd.to_datetime(row.usercreatedts, format="%Y-%m-%d %H:%M:%S.%f")

        email = "email" + str(i) + "@mail.com"
        i = i + 1

        users_coll.insert_one({
            'email': email,
            'username': row.username,
            'password': generate_password_hash('password'),
            'joinedAt': join_date
        })

        posts_coll.insert_one({
            'postedAt': post_date,
            'body': row.text,
            'likes': 0,
            'tags': hashtags,
            'tags_lc': [x.lower() for x in hashtags],
            'creator': {
                'username': row.username
            }
        })


@click.command('init-db')
def init_db_command():
    """Clear the existing data and add example data."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)