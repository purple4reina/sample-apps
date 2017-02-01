from gevent import monkey; monkey.patch_all()

import flask

app = flask.Flask(__name__)

@app.route('/')
def a():
    return '*'

if __name__ == '__main__':
    app.run(debug=True)
