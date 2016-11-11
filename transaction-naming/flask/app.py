import flask
import flask.views

import newrelic.agent

app = flask.Flask(__name__)

def _get_transaction_name():
    transaction = newrelic.agent.current_transaction()
    return getattr(transaction, 'name', None)

class Earth(flask.views.View):
    def dispatch_request(self):
        print('_get_transaction_name(): ', _get_transaction_name())
        return '*'

class Mars(flask.views.MethodView):
    def get(self):
        print('_get_transaction_name(): ', _get_transaction_name())
        return '*'

    def post(self):
        print('_get_transaction_name(): ', _get_transaction_name())
        return '*'

@app.route('/venus/')
def venus_func():
    print('_get_transaction_name(): ', _get_transaction_name())
    return '*'

app.add_url_rule('/earth/', view_func=Earth.as_view('earth'))
app.add_url_rule('/mars/', view_func=Mars.as_view('mars'))

if __name__ == '__main__':
    app.run(debug=True)
