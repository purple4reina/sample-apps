import flask
import time

app = flask.Flask(__name__)

@app.route('/')
def home():
    time.sleep(3)
    return ''

if __name__ == '__main__':
    app.run(debug=True)
