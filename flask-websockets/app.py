import flask
import newrelic.agent
import time

app = flask.Flask(__name__)


@app.route('/ok')
def hello_world():
    return 'Hello world'




if __name__ == '__main__':
    pcolor.print_red('Registering app...')
    newrelic.agent.initialize(config_file='newrelic.ini')
    newrelic.agent.register_application()

    pcolor.print_red('Running app...')
    app.run()
