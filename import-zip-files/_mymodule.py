import requests

def fetch(url, *args, **kwargs):
    return requests.get(url, *args, **kwargs)
