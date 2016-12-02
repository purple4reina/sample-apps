import flask
import requests

app2 = flask.Flask('app2')

@app2.route('/')
def app2_home():
    resp = requests.get('http://localhost:5002')
    assert resp.status_code == 200
    return '*'

if __name__ == '__main__':
    app2.run(debug=True, port=5001)
