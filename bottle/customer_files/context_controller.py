from data.models.shared.consts import CSRF_TOKEN
from data.services.auth import AuthService
from lib.config import ConfigGetter


class Controller(object):

    _config = ConfigGetter()

    @property
    def _jinja_env(self):
        return self._config._jinja_env

    def global_context(self):
        return {}

    def context(self):
        return {}

    def render(self, filename, **extra_context):
        context = self.global_context()
        context.update(self.context())
        context.update(extra_context)

        session = AuthService.get_or_create_session()
        if session and session.csrf_token:
            context[CSRF_TOKEN] = session.csrf_token

        template = self._jinja_env.get_template(filename)
        return template.render(context)
