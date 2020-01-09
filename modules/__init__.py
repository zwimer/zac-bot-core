from os import listdir
from os.path import isfile, join
import importlib


def lsF(d):
    return [f for f in listdir(d) if isfile(join(d, f)) ]

def to_cid(fil, package):
    return fil + ' - ' + package


class Importer:
    _setup = False
    _imported = {}
    _modules = {}

    @classmethod
    def setup(cls, m_path):
        cls._m_name = '.'.join(m_path.split('/')[1:-1])
        cls._m_path = m_path
        cls._setup = True

    @classmethod
    def import_module(cls, x):
        assert cls._setup
        fil = '.' + x
        package = cls._m_name
        cid = to_cid(fil, package)
        if cid not in cls._modules:
            cls._modules[cid] = importlib.import_module(fil, package)
        else:
            cls._modules[cid] = importlib.reload(cls._modules[cid])
        cls._imported[x] = cls._modules[cid].invoke

    @classmethod
    def unimport_module(cls, x):
        assert cls._setup
        del cls._imported[x]

    @classmethod
    def import_all(cls):
        assert cls._setup
        files = [ i for i in lsF(cls._m_path) if i.endswith('.py') ]
        modules = [ i[:-3] for i in files if not i.endswith('__init__.py') ]
        for i in modules:
            cls.import_module(i)

    @classmethod
    def get_imported(cls):
        assert cls._setup
        return cls._imported
