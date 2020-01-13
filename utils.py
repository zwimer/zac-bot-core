import inspect
import threading


def djoin(lst, delim = '\n    '):
    return delim + delim.join(lst)

def whois(update):
    return update._effective_chat.username

def reply(update, msg):
    update.message.reply_text(msg)

def cid(update):
    return update.message.chat_id

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
