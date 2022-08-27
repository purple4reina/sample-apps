# Celery

## Worker

Start the worker with

```
celery -A tasks worker -c 1
```

This starts just one worker


## Celery Beat

To use celery beat in addition to the worker start the beat with

```
celery -A beat_task beat -l DEBUG
```

Be sure the `-A <tasks>` portion is also changed to `-A beat_task` for the
worker
