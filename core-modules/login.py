from permissions import Permissions
from loader import Loader
from utils import reply

import logging


def invoke(update, context, _):
    if 'logout' not in Loader.loaded():
        reply(update, 'Refusing to login, logout module is not loaded')
        return
    try:
        user = Permissions.e_whois(update)
        new_u = context.args[0]
        try:
            Permissions.add_user_translation(user, new_u)
            msg = 'Logged in as @' + new_u
            logging.info(msg)
            reply(update, msg)
        except AssertionError as err:
            reply(update, 'Error: ' + str(err))
    except IndexError:
        reply(update, 'usage: /login <user>')
