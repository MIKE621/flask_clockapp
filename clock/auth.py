from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g


from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from clock import db

#Url inicial donde se montraran las demas vistas
bp = Blueprint('auth', __name__, url_prefix='/auth')

import functools

roles = ["Administrador", "Supervisor"]

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect('/auth/login')
        return view(**kwargs)
    return wrapped_view

@bp.route('register/', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':  
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        roll = request.form['roll']

        error = None
        success = None

        user = User(username, name, roll, generate_password_hash(password), 1)
        
        user_name = User.query.filter_by(username=username).first()
        if user_name == None:
            db.session.add(user)
            db.session.commit()
            success = f'El usuario {username} se registro con éxito!'
            return redirect('/auth/users')
            # flash(success)
        else:
            error = f'El usuario {username} se encuentra registrado!'
            flash(error)

    return render_template('register.html', roles=roles)

@bp.route('users/')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users =  users)

@bp.route('login/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        
        user = User.query.filter_by(username=username).first()

        #Validar datos
        if user == None:
            error = 'El usuario no existe'
        elif not check_password_hash(user.password, password):
            error = 'Contraseña incorrecta'

        #Inicio de sesion
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect('/dashboard')

        flash(error)
    return render_template('login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    print(user_id)

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@bp.route('logout/')
def logout():
    session.clear()
    return redirect('../login')

def get_user(id):
    user = User.query.get_or_404(id)
    return user

@bp.route('register_update/<int:id>', methods=('GET', 'POST'))
@login_required
def register_update(id):
    
    user = get_user(id)

    if request.method == 'POST':  
        user.username = request.form['username']
        user.name = request.form['name']
        user.password = request.form['password']
        user.roll = request.form['roll']
        # user.state = True if request.form.get('state') == 'on' else False

        db.session.commit()
        return redirect('../users')

    return render_template('register_update.html', user = user, roles=roles)

@bp.route('delete/<int:id>', methods=('GET', 'POST'))
@login_required
def delete(id):
    user = get_user(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/auth/users')