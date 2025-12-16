import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return {'request.headers': dict(flask.request.headers)}

if __name__ == '__main__':
    app.run(debug=True, port=8000)
