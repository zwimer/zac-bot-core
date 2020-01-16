from utils import logged, reply
import logging
import signal
import time
import os


@logged('kill')
def invoke(update, context, _):
    reqs = [ 'verified' ]
    try:
        assert reqs == context.args
        reply(update, 'Goodbye')
        logging.warning('Killing bot')
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(60)
        logging.error('Failed to gracefully kill bot. Killing.')
        os.kill(os.getpid(), signal.SIGINT)
    except AssertionError:
        reply(update, 'Usage: /kill ' + ' '.join(reqs))
