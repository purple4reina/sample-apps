from twisted.web import server, resource
from twisted.internet import reactor, endpoints


class Index(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return '*'


if __name__ == '__main__':
    endpoints.serverFromString(reactor,
            'tcp:8080').listen(server.Site(Index()))
    reactor.run()
