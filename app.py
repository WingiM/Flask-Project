from flask import Flask, make_response, abort, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.users import User
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
db_session.global_init('db/main_db.db')
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
TITLE = 'Yandex project'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    return render_template('base.html', title=TITLE)


@app.route('/register', methods=["POST", "GET"])
def register():
    title = 'Регистрация | ' + TITLE
    form = RegisterForm()
    if form.validate_on_submit():
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
    form = LoginForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = sess.query(User).filter((User.email == form.log_data.data) | (User.nickname == form.log_data.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


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
