import flask
import requests

app = flask.Flask(__name__)

sites = [
    'http://example.com',
    'http://google.com',
    'http://amazon.com',
    'http://newrelic.com',
]

@app.route('/')
def home():
    for site in sites:
        requests.get(site)
    return ''

if __name__ == '__main__':
    app.run(debug=True)
