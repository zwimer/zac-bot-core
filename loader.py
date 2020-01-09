from telegram.ext import CommandHandler
from auth import Auth


class Loader:
    _handlers = {}
    _modules = set()
    _builtins = set()
    _setup = False

    #################### Public ####################

    # Installed handlers
    @classmethod
    def setup(cls, dp, module_path):
        cls._m_path = module_path
        cls._setup = True
        cls._dp = dp

    # Used to install builtin commands
    @classmethod
    def install_builtin(cls, name, fn):
        assert cls._setup
        assert name not in cls._builtins
        cls._builtins.add(name)
        cls._install(name, fn, cls._groups.builtin)

    # Used to install module commands, protected by auth
    @classmethod
    def install_module(cls, name, raw_fn):
        assert cls._setup
        assert name not in cls._modules
        cls._modules.add(name)
        pathed_fn = lambda a, b : raw_fn(cls._m_path, a, b)
        fn = Auth.secure_module(pathed_fn, name)
        reqs = Auth.requirements(name)
        cls._install(name, fn, cls._groups.modules, **reqs)

    # Used to uninstall module commands
    @classmethod
    def uninstall_module(cls, name):
        assert cls._setup
        assert name in cls._modules
        cls._modules.remove(name)
        group = cls._groups.modules
        hid = cls._to_handler_id(name, group)
        handler = cls._handlers.pop(hid)
        cls._dp.remove_handler(handler, group)

    # Get everything loaded
    @classmethod
    def get_everything_loaded(cls):
        return cls._modules | cls._builtins

    # Get loaded modules
    @classmethod
    def get_loaded_modules(cls):
        return cls._modules

    #################### Private ####################

    # Groups
    class _groups:
        builtin = 0
        modules = 1

    @staticmethod
    def _to_handler_id(name, group):
        return name + ' - ' + str(group)

    # Install the command
    @classmethod
    def _install(cls, name, fn, group, **kwargs):
        assert cls._setup
        handler = CommandHandler(name, fn, **kwargs)
        hid = cls._to_handler_id(name, group)
        cls._handlers[hid] = handler
        cls._dp.add_handler(handler, group)

