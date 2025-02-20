import json
import os
import subprocess
import sys
import time

args = [sys.executable, os.path.join(os.path.dirname(__file__), 'timeit.py')]
git_sha = os.environ.get('GIT_SHA')

def handler(event, context):
    total = count = 0
    deadline = time.time() + context.get_remaining_time_in_millis() / 1000 - 5

    while time.time() < deadline:
        cmd = subprocess.run(args, capture_output=True)
        cmd.check_returncode()

        stdout = cmd.stdout.decode()
        print('stdout:', stdout)
        stderr = cmd.stderr.decode()
        print('stderr:', stderr)

        count += 1
        total += float(stdout)

    ave_time = total / count
    print(f'average of {count} runs:', ave_time)

    return {
            'statusCode': 200,
            'body': json.dumps({
                'average_time': ave_time,
                'count': count,
                'total_time': total,
                'git_sha': git_sha,
            }),
    }
