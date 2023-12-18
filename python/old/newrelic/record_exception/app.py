import newrelic.agent
import sys
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    try:
        1 / 0
    except ZeroDivisionError as e:
        record()
        raise

def record():
    newrelic.agent.record_exception(*sys.exc_info())

if __name__ == '__main__':
    app.run(debug=True)
