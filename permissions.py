from copy import deepcopy
import json

import utils


class Permissions:

    #################### Public ####################

    @classmethod
    def setup(cls, f):
        cls.f = f
        cls.load()

    ### Getters ###

    @classmethod
    def info(cls, module):
        return cls._info[module]

    @classmethod
    def users(cls):
        return cls._users.keys()

    @classmethod
    def groups(cls):
        return cls._groups.keys()

    @classmethod
    def modules(cls):
        return cls._modules.keys()

    ### Determiners ###

    @classmethod
    def is_protected(cls, module):
        return module in cls._modules

    @classmethod
    def is_user(cls, user):
        return user in cls._users

    @classmethod
    def user_modules(cls, user):
        return cls._users[user]

    ### Setters ###

    @classmethod
    def add_user(cls, name):
        assert name not in cls._users, 'user already exists'
        data = cls._data_copy()
        uid = 1 + max(-1, *data['users'].values())
        data['groups']['core']['everyone'].append(uid)
        data[name] = uid
        cls._update(data)

    @classmethod
    def add_group(cls, group):
        assert group not in cls._groups, 'group already exists'
        data = cls._data_copy()
        data['groups'][group] = [ ]
        cls._update(data)

    @classmethod
    def add_module(cls, module, description):
        assert len(description) > 0, 'description empty'
        assert module not in cls._modules, 'module already exists'
        data = cls._data_copy()
        data['modules'][module] = {
            'info' : description,
            'groups' : [ ],
            'users' : [ ]
        }
        cls._update(data)

    @classmethod
    def admin_modules(cls):
        return set(cls._admin_modules)

    @classmethod
    def is_admin(cls, user):
        return user in cls._admins

    ### Other ###

    @classmethod
    def secure_module(cls, module, fn):
        def wrapper(update, *args, **kwargs):
            if utils.user(update) in cls._modules[module]:
                fn(update, *args, **kwargs), 'module already loaded'
        return wrapper

    @classmethod
    def load(cls):
        cls._raw_data = cls._read_json(cls.f)
        cls._verify(cls._raw_data, True)
        cls._load_data(cls._raw_data)

    #################### Private ####################

    @classmethod
    def data_copy(cls):
        return deepcopy(cls._raw_data)

    @staticmethod
    def _read_json(fname):
        with open(fname) as f:
            data = f.read()
        return json.loads(data)

    @staticmethod
    def _verify(data, log_result = False):
        try:
            # User sanity check
            uids = set()
            users = set()
            for i, k in data['users'].items():
                assert i not in users, 'duplicate user'
                assert k not in uids, 'duplicate uid'
                users.add(i)
                uids.add(k)
            # Group sanity check
            assert uids == set(data['groups']['core']['everyone']), \
                'everyone group does not contain all users'
            assert len(data['groups']['core']['admin']) > 0, 'no admin'
            assert len(data['groups']['core']) == 2, 'core module miscount'
            groups = set()
            for i in data['groups']['core']:
                assert i not in groups, 'duplicate core group'
                groups.add(i)
            for i in data['groups']['configurable']:
                assert i not in groups, 'duplicate configurable group'
                groups.add(i)
            # Modules sanity check
            modules = set()
            for name, values in data['modules'].items():
                assert name not in modules, 'duplicate module'
                for i in values['groups']:
                    assert i in groups, 'non-existing group referenced'
                for i in values['users']:
                    assert i in uids, 'non-existing user referenced'
                if 'admin' in values['groups']:
                    err = 'admin group must be used in isolation'
                    assert len(values['groups']) == 1, err
                    assert len(values['users']) == 0, err
                assert values['info'] != '', 'empty info field'
                modules.add(name)
        except AssertionError as err:
            if log_result:
                logging.error(cls.f + ' failed to load with error: ' + str(err))
            raise

    @classmethod
    def _load_data(cls, data):
        # Preprocess data
        mods = {}
        groups = { **data['groups']['core'], **data['groups']['configurable'] }
        for key, value in data['modules'].items():
            uids = set(value['users'])
            for grp in value['groups']:
                uids |= set(groups[grp])
            mods[key] = uids
        inverted = { k : i for i,k in data['users'].items() }
        # Save modules
        cls._modules = { b : [ inverted[i] for i in c ] for b,c in mods.items() }
        # Save users
        cls._users = { }
        for user in data['users']:
            cls._users[user] = [ i for i,k in cls._modules.items() if user in k ]
        # Save groups
        cls._groups = { }
        for grp, values in groups.items():
            cls._groups[grp] = [ inverted[i] for i in values ]
        # Save info
        cls._info = { i : k['info'] for i,k in data['modules'].items() }
        # Save admin modules
        is_admin = lambda entry : 'admin' in entry['groups']
        cls._admin_modules = [ i for i,k in data['modules'].items() if is_admin(k) ]
        # Save admins
        cls._admins = set([ inverted[i] for i in data['groups']['core']['admin']])

    @classmethod
    def _update(data):
        cls._verify(data)
        cls._load_data(data)
        outs = json.loads(data)
        with open(cls.f, 'w') as f:
            f.write(outs)
