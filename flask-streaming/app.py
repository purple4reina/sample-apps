import flask

app = flask.Flask(__name__)


def countdown_iter(count):
    yield '<html><head><title>count</title></head><body>'
    while count:
        count -= 1
        yield '<div>%s</div>' % count
    yield '</body></html>'


@app.route('/')
def long_list():
    return flask.Response(countdown_iter(1000))


if __name__ == '__main__':
    app.run()
