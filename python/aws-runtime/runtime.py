import flask
import requests
import time
import uuid

app = flask.Flask(__name__)

@app.route('/2020-01-01/extension/register', methods=['POST'])
def register_extension():
    response = flask.Response({})
    response.headers['Lambda-Extension-Identifier'] = 'extension'
    return response

@app.route('/2022-07-01/telemetry', methods=['PUT'])
def register_telemetry():
    return {}

@app.route('/2020-01-01/extension/event/next', methods=['GET'])
def next():
    time.sleep(1)
    return {
            'eventType': 'INVOKE',
            'deadlineMs': 10000,
            'invokedFunctionArn': 'arn:aws:lambda:sa-east-1:601427279990:function:rey-python-lambda-dev-simple',
            #'shutdownReason': ,
            'requestId': uuid.uuid4(),
    }

@app.route('/lambda/logs', methods=['GET'])
def lambda_logs():
    requests.get('http://localhost:8214/lambda/start-invocation', methods=['GET'])
    return

if __name__ == '__main__':
    app.run(debug=True, port=9001)
