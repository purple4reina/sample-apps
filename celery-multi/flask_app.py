import flask
import tasks

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    for _ in xrange(3):
        tasks.slowly.delay(1)
    return 'hello world'

if __name__ == '__main__':
    app.run()
