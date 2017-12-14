from piston.handler import BaseHandler
from app.models import Cat


class CatHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Cat

    def read(self, request):
        return Cat.objects.all()
