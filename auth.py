import json


class Auth:
    auth_f = './auth.json'
    _cache = None

    #################### Public ####################

    @classmethod
    def refresh(cls):
        _ = cls._read_auth(refresh = True)

    # Check if uname is authd for group
    @classmethod
    def has_access(cls, uname, group):
        data = cls._read_auth()
        grp = data['groups'][group]['uid']
        try:
            uid = data['uid'][uname]
            return uid in grp
        except KeyError:
            return False

    # Wrapper
    @classmethod
    def secure_module(cls, fn, group):
        def wrapper(update, context):
            uname = update._effective_chat.username
            if cls.has_access(uname, group):
                fn(update, context)
        return wrapper

    # Getters

    @classmethod
    def groups(cls):
        return cls._read_auth()['groups'].keys()

    @classmethod
    def description(cls, group):
        return cls._read_auth()['groups'][group]['info']

    @classmethod
    def requirements(cls, group):
        return cls._read_auth()['groups'][group]['args']

    @classmethod
    def groups_containing(cls, name):
        data = cls._read_auth()
        assert name in data['uid'], 'User does not exist'
        uid = data['uid'][name]
        groups = []
        for i in data['groups'].items():
            if uid in i[1]['uid']:
                groups.append(i[0])
        return groups

    @classmethod
    def members(cls, group):
        data = cls._read_auth()
        assert group in data['groups'], 'Group does not exist'
        allowed = data['groups'][group]['uid']
        names = set()
        for i in allowed:
            for k in data['uid'].items():
                if i == k[1]:
                    names.add(k[0])
        return names

    # Modifiers

    @classmethod
    def add_user(cls, name):
        data = cls._read_auth()
        assert name not in data['uid'], 'User already exists'
        uid = 1 + max(data['uid'].values())
        data['uid'][name] = uid
        cls._write_auth()

    @classmethod
    def delete_user(cls, name):
        data = cls._read_auth()
        assert name in data['uid'], 'User does not exist'
        uid = data['uid'].pop(name)
        for i in data['groups'].values():
            allowed = i['uid']
            if uid in allowed:
                allowed.remove(uid)
        cls._write_auth()

    @classmethod
    def add_to_group(cls, name, group):
        data = cls._read_auth()
        assert name in data['uid'], 'No such user'
        assert group in data['groups'], 'No such group'
        uid = data['uid'][name]
        allowed = data['groups'][group]['uid']
        assert uid not in allowed, name + ' is already in group ' + group
        allowed.append(uid)
        cls._write_auth()

    @classmethod
    def remove_from_group(cls, name, group):
        data = cls._read_auth()
        assert name in data['uid'], 'No such user'
        assert group in data['groups'], 'No such group'
        uid = data['uid'][name]
        allowed = data['groups'][group]['uid']
        assert uid in allowed, name + ' is not in group ' + group
        allowed.remove(uid)
        cls._write_auth()

    #################### Private ####################

    # Read auth info
    @classmethod
    def _read_auth(cls, *, refresh = False):
        if refresh or (cls._cache is None):
            with open(cls.auth_f) as f:
                data = f.read()
            cls._cache = json.loads(data)
        return cls._cache

    # Write auth info
    @classmethod
    def _write_auth(cls):
        data = json.dumps(cls._cache, sort_keys = True, indent = 4)
        with open(cls.auth_f, 'w') as f:
            print('Updating ' + cls.auth_f + ' with new data:\n' + data)
            f.write(data)
