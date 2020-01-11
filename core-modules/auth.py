from permissions import Permissions
from utils import whois, reply, djoin, cid
import logging


def invoke(update, context, _):
    uname = whois(update)
    invocation = '/' + mod_name + djoin(context.args, ' ')
    logging.info('@' + uname + ' invoked ' + invocation)
    explore_tree(update, context, context.args, cmds, [])


def explore_tree(update, context, args, cmd, chain):
    try:
        opt = args[0]
        res = cmd[opt]
        chain.append(opt)
        if isinstance(res, dict):
            explore_tree(update, context, args[1:], res, chain)
        else:
            res(update, context, args[1:], chain)
    except (IndexError, KeyError):
        usage = 'usage: /' + mod_name + djoin(chain, ' ') + ' <argument>\nOptions:' + djoin(cmd.keys())
        reply(update, usage)

def passthrough(fn_usage, notify_success = True):
    def real_decorator(f):
        def wrapper(update, context, args, chain):
            try:
                f(update, *args)
                if notify_success:
                    reply(update, 'Success')
            except AssertionError as err:
                reply(update, 'Error: ' + str(err))
            except TypeError:
                if fn_usage:
                    chain.append(fn_usage)
                reply(update, 'usage: /' + mod_name + djoin(chain, ' '))
        return wrapper
    return real_decorator

##################### Handlers #####################

@passthrough('')
def refresh_auth(update, *_):
    Permissions.load()

def download_auth(update, context, *_):
    with open(Permissions.f, 'rb') as f:
        context.bot.send_document(chat_id=cid(update), document=f)

##################### Info #####################

@passthrough('<user>', False)
def read_user(update, user):
    mods = Permissions.user_info(user)
    reply(update, user + ' has access to:' + djoin(mods))

@passthrough('<group>', False)
def read_group(update, group):
    users = Permissions.group_info(group)
    reply(update, group + ' contains users:' + djoin(users))

@passthrough('<module>', False)
def read_mod(update, module):
    users = Permissions.group_info(group)
    reply(update, module + ' can be run by:' + djoin(users))

##################### Add #####################

############ User ############

@passthrough('<user>')
def add_user(_, user):
    Permissions.add_user(user)

@passthrough('<user> <group>')
def add_user_to_group(_, user, group):
    Permissions.add_user_to_group(user, group)

@passthrough('<user> <module>')
def add_user_to_mod(_, user, module):
    Permissions.add_user_to_module(user, module)

############ Group ############

@passthrough('<group>')
def add_group(_, group):
    Permissions.add_group(group)

@passthrough('<group> <module>')
def add_group_to_mod(_, group, module):
    Permissions.add_group_to_module(group, module)

############ Module ############

@passthrough('<module> <description>')
def add_mod(_, module, desc):
    Permissions.add_module(module, desc)

##################### Add #####################

############ User ############

@passthrough('<user>')
def remove_user(_, user):
    Permissions.remove_user(user)

@passthrough('<user> <group>')
def remove_user_from_group(_, user, group):
    Permissions.remove_user_from_group(user, group)

@passthrough('<user> <module>')
def remove_user_from_mod(_, user, module):
    Permissions.remove_user_from_module(user, module)

############ Group ############

@passthrough('<group>')
def remove_group(_, group):
    Permissions.remove_group(group)

@passthrough('<group> <module>')
def remove_group_from_mod(_, group, module):
    Permissions.remove_group_from_module(group, module)

############ Module ############

@passthrough('<module>')
def remove_mod(_, module):
    Permissions.remove_module(module)

##################### Config #####################

cmds = {
    'reload' : refresh_auth,
    'download' : download_auth,
    'info' : {
        'user' : read_user,
        'group': read_group,
        'module' : read_mod
    },
    'add' : {
        'user' : {
            'user' : add_user,
            'group' : add_user_to_group,
            'module' : add_user_to_mod
        },
        'group' : {
            'group' : add_group,
            'module' : add_group_to_mod
        },
        'module' : add_mod
    },
    'remove' : {
        'user' : {
            'user' : remove_user,
            'group' : remove_user_from_group,
            'module' : remove_user_from_mod
        },
        'group' : {
            'group' : remove_group,
            'module' : remove_group_from_mod
        },
        'module' : remove_mod
    }
}

mod_name = 'auth'
