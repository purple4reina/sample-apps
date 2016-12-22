import cherrypy

class HelloWorld(object):
    def index(self):
        return '*'
    index.exposed = True

class Error(object):
    def index(self):
        raise cherrypy.HTTPError(400, 'Badness Happened')
    index.exposed = True

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld())
else:
    cherrypy.config.update({'engine.autoreload.on': False})
    cherrypy.server.unsubscribe()
    cherrypy.engine.start()

    #wsgiapp = cherrypy.tree.mount(Error())
    wsgiapp = cherrypy.tree.mount(HelloWorld())
