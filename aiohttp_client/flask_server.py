import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    req = flask.request
    print('req.headers: ', req.headers)
    return '*'


if __name__ == '__main__':
    app.run(debug=True)
