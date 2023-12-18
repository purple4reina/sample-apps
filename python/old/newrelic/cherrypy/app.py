import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
print('newrelic.agent.__file__: ', newrelic.agent.__file__)

import cherrypy
print('cherrypy.__file__: ', cherrypy.__file__)

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
