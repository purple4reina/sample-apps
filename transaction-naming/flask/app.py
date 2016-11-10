import flask
import flask.views

app = flask.Flask(__name__)

class Home(flask.views.View):
    def dispatch_request(self):
        return '*'

app.add_url_rule('/', view_func=Home.as_view('home'))

if __name__ == '__main__':
    app.run(debug=True)
