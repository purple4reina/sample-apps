import flask

app2 = flask.Flask('app2')

@app2.route('/')
def app2_home():
    return 'Hello App 2'

if __name__ == '__main__':
    app2.run(debug=True, port=5001)
