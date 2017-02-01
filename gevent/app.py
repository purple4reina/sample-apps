from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()

import flask

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def a():
    return '*'

if __name__ == '__main__':
    app.run(debug=True)
