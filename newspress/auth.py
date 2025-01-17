''' The blueprint for authentication views '''
import functools
from flask import (
    redirect, render_template, g, flash, request, session, url_for, Blueprint,
)
from werkzeug.security import check_password_hash, generate_password_hash
from newspress.database import get_database

blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@blueprint.route('/register', methods=['POST', 'GET'])
def user_registration():
    ''' User account registration'''
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        db = get_database()
        error = None

        if not username:
            error = 'Username is required'
        elif not phone:
            error = 'Phone number is required'
        elif not fullname:
            error = 'Full Name is required'
        elif not email:
            error = 'email is required'
        elif not password:
            error = 'Password is required'
        if error is None:
            print(username, email, fullname, phone)
            try:
                db.execute(
                    "INSERT INTO user (username, phone, email, fullname, password) VALUES (?, ?, ?, ?, ?)",
                    (username, phone, email, fullname, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f'User with the {username} is registered!'
            else:
                return redirect(url_for('auth.user_login'))
        flash(error)
    return render_template('register.html')

@blueprint.route('/login', methods=['GET', 'POST'])
def user_login():
    ''' The user login view '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_database()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,),
        ).fetchone()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('login.html')

@blueprint.before_app_request
def load_logged_in_user():
    ''' Load the logged in user to the session '''
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_database()
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id, ),
        ).fetchone()
        g.user = user

@blueprint.route('/logout')
def user_logout():
    ''' User logout and clear the session '''
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    ''' Required authentication for editting, deleting, etc'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.user_login'))
        return view(**kwargs)
    return wrapped_view
