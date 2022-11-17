import requests

def post_to_channel(msg, ch):
    print(f'posting to slack: message={msg}, channel={ch}')
    resp = requests.post('https://example.com', data={'msg': msg, 'ch': ch})
    resp.raise_for_status()
    return resp.ok
