import newrelic.agent
from flask import Flask, got_request_exception
from flask_restful import Resource, Api
from werkzeug.exceptions import BadGateway


app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        raise BadGateway('oooooops')
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/')


@got_request_exception.connect_via(app)
def handle_exceptions(app, exception):
    newrelic.agent.record_exception()


if __name__ == '__main__':
    app.run(debug=True)
