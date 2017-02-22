**Testcase for reproducing a New Relic Python agent bug.**

For Django function based views, the agent successfully detects `TemplateSyntaxError`,
however for class based views, the agent does not.

**To repro:**

1. Clone the repo
2. `pip install -r requirements.txt`
3. `NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program ./manage.py runserver`
4. Visit:
  - http://localhost:8000/classbased1/
  - http://localhost:8000/classbased2/
5. Wait 60s for the New Relic Python agent to finish a harvest cycle.
6. Check the agent audit log output (in `audit.log`) to see if `TemplateSyntaxError` referenced.
7. Repeat steps 3-6 except visit the function based view example:
  - http://localhost:8000/functionbased/

**Expected:**

For all URLs, the `TemplateSyntaxError` shown in runserver stdout (and in the browser)
is also shown in audit.log, meaning it would be reported to APM by a production app.

**Actual:**

For the class based views the audit log does not reference `TemplateSyntaxError`,
but for the function based view it does.
