import inspect
import threading
import logging


def djoin(lst, delim = '\n    '):
    return delim + delim.join(lst)

def raw_whois(update):
    return update.message.chat.username

def reply(update, msg):
    update.message.reply_text(msg)

def cid(update):
    return update.message.chat_id


# Log invocations
def logged(mod, show_args = True):
    def real_decorator(f):
        def wrapper(update, context, extra):
            msg = '@' + raw_whois(update) + ' invoked: /' + mod
            msg += djoin(context.args, ' ') if show_args else ' ****'
            msg = msg.strip()
            logging.info(msg)
            f(update, context, extra)
        return wrapper
    return real_decorator

# RLock all methods of a class
def rlock_decorator(lock, f):
    def wrapper(*args, **kwargs):
        lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            lock.release()
    return wrapper

def rlock_methods(cls):
    lock = threading.RLock()
    for name, method in inspect.getmembers(cls, inspect.ismethod):
        setattr(cls, name, rlock_decorator(lock, method))
    return cls
