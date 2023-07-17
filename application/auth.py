# See https://flask.palletsprojects.com/en/2.3.x/tutorial/

from flask import g, Blueprint, flash, redirect, request, render_template, url_for, session

from werkzeug.security import check_password_hash, generate_password_hash

from application import db

from bson import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        database = db.get_database()
        users = database["users"]

        user_found = users.find_one({"username": username})

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if user_found is not None:
            error = 'Username already exists.'

        if error is None:
            new_user_id = users.insert_one({
                'username': username,
                'password': generate_password_hash(password)
            }).inserted_id
            print(f'New user registered. ID = {new_user_id}')
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        database = db.get_database()
        users = database["users"]

        user_found = users.find_one({"username": username})

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
        database = db.get_database()
        users = database["users"]
        g.user = users.find_one({'_id': ObjectId(session['user_id'])})


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))