from utils import user, reply
import logging


def invoke(update, context, stop):
    reqs = [ 'verified' ]
    try:
        assert reqs == context.args
        reply(update, 'Goodbye')
        logging.warning('@' + user(update) + ' invoked /kill')
        stop()
    except AssertionError:
        reply(update, 'Usage: /kill ' + ' '.join(reqs))
