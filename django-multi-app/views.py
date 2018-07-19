from django.http import HttpResponse
from django.views import View


HTML = """
<html>
<head>
    <meta charset="utf-8">
    <title>title</title>
</head>
<body>
    %s
</body>
</html>
"""


class Index(View):
    def get(self,  request):
        return HttpResponse('*')


class Power(View):
    def get(self,  request):
        return HttpResponse(HTML % 'power')


class Touch(View):
    def get(self,  request):
        return HttpResponse(HTML % 'touch')
