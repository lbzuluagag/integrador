import functools
import time
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)

from werkzeug.security import check_password_hash, generate_password_hash

from todo.db import get_db
from .extensions import mongo
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_collection = mongo.db.users

        error = None
        if not username:
            error = 'Username REQUIRED'
        if not password:
            error = 'Password REQUIRED'
        if mongo.db.users.find_one({'username':username}) is not None:
            error = "User already exists"

        if error is None:

            user_collection.insert({
            'username':username,
            'password':password})

            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user_collection = mongo.db.users

        user=user_collection.find_one({
            'username' : username,
            'password' : password
        })
        if user is None:
            error='Username or password incorrect'
            

        if error is None:
            
            session.clear()
            session['user_id'] = username
            return redirect(url_for('todo.index'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id == None:
        g.user = None
    else:
        
        #db, c = get_db()
        #c.execute(
        #    'select * from users where id = %s', (user_id,)
        #)
        user_collection = mongo.db.users
        g.user = user_collection.find_one()
        
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('todo.index'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('todo.index'))