import cherrypy

class HelloWorld(object):
    def index(self):
        return '*'
    index.exposed = True

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld())
else:
    cherrypy.config.update({'engine.autoreload.on': False})
    cherrypy.server.unsubscribe()
    cherrypy.engine.start()

    wsgiapp = cherrypy.tree.mount(HelloWorld())
