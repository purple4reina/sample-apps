import gevent
import gevent.socket

def bg_task():
    for i in range(1,10):
        print "background task", i
        gevent.sleep(2)

def long_task():
    for i in range(1,10):
        print i
        gevent.sleep()

def application(e, sr):
    print '--------------------start--------------------'
    sr('200 OK', [('Content-Type','text/html')])
    t = gevent.spawn(long_task)
    t.join()
    yield "sleeping for 3 seconds...<br/>"
    gevent.sleep(10)
    yield "done<br>"
    yield "getting some ips...<br/>"
    urls = ['www.google.com', 'www.example.com', 'www.python.org', 'projects.unbit.it']
    jobs = [gevent.spawn(gevent.socket.gethostbyname, url) for url in urls]
    gevent.joinall(jobs, timeout=2)

    for j in jobs:
        yield "ip = %s<br/>" % j.value

    gevent.spawn(bg_task) # this task will go on after request end
