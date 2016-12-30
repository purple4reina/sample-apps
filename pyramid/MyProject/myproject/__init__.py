from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    # routing goes here
    config.add_route('home', '/home')
    config.add_route('hello', '/')
    config.add_route('mongo', '/mongo')

    config.scan()
    return config.make_wsgi_app()
