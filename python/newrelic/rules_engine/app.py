import flask
import requests

app = flask.Flask(__name__)

home_sites = [
    'http://example.com',
    'http://google.com',
    'http://amazon.com',
    'http://newrelic.com',
]

snow_sites = [
    'http://weather.com',
]

@app.route('/')
def home():
    for site in home_sites:
        requests.get(site)
    return ''

@app.route('/snow')
def snow():
    for site in snow_sites:
        requests.get(site)
    return ''

if __name__ == '__main__':
    app.run(debug=True)
