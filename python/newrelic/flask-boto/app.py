import flask
import boto3

app = flask.Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!\n'

@app.route('/boto')
def rawr():
    return boto()


def boto():
    s3 = boto3.resource('s3')
    for o in s3.Bucket('nr-downloads-main').objects.all():
        pass
    return 'Hello S3\n'


@app.route('/bing')
def moar():
    return boto()



if __name__ == '__main__':
    app.run(debug=True)
