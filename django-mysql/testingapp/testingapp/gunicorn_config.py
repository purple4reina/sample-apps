import newrelic.agent


def worker_abort(worker):
    #newrelic.agent.shutdown_agent(timeout=5.0)
    #worker.log.info('New Relic: Shutdown Agent Complete.')
    worker.log.info('REINA: worker_abort hook executed')
