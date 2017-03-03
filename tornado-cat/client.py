import flask
import requests

app = flask.Flask(__name__)

def newrelic_in_headers(headers):
    for header in headers.keys():
        if header.lower() == 'x-newrelic-app-data':
            return True
    return False

@app.route('/')
def index():
    try:
        resp = requests.get('http://localhost:8888')
    except:
        return '!'

    if newrelic_in_headers(resp.headers):
        return '+'
    else:
        return '-'

if __name__ == '__main__':
    app.run(debug=True)
