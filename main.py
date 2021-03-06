#!/usr/bin/env python3

import sys, os
import logging

from telegram.ext import Updater

from loader import Loader
from permissions import Permissions


######################################################################
#                                                                    #
#                               Config                               #
#                                                                    #
######################################################################


container_hostname = 'zac-bot'
permisions_f = './permissions.json'
module_path = './modules/'
module_ordered_path = [
    './core-modules/',
    module_path
]

ro_path = module_path + '/ro/'
rw_path = module_path + '/rw/'

### Logging ###

log_file = './zac-bot.log'
log_config = {
    'format' : '%(levelname)s - %(message)s',
    'level' : logging.INFO
}


######################################################################
#                                                                    #
#                           Main Operation                           #
#                                                                    #
######################################################################


# Setup logs
def setup_logs():
    logging.basicConfig(**log_config)
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler(log_file))

# Error handler
def error(_, context):
    logging.warning('Update caused error "%s"', context.error)
    raise

# Fallback option
def unknown(update, _):
    uname = update._effective_chat.username
    if Permissions.is_user(uname):
        msg = 'Unknown command. See /help for available commands.'
        update.message.reply_text(msg)

# Check to see this is running in container_hostname
def is_in_container():
    with open('/proc/sys/kernel/hostname') as f:
        hostname = f.read().strip()
    return hostname == container_hostname


def main(_):
    setup_logs()

    # For security
    if not is_in_container():
        logging.error('Error: Not executing from container!')
        sys.exit(1)

    # Telegram API setup
    updater = None
    with open('token.priv') as f:
        updater = Updater(f.read().strip(), use_context=True)
    dp = updater.dispatcher

    # Create handler registration
    Permissions.setup(permisions_f)
    invoke_extra_args = {
        'mmj_lic' : ro_path,
        'pubkey' : ro_path,
        'shopping' : rw_path + '/shopping/',
        'log' : log_file
    }
    Loader.setup(dp, module_ordered_path, invoke_extra_args, unknown, error)

    # Load modules
    for mod in Permissions.modules():
        try:
            Loader.load(mod)
        except ModuleNotFoundError as err:
            logging.warning(str(err))

    # Start the Bot
    logging.info('Initiating polling.')
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


# Do not run on imports
if __name__ == '__main__':
    main(*sys.argv)
