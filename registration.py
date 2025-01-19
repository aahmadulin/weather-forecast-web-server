from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from db import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


log = Blueprint('log', __name__)

@log.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Пользователь с таким email уже существует.', category='error')
        elif username_exists:
            flash('Пользователь с таким ником уже существует.', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают. Проверьте пароли!', category='error')
        elif len(username) < 2:
            flash('Ваш юзернейм слишком короткий', category='error')
        elif len(password1) < 6:
            flash('Ваш пароль слишком короткий', category='error')
        elif len(email) < 5:
            flash('Ваша почта слишком коротка', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            flash('Вы зарегистрированы!')
            return redirect(url_for('log.login'))
        
    
    return render_template('sign_up.html')

@log.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Вы вошли!')
            return redirect(url_for('routes.home'))
    return render_template('login.html')

@log.route('/logout')
@login_required
def logout():
    username = request.form.get('username')
    logout_user()
    flash('Вы вышли!')
    return redirect(url_for('log.login'))