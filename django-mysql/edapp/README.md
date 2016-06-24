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
