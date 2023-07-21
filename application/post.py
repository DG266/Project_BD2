# See https://flask.palletsprojects.com/en/2.3.x/tutorial/
from flask import g, Blueprint, flash, redirect, request, render_template, url_for, jsonify

from werkzeug.exceptions import abort

from application.auth import login_required
from application import db

from bson import ObjectId

import datetime

import pprint


bp = Blueprint('post', __name__)


@bp.route('/')
def index():
    database = db.get_database()
    posts = database["posts"]

    # Get all posts (newest posts on top)
    data = posts.find({}).sort('postedAt', -1)

    return render_template('post/index.html', posts=data)


def clean_tags(tags_content):
    tags = tags_content.split(",")
    # Remove annoying spaces in tags
    for i in range(0, len(tags)):
        tags[i] = tags[i].strip()

    return tags


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        body = request.form['body']

        tags_content = request.form['tags']
        if not tags_content:
            tags = []
        else:
            tags = clean_tags(tags_content)

        error = None

        if not body:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            database = db.get_database()
            posts_coll = database['posts']
            posts_coll.insert_one({
                'postedAt': datetime.datetime.now(),
                'body': body,
                'likes': [],
                'tags': tags,
                'creator': {
                    'username': g.user['username']
                }
            })

            return redirect(url_for('post.index'))

    return render_template('post/create.html')


# Checks if the selected post exists AND (if check_author=True) the current user is the author of the post
def check_post(id_string, post, check_author=True):
    if post is None:
        abort(404, f"The post with ObjectId {id_string} doesn't exist.")

    if check_author and post['creator']['username'] != g.user['username']:
        abort(403)


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    database = db.get_database()
    posts_coll = database['posts']
    post = posts_coll.find_one({'_id': ObjectId(id)})
    check_post(id, post)

    if request.method == 'POST':
        updated_body = request.form['body']

        updated_tags_content = request.form['tags']
        if (not updated_tags_content) or (updated_tags_content.strip() == ""):
            updated_tags = []
        else:
            updated_tags = clean_tags(updated_tags_content)

        error = None

        if not updated_body:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            posts_coll.update_one({
                '_id': ObjectId(id)
            }, {
                '$set': {
                    'body': updated_body,
                    'tags': updated_tags
                }
            }, upsert=False)

            return redirect(url_for('post.index'))

    return render_template('post/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    database = db.get_database()
    posts_coll = database['posts']
    post = posts_coll.find_one({'_id': ObjectId(id)})
    check_post(id, post)

    posts_coll.delete_one({'_id': ObjectId(id)})

    return redirect(url_for('post.index'))


@bp.route('/<id>/like', methods=('POST',))
@login_required
def like(id):
    database = db.get_database()
    posts_coll = database['posts']
    post = posts_coll.find_one({'_id': ObjectId(id)})
    check_post(id, post, False)

    posts_coll.update_one({
        '_id': ObjectId(id)
    }, {
        '$addToSet': {
            'likes': g.user["_id"]
        }
    }, upsert=False)

    # return redirect(url_for('post.index'))
    resp = jsonify(success=True)
    return resp


@bp.route('/<id>/unlike', methods=('POST',))
@login_required
def unlike(id):
    database = db.get_database()
    posts_coll = database['posts']
    post = posts_coll.find_one({'_id': ObjectId(id)})
    check_post(id, post, False)

    posts_coll.update_one({
        '_id': ObjectId(id)
    }, {
        '$pull': {
            'likes': g.user["_id"]
        }
    }, upsert=False)

    # return redirect(url_for('post.index'))
    resp = jsonify(success=True)
    return resp

