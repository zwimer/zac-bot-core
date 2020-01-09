from auth import Auth


def invoke(_, update, context):
    uname = update._effective_chat.username
    print('@' + uname + ' invoked /auth' + ' '.join(context.args))
    usage = 'Usage: /auth <command> <args>'
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


cmds = {
    'reload' : refresh_auth,
    'view' : view_auth,
    'info' : auth_template('info'),
    'add' : auth_template('add'),
    'remove' : auth_template('remove')
}

delim = '\n    '