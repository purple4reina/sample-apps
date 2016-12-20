# Cherrypy

## Support ticket

https://newrelic.zendesk.com/agent/tickets/224215

User reported an inability to ignore errors of status code 400. I was unable to
reproduce what they were seeing.


## SEGFAULT

When running this app using uwsgi as per the [cherry-py
docs](http://docs.cherrypy.org/en/latest/deploy.html#uwsgi), a SEGFAULT is hit.

To recreate, run `./start_app.sh`.

The error:

```
*** Starting uWSGI 2.0.14 (64bit) on [Tue Dec 20 14:29:37 2016] ***
compiled with version: 4.2.1 Compatible Apple LLVM 7.0.2 (clang-700.1.81) on 12 October 2016 15:16:31
os: Darwin-14.5.0 Darwin Kernel Version 14.5.0: Sun Sep 25 22:07:15 PDT 2016; root:xnu-2782.50.9~1/RELEASE_X86_64
nodename: rabolofia
machine: x86_64
clock source: unix
detected number of CPU cores: 8
current working directory: /Users/rabolofia/Documents/sample-apps/cherrypy
detected binary path: /Users/rabolofia/Documents/sample-apps/cherrypy/env/bin/uwsgi
!!! no internal routing support, rebuild with pcre support !!!
*** WARNING: you are running uWSGI without its master process manager ***
your processes number limit is 709
your memory page size is 4096 bytes
detected max file descriptor number: 256
lock engine: OSX spinlocks
thunder lock: disabled (you can enable it with --thunder-lock)
uwsgi socket 0 bound to TCP address 127.0.0.1:8080 fd 3
Python version: 2.7.10 (default, Jul 14 2015, 19:46:27)  [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.39)]
Python main interpreter initialized at 0x7fe69bd00bd0
python threads support enabled
your server socket listen backlog is limited to 100 connections
your mercy for graceful operations on workers is 60 seconds
mapped 72760 bytes (71 KB) for 1 cores
*** Operational MODE: single process ***
[20/Dec/2016:14:29:38] ENGINE Bus STARTING
[20/Dec/2016:14:29:38] ENGINE Started monitor thread '_TimeoutMonitor'.
[20/Dec/2016:14:29:38] ENGINE Bus STARTED
WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x7fe69bd00bd0 pid: 23666 (default app)
spawned uWSGI worker 1 (and the only) (pid: 23666, cores: 1)
2016-12-20 14:29:38,366 (23666/uWSGIWorker1Core0) newrelic.core.agent INFO - New Relic Python Agent (2.76.0.55)
127.0.0.1 - - [20/Dec/2016:14:29:38] "GET / HTTP/1.1" 400 1428 "" "curl/7.43.0"
[pid: 23666|app: 0|req: 1/1] 127.0.0.1 () {24 vars in 251 bytes} [Tue Dec 20 14:29:38 2016] GET / => generated 1428 bytes in 5 msecs (HTTP/1.1 400) 4 headers in 150 bytes (2 switches on core 0)
127.0.0.1 - - [20/Dec/2016:14:29:39] "GET / HTTP/1.1" 400 1428 "" "curl/7.43.0"
[pid: 23666|app: 0|req: 2/2] 127.0.0.1 () {24 vars in 251 bytes} [Tue Dec 20 14:29:39 2016] GET / => generated 1428 bytes in 2 msecs (HTTP/1.1 400) 4 headers in 150 bytes (2 switches on core 0)
!!! uWSGI process 23666 got Segmentation Fault !!!
*** backtrace of 23666 ***
0   uwsgi                               0x00000001034c2120 uwsgi_backtrace + 48
1   uwsgi                               0x00000001034c2663 uwsgi_segfault + 51
2   libsystem_platform.dylib            0x00007fff8b95df1a _sigtramp + 26
3   ???                                 0x00000001052488f8 0x0 + 4381247736
4   Python                              0x0000000103603259 PyCFunction_Call + 502
5   Python                              0x00000001036527f3 PyEval_EvalFrameEx + 17005
6   Python                              0x0000000103654c82 _PyEval_SliceIndex + 902
7   Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
8   Python                              0x0000000103654c82 _PyEval_SliceIndex + 902
9   Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
10  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
11  Python                              0x0000000103654bf1 _PyEval_SliceIndex + 757
12  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
13  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
14  Python                              0x0000000103654bf1 _PyEval_SliceIndex + 757
15  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
16  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
17  Python                              0x0000000103654bf1 _PyEval_SliceIndex + 757
18  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
19  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
20  Python                              0x0000000103654bf1 _PyEval_SliceIndex + 757
21  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
22  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
23  Python                              0x00000001035f25de PyFunction_SetClosure + 826
24  Python                              0x00000001035d450a PyObject_Call + 99
25  Python                              0x0000000103650f82 PyEval_EvalFrameEx + 10748
26  Python                              0x0000000103654c82 _PyEval_SliceIndex + 902
27  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
28  Python                              0x0000000103654c82 _PyEval_SliceIndex + 902
29  Python                              0x00000001036519a6 PyEval_EvalFrameEx + 13344
30  Python                              0x000000010364e352 PyEval_EvalCodeEx + 1409
31  Python                              0x00000001035f25de PyFunction_SetClosure + 826
32  Python                              0x00000001035d450a PyObject_Call + 99
33  Python                              0x00000001035df2f7 PyMethod_New + 1210
34  Python                              0x00000001035d450a PyObject_Call + 99
35  Python                              0x00000001036543df PyEval_CallObjectWithKeywords + 93
36  Python                              0x0000000103681196 initthread + 1526
37  libsystem_pthread.dylib             0x00007fff9071305a _pthread_body + 131
38  libsystem_pthread.dylib             0x00007fff90712fd7 _pthread_body + 0
39  libsystem_pthread.dylib             0x00007fff907103ed thread_start + 13
*** end of backtrace ***
./start_app.sh: line 10: 23666 Segmentation fault: 11  newrelic-admin run-program uwsgi --socket 127.0.0.1:8080 --protocol=http --wsgi-file app.py --callable wsgiapp --enable-threads --single-interpreter --wsgi-env-behavior=holy
```
