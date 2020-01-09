#!/usr/bin/env python3

import sys
import logging

from telegram.ext import Updater

from auth import Auth
from admin import Admin
from loader import Loader
from importer import Importer


######################################################################
#                                                                    #
#                               Config                               #
#                                                                    #
######################################################################


core_module_path = './core-modules/'
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
    raise


######################################################################
#                                                                    #
#                           Native Modules                           #
#                                                                    #
######################################################################


# Start / help
def start(update, context):

    # Ignore unprivileged people
    uname = update._effective_chat.username
    if not Auth.is_privileged(uname):
        return

    # Get descriptions of commands
    groups = Loader.get_loaded_modules()
    msgs = [  ]
    def to_instr(cmd, data):
        return '/' + cmd + ': ' + data
    for i in groups:
        if Auth.has_access(uname, i):
            msgs.append(to_instr(i, Auth.description(i)))
    msgs.append(to_instr('help', 'This dialog'))

    # Reply
    msg = 'Authorized user detected.'
    msg += 'You have access to the following commands:'
    delim = '\n    '
    msg += delim + delim.join(msgs)
    update.message.reply_text(msg)

def help_fn(update, context):
    start(update, context)

def unknown(update, _):
    uname = update._effective_chat.username
    if Auth.is_privileged(uname):
        msg = 'Unknown command. See /help for available commands.'
        update.message.reply_text(msg)


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
    Admin.setup(updater)

    # Create handler registration
    dp = updater.dispatcher
    Loader.setup(dp, module_path)

    # Install start and help
    Loader.install_builtin('start', start)
    Loader.install_builtin('help', help_fn)
    Loader.install_fallback(unknown)

    # Create install list
    Importer.setup(core_module_path, module_path)
    Importer.import_all()
    install_list = Importer.get_imported()

    # Verify install list
    must_be_empty = [ i for i in Auth.groups() if i not in install_list.keys() ]
    err_msg = "modules.install_list does not contain the elements of auth.json"
    assert len(must_be_empty) == 0, err_msg

    # Install modules
    for name in Auth.groups():
        fn = install_list[name]
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
