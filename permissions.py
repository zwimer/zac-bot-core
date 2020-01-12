from copy import deepcopy
import logging
import json

import utils


class Permissions:

    ############################# Public #############################

    @classmethod
    def setup(cls, f):
        cls.f = f
        cls.load()

    ##################### Getters #####################

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

    @classmethod
    def admin_modules(cls):
        return set(cls._admin_modules)

    ##################### Determiners #####################

    @classmethod
    def is_protected(cls, module):
        return module in cls._modules

    @classmethod
    def is_user(cls, user):
        return user in cls._users

    @classmethod
    def user_modules(cls, user):
        return cls._users[user]

    @classmethod
    def is_admin(cls, user):
        return user in cls._admins

    ##################### Other #####################

    @classmethod
    def secure_module(cls, module, fn):
        def wrapper(update, *args, **kwargs):
            if utils.whois(update) in cls._modules[module]:
                fn(update, *args, **kwargs), 'module already loaded'
        return wrapper

    @classmethod
    def load(cls):
        data = cls._read_json(cls.f)
        cls._verify(data, True)
        cls._load_data(data)

    ##################### Config #####################

    ############ Info ############

    @classmethod
    def user_info(cls, user):
        assert user in cls._users, 'no such user'
        return list(cls._users[user])

    @classmethod
    def group_info(cls, group):
        assert group in cls._groups, 'no such group'
        return list(cls._groups[group])

    @classmethod
    def module_info(cls, module):
        assert module in cls._modules, 'no such module'
        return list(cls._modules[module])

    ############ Add ############

    ### Basic ###

    @classmethod
    def add_user(cls, name):
        assert name not in cls._users, 'user already exists'
        data = cls._data_copy()
        uid = 1 + max(-1, *data['users'].values())
        data['groups']['core']['everyone'].append(uid)
        data['users'][name] = uid
        cls._update(data)

    @classmethod
    def add_group(cls, group):
        assert group not in cls._groups, 'group already exists'
        data = cls._data_copy()
        data['groups']['configurable'][group] = [ ]
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

    ### Add to ###

    @classmethod
    def add_user_to_group(cls, user, group):
        assert user in cls._users, 'no such user'
        assert group in cls._groups, 'no such group'
        assert user not in cls._groups[group], 'user already in group'
        assert group != 'everyone', 'will not edit everyone group'
        data = cls._data_copy()
        confg = data['groups']['configurable']
        grp = confg if group in confg else data['groups']['core']
        grp[group].append(data['users'][user])
        cls._update(data)

    @classmethod
    def add_user_to_module(cls, user, module):
        assert user in cls._users, 'no such user'
        assert module in cls._modules, 'no such module'
        assert user not in cls._modules[module], 'user already has access to module'
        assert module not in cls._admin_modules, \
            'will not add user to an admin module.\nConsider adding user to admin group.'
        data = cls._data_copy()
        data['modules'][module]['users'].append(data['users'][user])
        cls._update(data)

    @classmethod
    def add_group_to_module(cls, group, module):
        assert group in cls._groups, 'no such group'
        assert module in cls._modules, 'no such module'
        assert group not in cls._raw_data['modules'][module]['groups'], \
            'group already has access to module'
        assert module not in cls._admin_modules, \
            'will not add group to an admin module.\nConsider adding user to admin group.'
        data = cls._data_copy()
        data['modules'][module]['groups'].append(group)
        cls._update(data)

    ############ Remove ############

    ### Basic ###

    @classmethod
    def remove_user(cls, user):
        assert user in cls._users, 'no such user'
        data = cls._data_copy()
        uid = data['users'][user]
        del data['users'][user]
        for grp in data['groups'].values():
            for i,k in grp.items():
                if uid in k:
                    k.remove(uid)
                assert uid not in k, 'remove_user sanity check failed'
        for i,k in data['modules'].items():
            if uid in k['users']:
                k['users'].remove(uid)
                assert uid not in k['users'], 'remove_user sanity check failed'
        cls._update(data)

    @classmethod
    def remove_group(cls, group):
        assert group in cls._groups, 'no such group'
        assert group not in cls._raw_data['groups']['core'], \
            'will not remove core group'
        data = cls._data_copy()
        del data['groups']['configurable'][group]
        for i,k in data['modules'].items():
            if group in k['groups']:
                k['groups'].remove(group)
                assert group not in k['groups'], 'remove_group sanity check failed'
        cls._update(data)

    @classmethod
    def remove_module(cls, module):
        assert module in cls._modules, 'no such module'
        data = cls._data_copy()
        del data['modules'][module]
        cls._update(data)

    ### Remove from ###

    @classmethod
    def remove_user_from_group(cls, user, group):
        assert user in cls._users, 'no such user'
        assert group in cls._groups, 'no such group'
        assert group != 'everyone', 'will not edit everyone group'
        assert user in cls._groups[group], 'user not in group'
        data = cls._data_copy()
        confg = data['groups']['configurable']
        grp = confg if group in confg else data['groups']['core']
        grp[group].remove(data['users'][user])
        assert user not in grp, \
            'remove_user_from_group sanity check failed'
        cls._update(data)

    @classmethod
    def remove_user_from_module(cls, user, module):
        assert user in cls._users, 'no such user'
        assert module in cls._modules, 'no such module'
        assert user in cls._modules[module], 'user does not have access to module'
        uid = cls._raw_data['users'][user]
        assert uid in cls._raw_data['modules'][module]['users'], \
            'user only has access to module via a group'
        data = cls._data_copy()
        data['modules'][module]['users'].remove(uid)
        assert user not in data['modules'][module]['users'], \
            'remove_user_from_module sanity check failed'
        cls._update(data)

    @classmethod
    def remove_group_from_module(cls, group, module):
        assert group in cls._groups, 'no such group'
        assert module in cls._modules, 'no such module'
        assert group in cls._raw_data['modules'][module]['groups'], 'group not in module'
        data = cls._data_copy()
        data['modules'][module]['groups'].remove(group)
        assert group not in data['modules'][module]['groups'], \
            'remove_group_from_module sanity check failed'
        cls._update(data)


    ############################# Private #############################

    @classmethod
    def _data_copy(cls):
        return deepcopy(cls._raw_data)

    @staticmethod
    def _read_json(fname):
        with open(fname) as f:
            data = f.read()
        return json.loads(data)

    @staticmethod
    def _verify(data, log_result = False):
        try:
            def all_unique(x):
                return len(list(x)) == len(set(x))

            # General
            assert data.keys() == set(['users', 'groups', 'modules']), 'top level keys invalid'

            # User sanity check
            uids = []
            users = []
            for i, k in data['users'].items():
                assert i not in users, 'duplicate user'
                assert k not in uids, 'duplicate uid'
                users.append(i)
                uids.append(k)
            assert all_unique(uids), 'uids sanity check'
            assert all_unique(users), 'users sanity check'
            users = set(users)
            uids = set(uids)

            # Group sanity check
            assert data['groups'].keys() == set(['core', 'configurable']), 'groups keys invalid'
            assert data['groups']['core'].keys() == set(['admin', 'everyone' ]), 'core keys invalid'
            assert uids == set(data['groups']['core']['everyone']), \
                'everyone group does not match all uids'
            assert len(data['groups']['core']['admin']) > 0, 'admin group may not be empty'
            assert len(data['groups']['core']) == 2, 'core module miscount'
            groups = []
            for i,k in data['groups']['core'].items():
                assert i not in groups, 'duplicate core group'
                assert all_unique(k), 'user repeats in group ' + i
                groups.append(i)
            for i,k in data['groups']['configurable'].items():
                assert i not in groups, 'duplicate configurable group'
                assert all_unique(k), 'user repeats in group ' + i
                groups.append(i)
            assert all_unique(groups), 'groups sanity check'
            groups = set(groups)

            # Modules sanity check
            modules = []
            for name, value in data['modules'].items():
                assert value.keys() == set([ 'info', 'users', 'groups' ]), 'module(' + name + ') keys invalid'
                assert name not in modules, 'duplicate module'
                assert all_unique(value['users']), 'user repeats in module ' + name
                assert all_unique(value['groups']), 'group repeats in module ' + name
                for i in value['groups']:
                    assert i in groups, 'non-existing group referenced'
                for i in value['users']:
                    assert i in uids, 'non-existing user referenced'
                if 'admin' in value['groups']:
                    err = 'admin group must be used in isolation'
                    assert len(value['groups']) == 1, err
                    assert len(value['users']) == 0, err
                assert value['info'] != '', 'empty info field'
                modules.append(name)
            assert all_unique(modules), 'modules sanity check'

        except AssertionError as err:
            if log_result:
                logging.error('Failed to verify permissions config with error: ' + str(err))
            raise

    @classmethod
    def _load_data(cls, data):
        cls._raw_data = data
        # Save modules
        mods = {}
        groups = { **data['groups']['core'], **data['groups']['configurable'] }
        for key, value in data['modules'].items():
            uids = set(value['users'])
            for grp in value['groups']:
                uids |= set(groups[grp])
            mods[key] = uids
        inverted = { k : i for i,k in data['users'].items() }
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
    def _update(cls, data):
        cls._verify(data)
        outs = json.dumps(data, sort_keys=True, indent=4, separators=(',', ' : '))
        cls._load_data(data)
        with open(cls.f, 'w') as f:
            f.write(outs)
