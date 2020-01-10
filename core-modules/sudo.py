from utils import reply
from loader import Loader


def invoke(updater, context, _):
    try:
        what = context.args[0]
        fn = Loader.pre_protection_fn(what)
        del context.args[0]
        fn(updater, context)
    except (IndexError, KeyError):
        reply(update, '/sudo <module> [args...]')
