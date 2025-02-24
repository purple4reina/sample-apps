import falcon

class ThingsResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = '*'

app = falcon.API()
things = ThingsResource()
app.add_route('/', things)
