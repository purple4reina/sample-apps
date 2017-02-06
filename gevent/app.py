from gevent import monkey
monkey.patch_all()

import os
import newrelic.agent
newrelic.agent.initialize(os.environ.get('NEW_RELIC_CONFIG_FILE'))
newrelic.agent.register_application(timeout=10.0)

import flask

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def a():
    return '*'

if __name__ == '__main__':
    app.run(debug=True)
