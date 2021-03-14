import os

from flask import Flask, abort, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from data.products import Products
from data.users import User
from forms.add_proudct import AddProductForm
from forms.login import LoginForm
from forms.register import RegisterForm
from tools.check_password import check_password

app = Flask(__name__)
db_session.global_init('db/main_db.db')
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
TITLE = 'HiTechStore'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def welcome():
    return render_template('welcome.html', title='Главная страница | ' + TITLE)


@app.route('/register', methods=["POST", "GET"])
def register():
    title = 'Регистрация | ' + TITLE
    form = RegisterForm()
    if form.validate_on_submit():
        if not check_password(form.password.data):
            return render_template('register.html', form=form, title=title,
                                   message='Пароль не соответствует требованиям')
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, title=title, message='Пароли не совпадают!')
        sess = db_session.create_session()
        if sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', form=form, title=title,
                                   message='Пользователь с таким именем уже существует')
        if sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, title=title, message='Почта уже используется')

        user = User(
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        sess.add(user)
        sess.commit()
        return redirect('/login')
    return render_template('register.html', title=title, form=form)


@app.errorhandler(403)
def forbidden(error):
    return redirect('/')


@app.route('/add_product', methods=["GET", "POST"])
@login_required
def add_product():
    if not current_user.is_admin:
        return abort(403)
    title = 'Добавление продукта | ' + TITLE
    form = AddProductForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        if sess.query(Products).filter(Products.name == form.name.data).first():
            return render_template('add_product.html', title=title, form=form,
                                   message='Товар с таким названием уже существует')

        product = Products(
            name=form.name.data,
            search_tags=form.search_tags.data,
            price=form.price.data
        )
        if image := form.image.data:
            filename = secure_filename(image.filename)
            path = os.path.join(app.root_path, 'static', 'img', 'product_images', filename)
            image.save(path)
            product.image = path
        sess.add(product)
        sess.commit()
        redirect('/catalog')
    print('не прошло')
    return render_template('add_product.html', title=title, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Авторизация | ' + TITLE
    form = LoginForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = sess.query(User).filter(
            (User.email == form.log_data.data) | (User.nickname == form.log_data.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, title=title)
    return render_template('login.html', title=title, form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
