from utils import reply


def invoke(updater, *_):
    msg = 'Welcome to zac-bot. '
    msg += 'Invoke /help to see what commands are availabe.'
    reply(updater, msg)
