import os
import requests
from flask import Flask, abort, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename
from data import db_session, products_resources
from data.categories import Categories
from data.products import Products
from data.users import User
from forms.add_proudct import AddProductForm
from forms.catalog_filter import CatalogFilterForm
from forms.edit_product import EditProductForm
from forms.login import LoginForm
from forms.register import RegisterForm
from tools.check_password import check_password

TITLE = 'HiTechStore'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
app.config['JSON_AS_ASCII'] = False
api = Api(app)
api.add_resource(products_resources.ProductsListResource, '/api/products')
api.add_resource(products_resources.ProductResource, '/api/products/<int:product_id>')
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init('db/main_db.db')


@app.route('/')
def welcome():
    return render_template('welcome.html', title='Главная страница | ' + TITLE)


@app.route('/catalog', methods=["GET", "POST"])
def catalog():
    form = CatalogFilterForm()
    title = 'Каталог | ' + TITLE
    url = f'{request.url_root}api/products'
    if form.validate_on_submit():
        params = {
            'price': form.price.data if form.price.data else None,
            'types': ','.join(form.types.data.split(', ')) if form.types.data else None,
            'order': form.sorting.data
        }
        url = requests.get(f'{request.url_root}catalog', params=params).url
        return redirect(url.split(request.url_root)[1])
    params = {
        'price': request.args.get('price'),
        'types': request.args.get('types'),
        'order': request.args.get('order')
    }
    products = requests.get(url, params=params).json()
    if 'error' in products:
        return abort(404)
    products = products['products']
    res_prods = []
    index = 0
    for _ in products[::3]:
        res_prods.append(products[index:index + 3])
        index += 3
    return render_template('catalog.html', title=title, products=res_prods, form=form)


@app.route('/catalog/<int:product_id>')
def load_product_page(product_id):
    url = f'{request.url_root}api/products/{product_id}'
    product = requests.get(url).json()
    if 'error' in product:
        return abort(404)
    product = product['product']
    title = product['name'] + ' | ' + TITLE
    sess = db_session.create_session()
    user = sess.query(User).get(current_user.id)
    has_product = any([i.name == product['name'] for i in user.cart])
    return render_template('product.html', title=title, product=product, has=has_product)


@app.route('/catalog/<int:product_id>/add_to_cart')
@login_required
def add_to_cart(product_id):
    sess = db_session.create_session()
    product = sess.query(Products).get(product_id)
    user = sess.query(User).get(current_user.id)
    user.cart.append(product)
    sess.commit()
    return redirect(f'/catalog/{product_id}')


@app.route('/catalog/<int:product_id>/remove_from_cart')
@login_required
def remove_from_cart(product_id):
    sess = db_session.create_session()
    product = sess.query(Products).get(product_id)
    user = sess.query(User).get(current_user.id)
    user.cart.remove(product)
    sess.commit()
    return redirect(f'/catalog/{product_id}')


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

        image = form.image.data
        filename = secure_filename(image.filename)
        path = os.path.join(app.root_path, 'static', 'img', 'product_images', filename)
        image.save(path)
        product = Products(
            name=form.name.data,
            price=form.price.data,
            about=form.about.data,
            specs=form.specs.data,
            stringed_categories=form.search_tags.data,
            image=url_for('static', filename=f'img/product_images/{filename}')
        )

        for cat in form.search_tags.data.split(', '):
            category = sess.query(Categories).filter(Categories.name == cat).first()
            if not category:
                category = Categories(
                    name=cat
                )
            sess.add(category)

            if category not in product.categories:
                product.categories.append(category)

        sess.add(product)
        sess.commit()
        redirect('/catalog')
    return render_template('add_product.html', title=title, form=form)


@app.route('/edit_product/<int:id>', methods=["GET", "POST"])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        return abort(403)
    sess = db_session.create_session()
    product = sess.query(Products).get(id)
    if not product:
        return abort(404)
    title = 'Редактирование продукта | ' + TITLE
    form = EditProductForm()
    if request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.about.data = product.about
        form.specs.data = product.specs
        form.search_tags.data = product.stringed_categories
    if form.validate_on_submit():
        if sess.query(Products).filter(Products.name == form.name.data, Products.id != id).first():
            return render_template('add_product.html', title=title, form=form,
                                   message='Товар с таким названием уже существует')
        product.name = form.name.data
        product.price = form.price.data
        product.about = form.about.data
        product.specs = form.specs.data
        product.stringed_categories = form.search_tags.data
        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            path = os.path.join(app.root_path, 'static', 'img', 'product_images', filename)
            image.save(path)
            product.image = url_for('static', filename=f'img/product_images/{filename}')

        for cat in form.search_tags.data.split(', '):
            category = sess.query(Categories).filter(Categories.name == cat).first()
            if not category:
                category = Categories(
                    name=cat
                )
            sess.add(category)

            if category not in product.categories:
                product.categories.append(category)
        sess.commit()
        return redirect('/catalog')
    return render_template('add_product.html', title=title, form=form)


@app.route('/cart')
@login_required
def user_cart():
    total = 0
    title = 'Корзина | ' + TITLE
    if not current_user.id:
        return redirect('/register')
    sess = db_session.create_session()
    user = sess.query(User).get(current_user.id)
    products = user.cart
    res_prods = []
    index = 0
    for _ in products[::3]:
        res_prods.append(products[index:index + 3])
        total += sum([prod.price for prod in products[index:index + 3]])
        index += 3
    return render_template('user_cart.html', title=title, products=res_prods, total=total)


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


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def errorhandler(error):
    return render_template('error.html', title='Ошибка | ' + TITLE, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
