# Cross Application Tracing

This application illustrates cross application tracing (CAT)

There are three applications, to start all of them just do `./start-app.sh`

Each app has one endpoint, just the `/` location.

1. The first app uses requests to just get `/` on the second app.
2. The second app uses requests to just get `/` on the third app.
3. The third app uses requests to just get `example.com`.

Send traffic to the whole thing but just doing
`while true ; do sleep 1 ; curl http://localhost:5000 ; done`

To stop it, you'll have to use `ps` to find the processes and kill them. Try
this: `ps aux | grep python | grep -e app[123] | awk '{print $2}' | xargs kill`
