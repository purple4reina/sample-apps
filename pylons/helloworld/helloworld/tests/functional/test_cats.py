from helloworld.tests import *

class TestCatsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='cats', action='index'))
        # Test response...
