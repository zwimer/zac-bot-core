import importlib
import traceback
import logging

from telegram.ext import (
    MessageHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters
)

from permissions import Permissions
from utils import reply, rlock_methods

@rlock_methods
class Loader:
    _py_mods = {}
    _installed = {}
    _pre_protection_fns = {}
    _fallback_g = 9999
    _g = 1000

    #################### Public ####################

    @classmethod
    def setup(cls, dp, ordered_dirs, passthrough, fallback, error_handler):
        assert len(ordered_dirs) > 0
        assert cls._g < cls._fallback_g
        assert 0 < cls._g
        cls._dp = dp
        cls._ordered_dirs = ordered_dirs
        cls._pass = passthrough
        cls._install_error_handler(error_handler)
        cls._install_fallback(fallback)

    @classmethod
    def load(cls, module):
        assert module not in cls._installed, 'module already loaded'
        assert Permissions.is_protected(module), 'module not authorized'
        # Priority given to earlier dirs
        for dir_ in cls._ordered_dirs:
            try:
                cls._load(module, dir_)
                logging.info('Successfully loaded ' + module)
                # Only one module of this name peritted
                return
            except ModuleNotFoundError:
                pass
            except Exception as err:
                logging.error('Error loading ' + module + traceback.format_exc())
                break
        msg = 'Load("' + module + '") failed'
        raise ModuleNotFoundError(msg)

    @classmethod
    def unload(cls, module):
        assert module in cls._installed, 'module not loaded'
        handler = cls._installed.pop(module)
        cls._dp.remove_handler(handler, cls._g)

    @classmethod
    def loaded(cls):
        return cls._installed.keys()

    @classmethod
    def pre_protection_fn(cls, module):
        assert module in cls._pre_protection_fns
        return cls._pre_protection_fns[module]

    #################### Private ####################

    @classmethod
    def _load(cls, module, package):
        mod = cls._reimport(module, package)
        try:
            fn = mod.invoke
        except AttributeError:
            logging.error('Module "' + module + '" has no "invoke" function')
            raise

        cls._install_handler(module, mod.invoke)

    @classmethod
    def _reimport(cls, module, dir_):
        if module not in cls._py_mods:
            package = dir_.replace('./', '').replace('/', '')
            mod = importlib.import_module('.' + module, package)
        else:
            mod = importlib.reload(cls._py_mods[module])
        cls._py_mods[module] = mod
        return mod

    @classmethod
    def _install_handler(cls, module, install_me):
        # Secure the function and ensure dispatch termination when complete
        def packaged_fn(update, context):
            try:
                extra_args = cls._pass[module] if module in cls._pass else None
                install_me(update, context, extra_args)
            except DispatcherHandlerStop:
                raise
            except Exception as err:
                msg = 'Error invoking ' + module + '.invoke: '
                msg += traceback.format_exc()
                logging.error(msg)
                reply(update, 'Internal error.')
            raise DispatcherHandlerStop()
        cls._pre_protection_fns[module] = packaged_fn
        safe = Permissions.secure_module(module, packaged_fn)
        # Install the handler
        c_handler = CommandHandler(module, safe)
        cls._dp.add_handler(c_handler, cls._g)
        cls._installed[module] = c_handler

    @classmethod
    def _install_fallback(cls, fallback):
        cls._fallback = MessageHandler(Filters.command, fallback)
        cls._dp.add_handler(cls._fallback, cls._fallback_g)

    @classmethod
    def _install_error_handler(cls, handler):
        cls._dp.add_error_handler(handler)
        cls._error_hander = handler
