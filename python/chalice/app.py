from chalice import Chalice, ConvertToMiddleware
from datadog_lambda.wrapper import datadog_lambda_wrapper

app = Chalice(app_name='rey-python-chalice')
app.register_middleware(ConvertToMiddleware(datadog_lambda_wrapper))

@app.route('/')
def index():
    return {'hello': 'world'}

@app.schedule('rate(1 minute)')
def run_cron(event):
    return {'hello': 'schedule'}

@app.lambda_function()
def function(params, context):
    return {'hello': 'function'}
