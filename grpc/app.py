"""
This flask application demonstrates a memory leak caused by the agent.
"""

import gc
import flask
import grpc
import random

import route_guide_pb2
import route_guide_pb2_grpc

from newrelic.api.web_transaction import WebTransaction as WT


app = flask.Flask(__name__)


@app.route('/')
def index():
    channel = grpc.insecure_channel('localhost:50051')
    stub = route_guide_pb2_grpc.RouteGuideStub(channel)
    feature = stub.GetFeature.future(route_guide_pb2.Point(
            latitude=random.randint(-100, 100),
            longitude=random.randint(-100, 100)))
    list(feature)

    while gc.collect():
        pass

    funcs = [o for o in gc.get_objects() if isinstance(o, WT)]
    num = len(funcs)
    print('num: ', num)

    return '*'


if __name__ == '__main__':
    app.run(debug=True)
