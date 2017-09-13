import time
import flask

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    req = flask.request
    print('req.headers: ', req.headers)
    return '*'


@app.route('/sleep')
def sleep():
    time.sleep(1)
    return '*'


@app.route('/redirect')
def redirect():
    return flask.redirect(flask.url_for('redirected'))


@app.route('/redirected')
def redirected():
    return flask.redirect(flask.url_for('index'))


@app.route('/raises')
def raises():
    1 / 0


@app.route('/chunked')
def chunked():
    return '*' * 1000000000


if __name__ == '__main__':
    app.run(debug=True)
