from admin import Admin


def invoke(_, update, context):
    uname = update._effective_chat.username
    print('@' + uname + ' invoked /kill ' + ' '.join(context.args))
    reqs = [ 'verified' ]
    usage = 'Usage: /kill ' + ' '.join(reqs)
    try:
        assert reqs == context.args
        reply(update, 'Goodbye')
        Admin.kill()
    except AssertionError:
        reply(update, usage)

def reply(update, msg):
    update.message.reply_text(msg)
