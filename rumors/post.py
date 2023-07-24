# See https://flask.palletsprojects.com/en/2.3.x/tutorial/

from flask import g, Blueprint, flash, redirect, request, render_template, url_for, jsonify, session
from werkzeug.exceptions import abort
from rumors.auth import login_required
from rumors.db import get_posts, get_posts_with_last_date, get_post, add_post, update_post, delete_post,\
    like_post, unlike_post, add_like, delete_like, get_user_likes, get_most_liked_last_hour, get_posts_by_tags
from bson import ObjectId

import datetime

import pprint


bp = Blueprint('post', __name__)


# @bp.route('/')
# def index():
#     # Get all posts (newest posts on top)
#     data = get_posts()
#
#     return render_template('post/index.html', posts=data)


@bp.route('/')
@bp.route('/index')
def index():
    max_posts_per_page = 5

    page = request.args.get('page', 0, type=int)

    user_liked_posts = get_user_liked_posts()

    # Sanitize page value
    if page < 0:
        page = 0

    # This happens when you go to the homepage
    if page == 0:
        posts_data = get_posts(page, max_posts_per_page)
        num_results = len(list(posts_data.clone()))
        print("Num. of results: " + str(num_results))

        if num_results > 0:
            session['next_page'] = 1
            session['last_date'] = posts_data[num_results - 1]['postedAt']

        return render_template('post/index.html', is_homepage=True, posts=posts_data, user_liked_posts=user_liked_posts)
    # This happens if you keep scrolling down
    else:
        posts_data = get_posts_with_last_date(max_posts_per_page, session['last_date'])
        num_results = len(list(posts_data.clone()))
        print("Num. of results: " + str(num_results))

        if num_results > 0:
            session['next_page'] = page + 1
            session['last_date'] = posts_data[num_results - 1]['postedAt']

        return render_template('post/partial_posts.html', is_homepage=True, posts=posts_data, user_liked_posts=user_liked_posts)


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
            add_post(datetime.datetime.now(), body, 0, tags, {'username': g.user['username']})

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
    post = get_post({'_id': ObjectId(id)})
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
            up_result = update_post(ObjectId(id), updated_body, updated_tags)

            return redirect(url_for('post.index'))

    return render_template('post/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post({'_id': ObjectId(id)})
    check_post(id, post)

    del_result = delete_post(ObjectId(id))

    return redirect(url_for('post.index'))


def get_user_liked_posts():
    user_liked_posts = []
    if g.user is not None:
        data = get_user_likes(g.user['_id'])
        for like_data in data:
            user_liked_posts.append(like_data['postId'])

    return user_liked_posts


@bp.route('/<id>/like', methods=('POST',))
@login_required
def like(id):
    post = get_post({'_id': ObjectId(id)})
    check_post(id, post, False)

    post_like_result = like_post(ObjectId(id), post['likes'])
    like_result = add_like(ObjectId(id), g.user['_id'])

    # return redirect(url_for('post.index'))
    resp = jsonify(success=True)
    return resp


@bp.route('/<id>/unlike', methods=('POST',))
@login_required
def unlike(id):
    post = get_post({'_id': ObjectId(id)})
    check_post(id, post, False)

    post_unlike_result = unlike_post(ObjectId(id), post['likes'])
    unlike_result = delete_like(ObjectId(id), g.user['_id'])

    # return redirect(url_for('post.index'))
    resp = jsonify(success=True)
    return resp


@bp.route('/trending', methods=('GET',))
def trending():
    limit = 10
    trending_posts = get_most_liked_last_hour(limit)
    posts = []
    for trending_post in trending_posts:
        posts.append(trending_post['post'][0])

    user_liked_posts = get_user_liked_posts()

    return render_template('post/index.html', is_homepage = False, posts=posts, user_liked_posts=user_liked_posts)


@bp.route('/search', methods=('GET',))
def search():
    query = request.args.get('query')
    print(query)

    query_tags = clean_tags(query)
    print(query_tags)

    tagged_posts = get_posts_by_tags(query_tags)

    user_liked_posts = get_user_liked_posts()

    return render_template('post/index.html', is_homepage = False, posts=tagged_posts, user_liked_posts=user_liked_posts)