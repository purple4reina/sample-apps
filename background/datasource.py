def test_datasource(settings):
    def _test(*args, **kwargs):
        print('Running test_datasource!!!!')
        return 1
    return {'factory': _test}
