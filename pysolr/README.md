# pysolr

This sample app does a simple search on Solr. I couldn't get Solr installed on
my laptop and I couldn't figure out how to communicate with Solr running in a
docker container. So, I ran this app using packnsend which means a bunch of
extra steps.

I had to copy my `app.py`, `newrelic.ini`, and `run_app.sh` files to my
`python_agent` directory. This way they can be grabbed when doing a packnsend
run.

```
$ cp ../sample-apps/pysolr/app.py . && \
    cp ../sample-apps/pysolr/newrelic.ini . && \
    cp ../sample-apps/pysolr/run_app.sh . && \
    git add . && \
    pns run ./run_app.sh
```
