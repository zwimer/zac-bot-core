from auth import Auth
from loader import Loader
from modules import Importer


def invoke(_, update, context):
    uname = update._effective_chat.username
    print('@' + uname + ' invoked /admin' + ' '.join(context.args))
    usage = 'Usage: /admin <command> <args>'
    try:
        key = context.args[0]
        prime = cmds[key]
        try:
            fn = prime[context.args[1]]
            fn(update, context, context.args[2:])
        except (KeyError, IndexError):
            assert len(prime.keys()) > 0
            msg = usage + '\n' + key + ' options:'
            msg += delim + delim.join(prime.keys())
            reply(update, msg)

    except (KeyError, IndexError):
        assert len(cmds.keys()) > 0
        msg = usage + '\nCommands:' + delim + delim.join(cmds.keys())
        reply(update, msg)

def reply(update, msg):
    update.message.reply_text(msg)


######################################################################
#                                                                    #
#                                Auth                                #
#                                                                    #
######################################################################


def refresh_auth(update, _, _2):
    msg = 'auth info refreshed'
    Auth.refresh()
    update.message.reply_text(msg)

def view_auth(update, context, _):
    chat_id = update.message.chat_id
    with open(Auth.auth_f, 'rb') as f:
        context.bot.send_document(chat_id=chat_id, document=f)

def auth_template(select):
    auth_options = {
        'info' : { 'user' : info_user, 'group' : info_group },
        'add' : { 'user' : add_user, 'to_group' : add_to_group },
        'remove' : { 'user' : remove_user, 'from_group' : remove_from_group }
    }
    def templated(update, _, args):
        options = auth_options[select]
        try:
            cmd = args[0]
            options[cmd](update, args[1:])
        except (KeyError, IndexError):
            msg = 'Usage: /admin auth ' + select + ' <cmd> <arguments>'
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
    usage = 'Usage: /admin auth info user <username>'
    groups = try_auth(update, Auth.groups_containing, args, usage, False)
    if groups is not None:
        msg = args[0] + ' is in the following groups:'
        msg += delim + delim.join(groups)
        reply(update, msg)

def info_group(update, args):
    usage = 'Usage: /admin auth info group <group>'
    users = try_auth(update, Auth.members, args, usage, False)
    if users is not None:
        msg = args[0] + ' contains the following users:'
        msg += delim + delim.join(users)
        reply(update, msg)

def add_user(update, args):
    usage = 'Usage: /admin auth add user <username>'
    try_auth(update, Auth.add_user, args, usage)

def add_to_group(update, args):
    usage = 'Usage: /admin auth add to_group <username> <group>'
    try_auth(update, Auth.add_to_group, args, usage)

def remove_user(update, args):
    usage = 'Usage: /admin auth remove user <username>'
    try_auth(update, Auth.delete_user, args, usage)

def remove_from_group(update, args):
    usage = 'Usage: /admin auth remove from_group <username> <group>'
    try_auth(update, Auth.remove_from_group, args, usage)


######################################################################
#                                                                    #
#                               module                               #
#                                                                    #
######################################################################


def load_module(update, _, args, *, cmd='load'):
    importable = Auth.groups()
    try:
        mod = args[0]
        assert mod not in Loader.get_loaded_modules()
        assert mod not in Importer.get_imported()
        assert mod in importable
        Importer.import_module(mod)
        imported = Importer.get_imported()
        Loader.install_module(mod, imported[mod])
        reply(update, mod + ' successfully loaded')
    except (AssertionError, IndexError):
        msg = 'Usage: /admin auth ' + cmd + ' <module>'
        imported = Importer.get_imported().keys()
        unimported = [ i for i in importable if i not in imported ]
        if len(unimported) == 0:
            msg += '\nNothing to load. Everything is currently imported'
        else:
            msg += '\nUnimported modules:' + delim + delim.join(unimported)
        reply(update, msg)

def reload_module(update, _, args):
    if unload_module(update, _, args, cmd='reload'):
        load_module(update, _, args, cmd='reload')

def unload_module(update, _, args, *, cmd='unload'):
    try:
        mod = args[0]
        assert mod in Loader.get_loaded_modules()
        assert mod in Importer.get_imported()
        Loader.uninstall_module(mod)
        Importer.unimport_module(mod)
        reply(update, mod + ' successfully unloaded')
        return True
    except (AssertionError, IndexError):
        msg = 'Usage: /admin auth ' + cmd + ' <module>'
        imported = Importer.get_imported().keys()
        msg += '\nImported modules:' + delim + delim.join(imported)
        reply(update, msg)
        return False

def reset_modules(update, _, _2):
    loaded = [ i for i in Loader.get_loaded_modules() ]
    for i in loaded:
        unload_module(update, _, [i])
    failed = []
    for i in Auth.groups():
        try:
            load_module(update, _, [i])
        except Exception as err:
            reply(update, 'Failed to load module "' + i + '" with exception: {0}'.format(err))
            failed.append(i)
    if len(failed) > 0:
        msg = 'Failed to load the following modules:'
        msg += delim + delim.join(failed)
    else:
        msg = 'Successfully reset modules.'
    reply(update, msg)


######################################################################
#                                                                    #
#                              Globals                               #
#                                                                    #
######################################################################


cmds = {
    'auth' : {
        'reload' : refresh_auth,
        'view' : view_auth,
        'info' : auth_template('info'),
        'add' : auth_template('add'),
        'remove' : auth_template('remove')
    },
    'module' : {
        'load' : load_module,
        'reload' : reload_module,
        'unload' : unload_module,
        'reset' : reset_modules
    }
}

delim = '\n    '
