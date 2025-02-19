import argparse
import os
import subprocess
import sys

def stmt():
    import time
    start = time.time()
    import ddtrace
    print(time.time() - start)

def run(importtime=False, number=1000):
    dirname = os.path.dirname(__file__)
    args = [f'{dirname}/env/bin/python', __file__]
    if importtime:
        args.insert(1, '-X')
        args.insert(2, 'importtime')

    total = 0
    for _ in range(number):
        cmd = subprocess.Popen(args, env={
            'TEST_TEST': '1',
            'PYTHONPATH': dirname,
            'AWS_LAMBDA_FUNCTION_NAME': 'test',
            'DD_API_SECURITY_ENABLED': 'false',
            'DD_INSTRUMENTATION_TELEMETRY_ENABLED': 'false',
        }, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        total += float(cmd.stdout.read().decode())
        print(cmd.stderr.read().decode() or '.', end='', flush=True)
    print(f'average of {number} runs:', total / number)

if __name__ == '__main__':
    if os.environ.get('TEST_TEST'):
        stmt()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('--importtime', action='store_true')
        parser.add_argument('--number', '-n', type=int, default=1000)
        args = parser.parse_args()
        run(args.importtime, args.number)
