# Security Spec Testing

For the [Security Spec
Compliance](https://newrelic.atlassian.net/browse/PYTHON-2302) MMF, my job was
to review the [Agent
Security](https://source.datanerd.us/agents/agent-specs/blob/master/Agent-Security.md)
spec and file Jira tickets for anything we are out of compliance on. This is
the sample application I used for testing. Each endpoint demonstrates a
different item in the spec.


## High Security Mode

When the config file has `high_security = true` but high security is not set on
the server side, the agent will attempt to connect to the collector but will
receive an error. It will continue to try to connect but will not create an
active session nor harvest any data. The connect payload will be sent once
every 5 minutes in perpetuity.

The agent behaves in a similar way if `high_security = false` (the default) and
high security is set on the server side.

### Forced configuration

`ssl`: If `ssl = false` is set in the config file, the agent will change it to
`true`.

`record_sql`: If `transaction_tracer.record_sql` is not set to `raw` in the
config file, the agent will change it to `raw`.

`attributes.include`: The agent does not properly handle this case!!! I believe
this is because when the `capture_params` setting was deprecated, it was not
properly/fully translated to the new setting. A [new Jira
ticket](https://newrelic.atlassian.net/browse/PYTHON-2592) was filed though a
[previous ticket](https://newrelic.atlassian.net/browse/PYTHON-2202) is also
related. This is not a huge deal though because we do not actually capture
parameters when in high security mode. However, we do not alert customers to
the fact that we have overridden their setting. Oh, and we should update the
tests. I've documented all this in the Jira.

### Security sensitive attributes and segment parameters

Attributes that contain a uri:
+ `request.headers.referer` and `request.referer`: You can set the `Referer`
header by using curl and adding `-H 'Referer:
http://localhost:5000?mykey=myheader'`. The query parameters are properly
removed when in high security mode.
+ `request_uri`: This is a bit of mumbo done in `WebTransaction.__init__`. We use
`urlparse` to pull off the query params no matter what. I tested this by
physically editing the agent code to set `REQUEST_URI` in the environ.
+ `original_url`: There is no mention of `original_url` anywhere in the codebase.
+ `CurrentUrl`: There is no mention of `CurrentUrl` anywhere in the codebase. Or
anything in any combinations of capitalizations.

NR attributes:
+ `request.parameters.*`: None are set when in HSM.
+ `service.request.*`: We use `request.parameters.*` and not this.
+ `sql`: Sadly, I'm pretty sure we are doing this wrong! I used the `/sql`
  endpoint in my here flask app which creates a table then inserts and selects
  stuff from it. When I grep through the audit logs for statements like
  `SELECT` or `INSERT` I see stuff like `'SELECT * FROM stocks WHERE
  trans="BUY"'` which is _very_ wrong. I am also seeing this in the UI. For
  example [this sql trace
  thingy](https://rpm.newrelic.com/accounts/1178500/applications/74226871/datastores#/overview/SQLite/trace/?id=3dc0fba5-d9e2-11e7-abfc-0242ac110009_4003_5009&metric=Datastore%252Fstatement%252FSQLite%252Fstocks%252Finsert).
  I filed a [Jira ticket](https://newrelic.atlassian.net/browse/PYTHON-2594).
  The particular bug has to do with quoting styles (single v double).
+ `message.parameters.*`: Using my `/message` endpoint, you can see that we
  send up parameters. Sadface. I filed a [Jira
  Ticket](https://newrelic.atlassian.net/browse/PYTHON-2595).
+ `job.(type).args.*`: "Background job arguments are ignored" We don't do this
  at all ever.
+ `errorMessage` and `error.message`: Using my `/error` endpoint, looking in
  the audit logs and the UI, I do not see "Here is the error message". 

### Custom APIs

+ `record_custom_event`: I use `record_custom_event` in the `/event` endpoint.
  When you grep through the audit log there is no mention of the world "hello".
  Additionally, I do not see a new event type in Insights. (I only see that I
  can `SELECT * FROM X` where X is either Transaction or TransactionError.
+ `add_custom_parameter`: I use `add_custom_parameter` in the `/param` endpoint
  to add the hello world parameter to the transaction. I do not see the word
  "hello" in the audit logs nor do I see it in the transaction trace in the UI.
+ `capture_request_params`: When trying to use this I get the warning:
  "WARNING - Cannot modify capture_params in High Security Mode." I even tried
  just doing `txn.capture_params = True` but I still couldn't get them to be
  sent. This is because the params are actually saved on
  `WebTransaction.__init__`.
+ `notice_error` aka `record_exception`: When in high security mode, I see that
  if you use `record_exception` we ignore any `params` passed in and we do not
  send the text of the error message. However, I did find a vulnerability where
  you can manually set `transaction.settings.high_security = False` then we do
  in fact pass up the params! Filed a [Jira
  Ticket](https://newrelic.atlassian.net/browse/PYTHON-2596) for that.

Custom Query APIs from external modules: We don't handle this correctly either.
I believe what they are saying here is that we should not allow third party
instrumentations in high security mode. I filed a [Jira
ticket](https://newrelic.atlassian.net/browse/PYTHON-2597).


## Secure by Default

### Are our settings secure by default?

There are some things we do differently by default. They are stated upon
startup when in high security mode.

+ `strip_exception_messages.enabled`: We want to always capture these things by
  default so I don't want to suggest we change this setting.
+ `custom_insights_events.enabled`: If people want to send insights events,
  should they enable this setting?

### Documented suggestions

I don't see anything explicit in the docs about "if you want HSM then you
should do these things exactly". There is however a list of things that HSM
changes. Note that this is a SHOULD so we don't have to do it.


## Datastore queries (SQL obfuscation)

We do obfuscate queries in the ways described in the spec. However, I am
concerned that there could be some bugs in it as I found yesterday. I believe
we should implement the cross agent tests for these.


## Datastore Segment API

We provide an API for databases that includes sql traces but it isn't public
yet.

We provide an API for datastores that does not include sql traces that is
public. We do not need to worry about this API because it does not collect the
query.

This section says we should use a `slow_query_whitelist` but it's only a
should. We do not do this. We are not going to do this.


## Infrastructure Context

Gathering host for datastore traces. This is very specific to each package we
instrument. I recall when we did this implementation last summer and fall that
we were very careful. We should be good here.


## Custom Attributes

Do not allow users to send any custom attributes or events.

API method and comments:
+ `register_data_source`: These produce metrics. HSM does not prevent metrics.
+ `capture_request_params`: This basically just sets
  `transaction.capture_params = True` and has the vulnerability where you can
  set `transaction.settings.high_security = False` before running it. (see
  [Jira](https://newrelic.atlassian.net/browse/PYTHON-2596))
+ `add_custom_parameter`: Has PYTHON-2596 vuln.
+ `record_exception`: I can get the error message to be sent if I include a
  `strip_exception_messages.whitelist = module:classname` in my ini file. [Jira
  filed](https://newrelic.atlassian.net/browse/PYTHON-2604)
+ `record_custom_event`: I can do `txn.settings.custom_insights_events.enabled
  = True` and it will record the event! [filed
  Jira](https://newrelic.atlassian.net/browse/PYTHON-2605)

+ `add_user_attribute`: Alias to `add_custom_parameter`

+ `function_trace`: I wanna see if you can send params when in HSM. Oh. I can.
  [Filed](https://newrelic.atlassian.net/browse/PYTHON-2606)

I went through everything in `newrelic/agent.py` to double check it. I filed
several tickets as listed above.


## Background jobs

This section applies to our Celery (BackgroundTask) and Pika
(MessageTransaction) instrumentation.

+ `MessageTransaction` and `pika`: The Messaging spec says that we always send all the
  `message.*` attributes. Even though this doesn't make sense to me, that is
  the spec and Allan says he cleared it with security.
+ `BackgroundTask` and `celery`: Our Celery instrumentation just creates
  background tasks with nothing special. There are no parameters or attributes
  or headers or anything of the sort that we would ever send up.


## URI Request Parameters (URI Search Params)

+ Already confirmed that all request parameters are removed.
+ `fragmentid`: I searched the repo and didn't find anything about `fragmentid`
  or `fragment`. There is some mention in some cross agent test fixtures
  though. This is also a MAY.


## Request / Response Headers

You can change `txn.capture_params` to True sometime before the end of the
transaction and we should end up recording all headers. Actually no. Because it
relies on `self.high_security` during `WebTransaction.__init__` to save the
headers to `self._request_params`, this hack doesn't actually work. We're good.
