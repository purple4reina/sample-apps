# Rules Engine

As per the agent spec, there are currently two things that we are doing
incorrectly.

## Case insensitive matches

We don't do it. We are sensitive. To fix, we'd need to change

```python
self.match_expression_re = re.compile(self.match_expression)
```

to

```python
self.match_expression_re = re.compile(self.match_expression, re.IGNORECASE)
```

in `newrelic.core.rules_engine` line 12. See the [python `re` module
docs](https://docs.python.org/2.7/library/re.html#re.IGNORECASE).

The tests in `tests.cross_agent.test_rules` and
`newrelic.core.tests.test_rules_engine` would then need to be fixed and/or
augmented.

## Ignore transaction

If a rule is matched and it says that we should ignore the transaction, we
should do that. But we don't. We need to fix that.

The `RulesEngine.normalize` method in `newrelic.core.rules_engine` returns a
tuple: The "fixed" string then if the transaction should be ignored.

This method is being called by the [stats
engine](https://source.datanerd.us/python-agent/python_agent/blob/develop/newrelic/core/stats_engine.py#L943).
But the second item in the tuple is never being used!

The tests in `tests.cross_agent.test_rules` should be augmented to reflect
this.

## Language agent transaction segment terms rules

https://newrelic.atlassian.net/wiki/spaces/eng/pages/81789286/Language+agent+transaction+segment+terms+rules

The file `segments.py` demonstrates the use of segment term rules in the agent.
In the APM UI these are called "URL whitelist terms" and can be edited from
https://rpm.newrelic.com/accounts/1178500/applications/126045053/url_rules#.
