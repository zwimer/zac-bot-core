#!/usr/bin/env python3

import sys
import logging

from telegram.ext import Updater

from auth import Auth
from loader import Loader
from modules import Importer


######################################################################
#                                                                    #
#                               Config                               #
#                                                                    #
######################################################################


module_path = './modules/'


######################################################################
#                                                                    #
#                           Error Handling                           #
#                                                                    #
######################################################################



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO)
logger = logging.getLogger(__name__)

# Error handler
def error(_, context):
    logger.warning('Update caused error "%s"', context.error)
    raise # TODO


######################################################################
#                                                                    #
#                           Native Modules                           #
#                                                                    #
######################################################################


# Start / help
def start(update, context):
    uname = update._effective_chat.username
    groups = Loader.get_loaded_modules()
    msgs = [  ]
    def to_instr(cmd, data):
        return '/' + cmd + ': ' + data
    for i in groups:
        if Auth.has_access(uname, i):
            msgs.append(to_instr(i, Auth.description(i)))
    if len(msgs) == 0:
        return
    msgs.append(to_instr('help', 'This dialog'))
    msg = 'Authorized user detected. You have access to the following commands:'
    delim = '\n    '
    msg += delim + delim.join(msgs)
    update.message.reply_text(msg)

def help_fn(update, context):
    start(update, context)


######################################################################
#                                                                    #
#                           Main Operation                           #
#                                                                    #
######################################################################


def main(_):

    # Create the updater
    updater = None
    with open('token.priv') as f:
        updater = Updater(f.read().strip(), use_context=True)

    # Create handler registration
    dp = updater.dispatcher
    Loader.setup(dp, module_path)

    # Install start and help
    Loader.install_builtin('start', start)
    Loader.install_builtin('help', help_fn)

    # Create install list
    Importer.setup(module_path)
    Importer.import_all()
    install_list = Importer.get_imported()

    # Verify install list
    g1 = install_list.keys()
    g2 = Auth.groups()
    err_msg = "modules.install_list does not match auth.json"
    assert sorted(g1) == sorted(g2), err_msg

    # Install modules
    for name, fn in install_list.items():
        Loader.install_module(name, fn)

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


# Do not run on imports
if __name__ == '__main__':
    main(*sys.argv)
