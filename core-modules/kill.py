from utils import logged, reply
import logging


@logged('kill')
def invoke(update, context, stop):
    reqs = [ 'verified' ]
    try:
        assert reqs == context.args
        reply(update, 'Goodbye')
        stop()
    except AssertionError:
        reply(update, 'Usage: /kill ' + ' '.join(reqs))
