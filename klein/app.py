from klein import run, route

@route('/')
def home(request):
    return '*'

if __name__ == '__main__':
    run('localhost', 8080)
