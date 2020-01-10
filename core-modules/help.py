from utils import user, djoin, reply
from permissions import Permissions
from loader import Loader


def invoke(update, context, _):

    # Ignore unprivileged people
    who = user(update)
    if not Permissions.is_user(who):
        return

    # Get descriptions of the loaded modules that the user may invoke
    mods = set(Loader.loaded()) & set(Permissions.user_modules(who))
    descs = [ '/' + i + ': ' + Permissions.info(i) for i in mods ]

    # Reply
    msg = 'Authorized user detected. '
    msg += 'You have access to the following commands:' + djoin(descs)
    reply(update, msg)
