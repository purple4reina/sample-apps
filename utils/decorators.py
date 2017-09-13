from __future__ import print_function

from newrelic.agent import transient_function_wrapper


def print_nice_transaction_trace():

    def _print_metrics(node, level=0):
        def print_headings():
            print('name', end='\t')
            print('start', end='\t')
            print('end', end='\t')
            print('start - end', end='\t')
            print('exclusive', end='\t')
            print()

        def print_start():
            start = round(node.start_time, 3)
            start = str(start).split('.')[0][-3:] + '.' + str(start).split('.')[1]
            print(start, end='\t')

        def print_end():
            end = round(node.end_time, 3)
            end = str(end).split('.')[0][-3:] + '.' + str(end).split('.')[1]
            print(end, end='\t')

        def print_node_time():
            mytime = node.end_time - node.start_time
            print(round(mytime, 3), end='\t')

        def print_exclusive_time():
            print(round(node.exclusive, 3), end='\t')

        if level == 0:
            name = node.base_name
            print_headings()
        elif hasattr(node, 'name'):
            name = node.name
        elif hasattr(node, 'url'):
            name = node.url
        else:
            name = node.operation
        print('    ' * level + name, end='\t')
        print_start()
        print_end()
        print_node_time()
        print_exclusive_time()
        print()
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


def print_metrics():

    @transient_function_wrapper('newrelic.core.stats_engine',
            'StatsEngine.record_transaction')
    def _print_metrics(wrapped, instance, args, kwargs):
        try:
            result = wrapped(*args, **kwargs)
        except:
            raise
        else:
            metrics = instance.stats_table

            for key, value in metrics.items():
                print(key[0], '\t', key[1])

        return result

    return _print_metrics
