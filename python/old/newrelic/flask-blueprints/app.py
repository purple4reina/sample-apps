import flask

app = flask.Flask(__name__)

@app.route('/home')
@app.route('/info')
def home():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
