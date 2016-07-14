import flask
import requests

app1 = flask.Flask('app1')

@app1.route('/')
def app1_home():
    resp = requests.get('http://localhost:5001')
    return 'Hello App 1\n'

if __name__ == '__main__':
    app1.run(debug=True, port=5000)
