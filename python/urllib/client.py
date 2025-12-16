import ddtrace.auto
import urllib.request
import urllib.parse
import requests

def send_urllib(url, body):
    if isinstance(body, str):
        body = body.encode('utf-8')
    req = urllib.request.Request(url, method='GET')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Content-Length', len(body))
    req.add_header('Rey-Header', 'purple')
    resp = urllib.request.urlopen(req, body)
    return resp.read().decode()

def send_requests(url, body):
    resp = requests.get(url, body)
    resp.raise_for_status()
    return resp.text

if __name__ == '__main__':
    # does not include dd headers
    print(send_urllib('http://localhost:8000', '{"hello":"world"}'))
    # does include dd headers
    print(send_requests('http://localhost:8000', '{"hello":"world"}'))
