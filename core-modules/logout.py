from permissions import Permissions
from loader import DispatcherHandlerContinue
from utils import reply, raw_whois, logged

import logging


@logged('logout')
def invoke(update, *_):
    # raw_user should not be able to log out e_user
    raw_user = raw_whois(update)
    if raw_user == Permissions.e_whois(update):
        raise DispatcherHandlerContinue
    # If invoked by e_user
    try:
        Permissions.remove_user_translation(raw_user)
        reply(update, 'Success')
    except AssertionError as err:
        logging.error(str(err))
        reply(update, 'Error: ' + str(err))
