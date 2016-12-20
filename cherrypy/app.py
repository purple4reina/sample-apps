import cherrypy

class HelloWorld(object):
    def index(self):
        return '*'
    index.exposed = True

class Error(object):
    def index(self):
        raise cherrypy.HTTPError(400, 'Badness Happened')
    index.exposed = True

cherrypy.config.update({'engine.autoreload.on': False})
cherrypy.server.unsubscribe()
cherrypy.engine.start()

wsgiapp = cherrypy.tree.mount(Error())
