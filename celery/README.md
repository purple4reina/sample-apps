# Celery App

## Isolating celery multi bugs

Using rabbitmq running in a docker container with `docker run -d --net=host -p 5672:5672 rabbitmq`

+ `celery worker` without docker or agent using `python call_tasks.py`
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start worker with `celery worker -A tasks --concurrency=1 -l info`, this leaves the terminal with a streaming of the celery logs
  - I see "slowly..." printed to the terminal and my other DEBUG statements printed to the terminal of the worker.

+ `celery multi` without docker or agent using `python call_tasks.py`
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start celery multi with `celery multi start node1 -A tasks --concurrency=1 -l info`, then must `tail -f node1.log` to stream the logs. Stop it with `celery multi stop node1`
  - I see "slowly..." printed to the terminal and my other DEBUG statements printed to the terminal of the worker.
  - Must stop the node with `celery multi stop node1`

+ running `celery worker` inside a docker container, no agent, then calling `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start the worker in a container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery celery worker -A tasks --concurrency=1 -l info`
  - I see "slowly..." printed to the terminal and my other DEBUG statements printed to the terminal of the worker container.

+ running `celery multi` inside a docker container, no agent, then calling `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start the celery multi container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery ./start_celery_multi.sh` (this will start celery multi with the same command as above and then tail the log file)
  - I see "slowly..." printed to the terminal and my other DEBUG statements printed to the terminal of the worker container.

+ Change the `celery worker` commands to use ./start_celery_worker.sh
  - Tested with running inside docker container, works as before
  - Start worker in container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery ./start_celery_worker.sh`

+ running `celery worker` without docker but with agent, then running `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Make sure that the correct newrelic-admin binary is being used by doing `source env/bin/activate`, I found that a `which newrelic-admin` didn't necessarily show the one that was actually being used, for some reason it kept using the one at `/usr/local/bin/newrelic-admin`
  - Start the celery worker with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery worker -A tasks --concurrency=1 -l info`
  - What is in the nrlog.log is printed to the stdout of the celery worker command, the audit.log is not there though

+ running `celery worker` inside a docker container, with agent, then calling `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start the celery worker in a container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true -e NEW_RELIC_CONFIG_FILE=newrelic.ini celery newrelic-admin run-program celery worker -A tasks --concurrency=1 -l info`
  - The nrlog.log is printed to the stdout of the celery worker command, the audit.log is not there though

+ running `celery multi` without docker, with agent, then calling `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start celery multi with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery multi start node1 -A tasks --concurrency=1 -l info`
  - Must stop the node with `celery multi stop node1`, confirm it is stopped with `ps aux | grep celery`, may need to do a kill that way

+ running `celery multi` inside a docker container, with agent, then calling `python call_tasks.py` locally
  - tasks.py needs `app = Celery('tasks', broker='amqp://192.168.59.103:5672//')`
  - Start the celery worker in a container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true -e NEW_RELIC_CONFIG_FILE=newrelic.ini celery newrelic-admin run-program ./start_celery_multi.sh`
  - I see in the audit.log (by doing a docker exec on the container and tailing audit.log) that the harvest is happening as expected and the transactions are being sent to the collector
    * There is an entry for 'method': 'analytic_event_data' that includes in the DATA the three times the tasks.sleepy was called

+ running `init.d/celeryd start` inside a docker container, without agent, then calling `python call_tasks.py` locally
  - Start the celeryd in container with `docker run -it -v $PWD:/data --net=host celery ./init.d/celeryd start`
  - Must set `CELERY_APP` env var
  - Changes to the init.d/celeryd script (from what is found in github) are seen in [init.d/celeryd](init.d/celeryd)

+ running `celery multi` locally, with agent, but with a higher concurrency
  - Start celery multi with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery multi start node1 -A tasks --concurrency=3 -l info`
  - The audit.log shows three different payloads going out about the celery commands, one for each of the workers that were created

  + running `celery multi` locally, with agent, with more workers by name
    - Start celery multi with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery multi start node1 node2 node3 -A tasks --concurrency=1 -l info`
    - The audit.log shows three different payloads going out about the celery commands, one for each of the workers that were created

+ running `celery multi` in a container, but not using the NEW_RELIC env var
  - Start the celery worker in a container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery newrelic-admin run-program ./start_celery_multi.sh`
  - It is not reporting, nothing is showing up in the audit.log nor in the docker container's stdout, this is expected

+ running `celery multi` in a container, putting the NEW_RELIC env var in the ./start_celery_multi.sh script
  - Edit the start_celery_multi.sh script to include the env var
  - Start the celery worker in a container with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery newrelic-admin run-program ./start_celery_multi.sh`

+ running `celery multi` in container, changing the name of the ini file
  - Works, seeing the payloads in the audit.log

+ running `celery multi` in container, putting the `newrelic-admin` part of the command inside the start_celery_multi.sh file
  - Works, seeing the payloads in the audit.log file

+ running `celery multi` in a container, with agent, and using flask that is running locally
  - Still seems to be working
  - Started the container with no env vars, the newrelic-admin command and the env var is in the ./start_celery_multi.sh file

+ Consider env vars: Which env vars are existing when the celery worker command is called from the celery multi command? How do I know?
  - From the subprocess.Popen docs:
  - *If env is not None, it must be a mapping that defines the environment variables for the new process; these are used instead of inheriting the current process’ environment, which is the default behavior.*

+ Consider different celery versions
  - Seems like all is good with v3.1.23
  - Even the v2's all have the env set correctly to Popen

+ Consider Django with Celery -- it looks like users are doing stuff with `./manage.py celery blah`

+ Consider Django with Celery -- it looks like users are doing stuff with `./manage.py celery blah`
  - Just installing django (via pip), then starting project and apps with the cmdline tool, `./manage.py celery` command not found
  - I created a view that will call the slowly task (I had to make a copy of the tasks file and put it in the app)
  - `celery worker` without agent:
    * Started `celery worker` in container without agent with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery celery worker -A django_app.myproject.myapp.celerytasks --concurrency=1 -l info` from the root dir
    * Started django runserver from the django_app/myproject dir with `./manage.py runserver`
  - `celery worker` with agent:
    * Started `celery worker` in container with agent with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true -e NEW_RELIC_CONFIG_FILE=worker-newrelic.ini celery newrelic-admin run-program celery worker -A django_app.myproject.myapp.celerytasks --concurrency=1 -l info` from the root dir
    * Started django runserver without agent with `./manage.py runserver` from the django_app/myproject dir
    * The UI shows that the transactions are reporting as expected
  - `celery multi` with agent:
    * Started `celery multi` in container without agent with `docker run -it -v $PWD:/data --net=host -e C_FORCE_ROOT=true celery ./start_celery_multi.sh django_app.myproject.myapp.celerytasks`
    * The UI shows that the transactions are reporting as expected

+ try specifically with bill's app
  - Celery (pwd is wdirks_sample_apps/Celery)
    * Need to make rabbitmq available on 127.0.0.1:5672, did this by adding a portforward to the boot2docker vm in virtualbox. Should remove this when done!
    * Change the license key in newrelic.ini
    * Start `celeryd` (deprecated) with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celeryd  -A tasks -l info` then run `python run_celery_task.py`, seeing 10 transactions show up in the UI
    * Start `celery worker` with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery worker -A tasks -l info` then run `python run_celery_task.py`, seeing 10 transactions show up in the UI
    * Start `celery worker` detached with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery worker --detach -A tasks -l info --pidfile=detach.pid`, seeing 10 transactions show up in the UI, must stop the celeries with `kill`
    * Start `celery multi` with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery multi start multi-test -A tasks -l info`, seeing the transactions show up in the UI, must stop the celeries with a command
  - Celery with older celery version
    * Rollback celery with `pip uninstall celery && pip install celery==3.1.22`
    * Start `celery multi` with `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery multi start multi-test -A tasks -l info`
    * Versions tested
      + 3.1.23
      + 3.1.22
      + 3.1.21
      + 3.1.20
      + 3.0.20
