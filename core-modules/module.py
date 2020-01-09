from auth import Auth
from loader import Loader
from importer import Importer


def invoke(_, update, context):
    uname = update._effective_chat.username
    print('@' + uname + ' invoked /module' + ' '.join(context.args))
    usage = 'Usage: /module <command> <args>'
    try:
        fn = cmds[context.args[0]]
        fn(update, context, context.args[1:])
    except (KeyError, IndexError):
        assert len(cmds.keys()) > 0
        msg = usage + '\nCommands:'
        msg += delim + delim.join(cmds.keys())
        reply(update, msg)

def reply(update, msg):
    update.message.reply_text(msg)


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


cmds = {
    'load' : load_module,
    'reload' : reload_module,
    'unload' : unload_module,
    'reset' : reset_modules
}

delim = '\n    '

