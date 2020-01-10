def djoin(lst):
    delim = '\n    '
    return delim + delim.join(lst)

def user(update):
    return update._effective_chat.username

def reply(update, msg):
    update.message.reply_text(msg)

def cid(update):
    return update.message.chat_id
