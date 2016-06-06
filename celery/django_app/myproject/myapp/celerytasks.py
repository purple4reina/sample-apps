from celery import Celery
app = Celery('celerytasks', broker='amqp://192.168.59.103:5672//')

import time

# Simple debugging wrapper
def debug_wrapper(f):
    name = f.__name__
    def wrap(*args, **kwargs):
        print_red('DEBUG: Starting function "%s"' % name)
        start = time.time()
        returned = f(*args, **kwargs)
        end = time.time()
        duration = round(end - start, 3)
        print_red('DEBUG: Function "%s" ended after %s seconds' % (name, duration))
        return returned
    return wrap

def print_red(text):
    red = '\033[1;35m'  # actually, it's purple
    stop = '\033[0m'
    print '%s%s%s' % (red, text, stop)

@app.task(name='slowly')
@debug_wrapper
def slowly(sec):
    time.sleep(sec)
