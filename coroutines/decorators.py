from newrelic.agent import transient_function_wrapper


def print_nice_transaction_trace():

    def _print_metrics(node, level=0):
        def print_node_time():
            mytime = node.end_time - node.start_time
            print(round(mytime, 3))

        if level == 0:
            name = node.base_name
        else:
            name = node.name
        print('    ' * level + name, end='\t')
        print_node_time()
        for child in node.children:
            _print_metrics(child, level=level + 1)

    @transient_function_wrapper('newrelic.core.stats_engine',
            'StatsEngine.record_transaction')
    def _print_nice_transaction_trace(wrapped, instance, args, kwargs):
        try:
            result = wrapped(*args, **kwargs)
        except:
            raise
        finally:
            def _bind_params(transaction, *args, **kwargs):
                return transaction
            transaction = _bind_params(*args, **kwargs)
            _print_metrics(transaction)

        return result

    return _print_nice_transaction_trace
