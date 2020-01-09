from os import listdir
from os.path import isfile, join
import importlib


class Importer:
    _setup = False
    _imported = {}
    _modules = {}

    #################### Public ####################

    @classmethod
    def setup(cls, core_module_path, module_path):
        cls._c_name = '.'.join(core_module_path.split('/')[1:-1])
        cls._m_name = '.'.join(module_path.split('/')[1:-1])
        cls._core_module_path = core_module_path
        cls._module_path = module_path
        cls._setup = True

    @classmethod
    def import_module(cls, x):
        # Core packages take priority
        packages = [ cls._c_name, cls._m_name ]
        for i in packages:
            try:
                cls._import_module(x, i)
                # Disallow core and non-core packages to share names
                break
            except ModuleNotFoundError as e:
                pass

    @classmethod
    def unimport_module(cls, x):
        assert cls._setup
        del cls._imported[x]

    @classmethod
    def import_all(cls):
        assert cls._setup
        files = lsF(cls._core_module_path) + lsF(cls._module_path)
        pyfiles = [ i for i in files if i.endswith('.py') ]
        modules = [ i[:-3] for i in pyfiles if not i.endswith('__init__.py') ]
        for i in modules:
            cls.import_module(i)

    @classmethod
    def get_imported(cls):
        assert cls._setup
        return cls._imported

    #################### Private ####################

    @classmethod
    def _import_module(cls, x, package):
        assert cls._setup
        fil = '.' + x
        cid = to_cid(fil, package)
        if cid not in cls._modules:
            cls._modules[cid] = importlib.import_module(fil, package)
        else:
            cls._modules[cid] = importlib.reload(cls._modules[cid])
        cls._imported[x] = cls._modules[cid].invoke


def lsF(d):
    return [f for f in listdir(d) if isfile(join(d, f)) ]

def to_cid(fil, package):
    return fil + ' - ' + package
