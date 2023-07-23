# See https://flask.palletsprojects.com/en/2.3.x/tutorial/

from flask import g, Blueprint, flash, redirect, request, render_template, url_for, session
from application.db import add_user, get_user_by_id, get_user_by_email, get_user_by_username
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        email_found = get_user_by_email(email)
        username_found = get_user_by_username(username)

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if email_found is not None:
            error = 'This email is already present.'

        if username_found is not None:
            error = 'This username already exists.'

        if error is None:
            new_user_id = add_user(email, username, generate_password_hash(password))
            print(f'New user registered. ID = {new_user_id}')
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_found = get_user_by_username(username)

        error = None

        if user_found is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user_found['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            logged_user_id = user_found['_id']
            session['user_id'] = str(logged_user_id)
            print(f'Successfully logged in. ID = {logged_user_id}')
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():    # runs before the view function, no matter what URL is requested
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(ObjectId(session['user_id']))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
