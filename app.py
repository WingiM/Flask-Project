from flask import Flask, make_response, abort, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
TITLE = 'Yandex project'


@app.route('/')
def main_page():
    return render_template('base.html', title=TITLE)


if __name__ == '__main__':
    app.run()
