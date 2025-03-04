import os

def stmt():
    import time
    start = time.time()
    # when using the layer, this is the entrypoint to all instrumentation
    import datadog_lambda.handler
    print(time.time() - start)

def _patch_extension():
    # ensure datadog_lambda thinks the extension is running
    orig_exists = os.path.exists
    def exists(file, *args, **kwargs):
        if file == '/opt/extensions/datadog-agent':
            return True
        return orig_exists(file, *args, **kwargs)
    os.path.exists = exists

def run(importtime=False, number=100):
    import subprocess

    dirname = os.path.dirname(__file__)
    args = [f'{dirname}/env/bin/python', __file__]
    if importtime:
        args.insert(1, '-X')
        args.insert(2, 'importtime')
        number = 1

    env = {
            'TEST_TEST': '1',
            'PYTHONPATH': dirname,
            'AWS_LAMBDA_FUNCTION_NAME': 'test',
            '_HANDLER': 'datadog_lambda.handler.handler',
            'DD_API_SECURITY_ENABLED': 'false',
            'DD_INSTRUMENTATION_TELEMETRY_ENABLED': 'false',
            'DD_LAMBDA_HANDLER': 'pprint.pprint',
    }

    total = 0
    for _ in range(number):
        cmd = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print(cmd.stderr.read().decode() or '.', end='', flush=True)
        total += float(cmd.stdout.read().decode())
    print(f'\naverage of {number} runs:', total / number)

if __name__ == '__main__':
    if os.environ.get('TEST_TEST'):
        _patch_extension()
        stmt()
    else:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--importtime', action='store_true')
        parser.add_argument('--number', '-n', type=int, default=1000)
        args = parser.parse_args()
        run(args.importtime, args.number)
