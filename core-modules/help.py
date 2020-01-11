from utils import whois, djoin, reply
from permissions import Permissions
from loader import Loader


def invoke(update, context, _):

    # Ignore unprivileged people
    who = whois(update)
    if not Permissions.is_user(who):
        return

    # If /help admin was requested
    admin_mods = Permissions.admin_modules()
    if Permissions.is_admin and len(context.args) > 0:
        if context.args[0] == 'admin':
            help_admin(update, admin_mods)
            return

    # Get descriptions of the loaded modules that the user may invoke
    mods = set(Loader.loaded()) & set(Permissions.user_modules(who))
    mods -= set(['start'])
    non_admin_mods = mods - admin_mods
    descs = [ '/' + i + ': ' + Permissions.info(i) for i in non_admin_mods ]

    # Reply
    if Permissions.is_admin(who):
        descs.insert(0, 'Admin: /help admin for admin modules')
    reply(update, 'You may use:' + djoin(descs))

def help_admin(update, mods):
    descs = [ '/' + i + ': ' + Permissions.info(i) for i in mods ]
    reply(update, 'Admin modules:' + djoin(descs))
