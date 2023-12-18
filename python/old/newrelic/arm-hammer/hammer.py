import time

import newrelic.agent
from newrelic.core.application import Application

newrelic.agent.initialize('newrelic.ini')
settings = newrelic.agent.global_settings()
app = Application(settings.app_name, [])
app.connect_to_data_collector()

try:
    while True:
        try:
            print(app._active_session.get_agent_commands())
        except Exception as e:
            # if you want to do something with the exception other
            # than printing it, do so here
            print(e.__class__.__name__, e)

        time.sleep(1)  # edit this to your liking

finally:
    app._active_session.shutdown_session()
