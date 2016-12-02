import flask
import requests

app3 = flask.Flask('app3')

@app3.route('/')
def app3_home():
    resp = requests.get('http://example.com')
    assert resp.status_code == 200
    return '*'

if __name__ == '__main__':
    app3.run(debug=True, port=5002)
