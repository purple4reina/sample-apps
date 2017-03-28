from newrelic.agent import transient_function_wrapper


def print_nice_transaction_trace():

    def _print_metrics(node, level=0):
        if level == 0:
            name = node.base_name
        else:
            name = node.name
        print('    ' * level + name)
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


def validate_tt_parenting(expected_parenting):
    def validate_parenting(node, expected_node):
        expected_children = expected_node[1]
        node_name = getattr(node, 'name', node.base_name)

        def name():
            return '%s != %s' % (node_name, expected_node[0])
        def length():
            return 'for node %s, len(node.children)=%s, len(expected_children)=%s' % (
                    node_name, len(node.children), len(expected_children))

        assert node_name == expected_node[0], name()
        assert len(node.children) == len(expected_children), length()

        for index, child in enumerate(node.children):
            validate_parenting(child, expected_children[index])

    @transient_function_wrapper('newrelic.core.stats_engine',
            'StatsEngine.record_transaction')
    def _validate_tt_parenting(wrapped, instance, args, kwargs):
        try:
            result = wrapped(*args, **kwargs)
        except:
            raise
        finally:
            def _bind_params(transaction, *args, **kwargs):
                return transaction
            transaction = _bind_params(*args, **kwargs)
            validate_parenting(transaction, expected_parenting)

        return result

    return _validate_tt_parenting

