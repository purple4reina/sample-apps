import json
import os
import requests

child_url = os.environ.get('CHILD_URL', '')
root1_url = child_url + 'root1'
root2_url = child_url + 'root2'

def root1(event, context):
    return requests.get(root1_url).text

def root2(event, context):
    return requests.get(root2_url).text

def child(event, context):
    return 'ok'
