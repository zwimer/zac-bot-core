from permissions import Permissions
from utils import user, reply, djoin, cid
import logging


def invoke(update, context, _):
    uname = update._effective_chat.username
    logging.info('@' + uname + ' invoked /auth ' + ' '.join(context.args))
    usage = 'Usage: /auth <command> <args>'
    try:
        cmds[context.args[0]](update, context, context.args[1:])
    except (KeyError, IndexError):
        reply(update, usage + '\nCommands:' + djoin(cmds.keys()))

def refresh_auth(update, *_):
    try:
        Permissions.load()
    except AssertionError:
        raise
    reply(update, 'Permissions refreshed')

def view_auth(update, context, _):
    with open(Permissions.f, 'rb') as f:
        context.bot.send_document(chat_id=cid(update), document=f)

def auth_template(select):
    auth_options = {
        'info' : { 'user' : info_user, 'group' : info_group },
        'add' : { 'user' : add_user, 'group' : add_group, 'to_group' : add_to_group },
        'remove' : { 'user' : remove_user, 'from_group' : remove_from_group }
    }
    def templated(update, _, args):
        options = auth_options[select]
        try:
            cmd = args[0]
            options[cmd](update, args[1:])
        except (KeyError, IndexError):
            msg = 'Usage: /auth ' + select + ' <cmd> <arguments>'
            msg += '\nCommands:' + delim + delim.join(options.keys())
            reply(update, msg)
    return templated

def try_auth(update, f, args, usage, notify_success = True):
    try:
        ret = f(*args)
        if notify_success:
            reply(update, 'Success')
        return ret
    except AssertionError as err:
        reply(update, 'Error: ' + str(err))
    except TypeError:
        reply(update, usage)

def info_user(update, args):
    usage = 'Usage: /auth info user <username>'
    groups = try_auth(update, Auth.groups_containing, args, usage, False)
    if groups is not None:
        msg = args[0] + ' is in the following groups:'
        msg += delim + delim.join(groups)
        reply(update, msg)

def info_group(update, args):
    usage = 'Usage: /auth info group <group>'
    users = try_auth(update, Auth.members, args, usage, False)
    if users is not None:
        msg = args[0] + ' contains the following users:'
        msg += delim + delim.join(users)
        reply(update, msg)

def add_user(update, args):
    usage = 'Usage: /auth add user <username>'
    try_auth(update, Auth.add_user, args, usage)

def add_group(update, args):
    usage = 'Usage: /auth add group <group> [info] [info...]'
    try:
        assert len(args) > 1
        group = args[0]
        description = ' '.join(args[1:])
        try_auth(update, Auth.add_group, [group, description], usage)
    except AssertionError:
        reply(update, usage)

def add_to_group(update, args):
    usage = 'Usage: /auth add to_group <username> <group>'
    try_auth(update, Auth.add_to_group, args, usage)

def remove_user(update, args):
    usage = 'Usage: /auth remove user <username>'
    try_auth(update, Auth.delete_user, args, usage)

def remove_from_group(update, args):
    usage = 'Usage: /auth remove from_group <username> <group>'
    try_auth(update, Auth.remove_from_group, args, usage)


cmds = {
    'reload' : refresh_auth,
    'view' : view_auth
}
    # 'info' : auth_template('info'),
    # 'add' : auth_template('add'),
    # 'remove' : auth_template('remove')
# }
delim = '\n    '
