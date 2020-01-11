from utils import whois, reply, djoin
from permissions import Permissions
from loader import Loader
import logging


def invoke(update, context, _):
    logging.info('@' + whois(update) + ' invoked /module ' + ' '.join(context.args))
    usage = 'Usage: /module <command> <args>'
    try:
        fn = cmds[context.args[0]]
        fn(update, context.args[1:])
    except (KeyError, IndexError):
        assert len(cmds.keys()) > 0
        msg = usage + '\nCommands:' + djoin(cmds.keys())
        reply(update, msg)


def list_module(update, *_):
    reply(update, 'Modules:' + djoin(Permissions.modules()))

def load_module(update, args, *, cmd='load'):
    try:
        mod = args[0]
        Loader.load(mod)
        reply(update, mod + ' successfully loaded')
        return True
    except (AssertionError, IndexError) as e:
        msg = 'Usage: /module ' + cmd + ' <module>'
        unloaded = [ i for i in Permissions.modules() if i not in Loader.loaded() ]
        msg += '\nUnloaded modules:' + djoin(unloaded)
        reply(update, msg)
        return False
    except Exception as e:
        reply(update, 'Failed to load module.')
        raise

def reload_module(update, args):
    if unload_module(update, args, cmd='reload'):
        load_module(update, args, cmd='reload')

def unload_module(update, args, *, cmd='unload'):
    try:
        mod = args[0]
        Loader.unload(mod)
        reply(update, mod + ' successfully unloaded')
        return True
    except (AssertionError, IndexError):
        msg = 'Usage: /module ' + cmd + ' <module>'
        msg += '\nLoaded modules:' + djoin(Loader.loaded())
        reply(update, msg)
        return False

def reset_modules(update, _):
    for i in list(Loader.loaded()):
        Loader.unload(i)
    reply(update, 'All modules unloaded. Loading modules.')
    success = []
    for mod in Permissions.modules():
        try:
            Loader.load(mod)
            success.append(mod)
        except ModuleNotFoundError as err:
            reply(update, str(err))
            logging.warning(str(err))
    if len(success) > 0:
        msg = 'Successfully loaded:' + djoin(success)
        reply(update, msg)


cmds = {
    'list' : list_module,
    'load' : load_module,
    'reload' : reload_module,
    'unload' : unload_module,
    'reset' : reset_modules
}
