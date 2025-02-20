import os
import time

start = time.time()
import ddtrace
diff = time.time() - start
print(diff)

from metric import statsd
statsd.distribution('rey.ddtrace.import', diff, tags=[
    f'git_sha:{os.environ.get("GIT_SHA")}',
])
