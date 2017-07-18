# Pivotal Cloud Foundry

This app is designed to test the utilization metadata for PCF.


## Prepare the agent

To make things easier, we'll want to just print the metadata to stdout so we
can just read the logs at agent start up instead of needing to dig through the
audit logs. As of the creation of this app, I did this by adding

```python
print '----------------------------------------'
detect = PCFUtilization.detect()
print 'PCFUtilization.detect(): ', detect
print '----------------------------------------'
```

to the bottom of `newrelic/common/utilization_pivotal.py` then being sure that
the file is imported by adding

```python
from newrelic.common.utilization_pivotal import PCFUtilization
```

to the top of `newrelic/core/data_collector.py`.

Next, we will need to make the distro available once uploaded. To do this,
build the package with `./build.sh` from within the python agent repo, then
copy the package found in `dist/` to this directory. Currently, this file is
named `newrelic-2.89.1.0.tar.gz` and is referenced in the `requirements.txt`
file.


## Prepare deploy

Make sure you are logged into PCF by following the [tutorial from
Pivotal](https://pivotal.io/platform/pcf-tutorials/getting-started-with-pivotal-cloud-foundry/deploy-the-sample-app).

Next, you'll want to tail the logs. This assumes that you've already deployed
the app once, else the app name won't exist.

```
$ cf logs reyapp
```

Now, deploy the app with

```
$ cf push
```

and send it some traffic by `curl`ing the correct url.

```
requested state: started
instances: 1/1
usage: 128M x 1 instances
urls: reyapp-alluring-exiler.cfapps.io                  <----- USE THIS URL
last uploaded: Tue Jul 18 23:12:51 UTC 2017
stack: cflinuxfs2
buildpack: python_buildpack

     state     since                    cpu    memory          disk             details
#0   running   2017-07-18 04:13:58 PM   0.7%   45.5M of 128M   154.4M of 256M
```

When you view the logs that you've been tailing, you should now see the correct
Pivotal metadata!

```
2017-07-18T16:13:57.32-0700 [APP/PROC/WEB/0] OUT ----------------------------------------
2017-07-18T16:13:57.32-0700 [APP/PROC/WEB/0] OUT PCFUtilization.detect():  {'cf_instance_guid': 'b3a75193-8c6f-4efc-41ee-f6a6', 'memory_limit': '128m', 'cf_instance_ip': '10.10.149.69'}
2017-07-18T16:13:57.32-0700 [APP/PROC/WEB/0] OUT ----------------------------------------
```
