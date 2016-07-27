"""
simple helper for running independent wdft apps for debug/dev
"""

from flask import Flask, redirect
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from wdft import create_app


app = create_app([])
app.run(host="0.0.0.0", port=5000, debug=True)
