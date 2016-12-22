import flask
import newrelic.agent

app = flask.Flask(__name__)

@app.route('/')
def home():
    newrelic.agent.add_custom_parameter('hello-world', 123456)
    return '*'

if __name__ == '__main__':
    app.run(debug=True)
