import contextlib
import boto3
import json

from aws_durable_execution_sdk_python import durable_execution, DurableContext
from aws_durable_execution_sdk_python.__about__ import __version__
from aws_durable_execution_sdk_python.config import CallbackConfig, WaitForCallbackConfig, Duration
from aws_durable_execution_sdk_python.types import BatchResult
from aws_durable_execution_sdk_python.waits import WaitForConditionConfig

lambda_client = boto3.client('lambda')

class DurableEvent(dict):
    def get(self, key, default=None):
        return dict.get(self, 'v', {}).get(key, {}).get('v', default)

@durable_execution
def handler(event, context):

    context.logger.info('starting')
    context.logger.info(f'aws_durable_execution_sdk_python version: {__version__}')
    context.logger.info(json.dumps(event))

    event = DurableEvent(event)

    if event.get('attempt', 1) > 1:
        return {'handler': 'invoke', 'result': 'done'}

    callback_id = event.get('callback_id')
    if callback_id is not None:
        lambda_client.send_durable_execution_callback_success(
                CallbackId=callback_id,
                Result='hello',
        )
        return {'handler': 'callback', 'result': 'done'}

    results = []

    # steps
    context.logger.info('steps')
    result = context.step(lambda _: True, name='rey-step')
    context.logger.info(f'steps result: {result}')
    results.append({'name': 'steps', 'result': result})

    # wait
    context.logger.info('wait')
    result = context.wait(Duration.from_seconds(5), name='rey-wait')
    context.logger.info(f'wait results: {result}')
    results.append({'name': 'wait', 'result': result})

    ## parallel
    #context.logger.info('parallel')
    #result = context.parallel(
    #        lambda ctx: ctx.step(lambda _: True, name='rey-task1'),
    #        lambda ctx: ctx.step(lambda _: True, name='rey-task2'),
    #        lambda ctx: ctx.step(lambda _: True, name='rey-task3'),
    #).get_results()
    #context.logger.info(f'parallel result: {result}')
    #results.append(result)

    # map
    context.logger.info('map')
    result = context.map(
            ['zero', 'one', 'two', 'three', 'four'],
            lambda ctx, item, index, items: ctx.step(lambda _: item),
            name='rey-map',
    ).get_results()
    context.logger.info(f'map result: {result}')
    results.append({'name': 'map', 'result': result})

    ## child context
    #context.logger.info('child context')
    #result = context.run_in_child_context(
    #        lambda ctx: ctx.parallel(
    #            lambda ctx: ctx.step(lambda _: True, name='rey-child1'),
    #            lambda ctx: ctx.step(lambda _: True, name='rey-child2'),
    #            lambda ctx: ctx.step(lambda _: True, name='rey-child3'),
    #        ),
    #        name='rey-child-context',
    #)
    #context.logger.info(f'child context result: {result.get_results()}')
    #results.append(result.get_results())

    ## conditional wait
    #result = context.wait_for_condition(
    #        lambda state, ctx: {'status': 'completed'},
    #        config=WaitForConditionConfig(
    #            initial_state={'status': 'pending'},
    #            wait_strategy=lambda state, attempt: {'should_continue': state['status'] != 'completed'},
    #        )
    #)
    #results.append(result)

    # invoke
    context.logger.info('invoke')
    result = context.invoke(
            'arn:aws:lambda:us-east-1:425362996713:function:rey-durable-function:$LATEST',
            {'attempt': 2},
            name='invoke-processor'
    )
    context.logger.info(f'invoke result: {result}')
    results.append({'name': 'invoke', 'result': result})

    ## callback
    #callback = context.create_callback(
    #        name='approval',
    #        config=CallbackConfig(timeout_seconds=10),
    #)
    #context.step(
    #        lambda _: context.invoke(
    #            'arn:aws:lambda:us-east-1:425362996713:function:rey-durable-function',
    #            {'callback_id': callback.callback_id},
    #            name='invoke-callback'
    #        ),
    #        name='send_request'
    #)
    #result = callback.result()
    #results.append(result)

    ## wait for callback
    #result = context.wait_for_callback(
    #        lambda callback_id: context.invoke(
    #            'arn:aws:lambda:us-east-1:425362996713:function:rey-durable-function',
    #            {'callback_id': callback_id},
    #            name='invoke-wait-callback',
    #        ),
    #        name='external-api',
    #        config=WaitForCallbackConfig(timeout_seconds=10),
    #)
    #results.append(result)

    return {
            'event': event,
            'results': results,
    }
