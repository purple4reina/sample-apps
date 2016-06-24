# Ed App

This is a copy of the binaries, installed packages and app source as run on the dynos in Ed's Heroku production instance

It was downloaded from
https://drive.google.com/a/newrelic.com/file/d/0B-MCQaHGzyxkTFNkVkdhOWtBU3c/view?usp=sharing

In Ed's words:

> I can't think of anything specific unfortunately.

> If it helps, I can give you the download link to the Heroku slug for the app --
which contains the Python binaries, installed packages and app source as run on
the dynos.

> The link is only valid for an hour, so if it's expired since ping me and I'll
add another:

> https://s3-external-1.amazonaws.com/herokuslugs/heroku.com/v1/5fa311e3-20b7-4244-8144-f409fc0f27f1?AWSAccessKeyId=AKIAJWLOWWHPBWQOPJZQ&Signature=I%2FV88k9Ffkntpq0qdqpJIRr94Yk%3D&Expires=1466627296
(it's a .tar.gz; S3 manages to lose the filename)


## Comparisons
Some notes on the differences between what Ed has given us here and what can be downloaded of treeherder from github.

### Similarities
The source for the treeherder app is pretty much the same, just might be a different git HEAD.

### Differences
+ It looks like there are some differences in the code itself, I assume due to differing git HEADs
+ The sample from Ed has three new directories:
  - .heroku
    * lists the python version which is 2.7.11. My laptop is running 2.7.10, but the Vagrant box is running 2.7.11.
    * `.heroku/python/bin` directory provides all binaries (like the python, celery, and newrelic-admin ones)
  - .profile.d
    * `.profile.d/python.gunicorn.sh` is a script that sets some configuration for the gunicorn workers. *this is a good spot to explore!*
  - dist
    * seems to just contain the html and css files for the website?

## Running locally
It seems that Heroku supports local development in environments that closely mirror their prod ones. The [docker one](https://devcenter.heroku.com/articles/local-development-with-docker) seems promising...

+ Download the heroku toolbelt
+ Get the heroku docker plugin `heroku plugins:install heroku-container-tools`
+ Create `app.json` file to tell the plugin the configs for the docker container. Put it in the root dir of the app itself.
+ Initialize all the things `heroku container:init`
+ Requires `docker-compose`, so get that set up
  * Start a virtualenv from within Ed's app `virtualenv env` and activate it
  * upgrade pip with `pip install --upgrade pip`
  * install docker-compose `pip install docker-compose`
+ Fix the `docker-compose.yml` file. Any place where there is `environment:` and nothing after that, comment it out.
+ Start just the "web" the container `docker-compose up web`
  - I am continually getting errors when it is trying to run `pip install -r requirements.txt`. I am going to stop here for now.
