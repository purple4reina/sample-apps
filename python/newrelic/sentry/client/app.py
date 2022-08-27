import flask
import requests

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    requests.get('http://localhost:8000/hello/')
    return '*'

if __name__ == '__main__':
    app.run(debug=True)
