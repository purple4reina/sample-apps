import flask


print
blueprint = flask.Blueprint('blueprint', __name__)

@blueprint.route('/')
def home():
    return 'Hello'

@blueprint.route('/')
def yohome():
    return 'yoHello'

app = flask.Flask(__name__)

app.register_blueprint(blueprint)

print 'app.url_map: ', app.url_map


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
