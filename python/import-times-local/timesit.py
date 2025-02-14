import os
import subprocess
import sys

def stmt():
    import time
    start = time.time()
    import ddtrace
    print(time.time() - start)

def run():
    dirname = os.path.dirname(__file__)
    args = [f'{dirname}/env/bin/python', __file__]
    if os.environ.get('PYTHONIMPORTTIME'):
        args.insert(1, '-X')
        args.insert(2, 'importtime')

    total, runs = 0, 1000
    for _ in range(runs):
        cmd = subprocess.Popen(args, env={
            'TEST_TEST': '1',
            'PYTHONPATH': dirname,
            'AWS_LAMBDA_FUNCTION_NAME': 'test',
            'DD_API_SECURITY_ENABLED': 'false',
            'DD_INSTRUMENTATION_TELEMETRY_ENABLED': 'false',
        }, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        total += float(cmd.stdout.read().decode())
        print(cmd.stderr.read().decode(), end='')
    print(f'average of {runs} runs:', total / runs)

if __name__ == '__main__':
    if os.environ.get('TEST_TEST'):
        stmt()
    else:
        run()
