import copy
from flask import Blueprint


class WDFTBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        self.assets = kwargs.pop('assets', [])
        self.config = kwargs.pop('config', None)
        self.jinja_filters = kwargs.pop('jinja_filters', [])
        self.jinja_globals = kwargs.pop('jinja_globals', [])
        self.url_prefix = kwargs.get('url_prefix', None)
        kwargs.setdefault('static_url_path', '/static/bp')

        super(WDFTBlueprint, self).__init__(*args, **kwargs)

    def add_url_rule(self, *args, **kwargs):
        retina = kwargs.pop('retina', False)
        if retina:
            rule = args[0]
            endpoint = args[1]
            retina_rule = rule.replace('.png', '@2x.png')
            retina_endpoint = endpoint + '@2x'
            retina_kwargs = copy.deepcopy(kwargs)
            if not 'defaults' in retina_kwargs:
                retina_kwargs['defaults'] = {}
            retina_kwargs['defaults']['size'] = '@2x'
            retina_args = (retina_rule, retina_endpoint) + args[2:]
            super(WDFTBlueprint, self).add_url_rule(*retina_args, **retina_kwargs)
        super(WDFTBlueprint, self).add_url_rule(*args, **kwargs)

    def register(self, app, options, first_registration=False):
        assets_env = app.jinja_env.assets_environment
        for asset_name, bundle in self.assets:
            assets_env.register(asset_name, bundle)
        app.config.from_object(self.config)
        for name, fn in self.jinja_filters:
            app.jinja_env.filters[name] = fn
        for name, fn in self.jinja_globals:
            app.jinja_env.globals[name] = fn

        super(WDFTBlueprint, self).register(app, options, first_registration=first_registration)

