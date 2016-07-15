import flask
import time

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return flask.render_template('hello_world.html')

@app.route('/slow')
def slow_world():
    time.sleep(5)
    return 'Hello Slow World!'

@app.route('/error')
def error():
    raise Exception

if __name__ == '__main__':
    app.run(debug=True)
