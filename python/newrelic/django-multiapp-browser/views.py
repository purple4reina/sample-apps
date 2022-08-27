from django.http import HttpResponse
from django.views import View


_page = """
<html>
<head>
    <meta charset="utf-8">
    <title>my page title</title>
</head>
<body onload="alert('hello world!');">
    HELLO WORLD!
</body>
</html>
"""


class Index(View):
    def get(self,  request):
        return HttpResponse(_page)
