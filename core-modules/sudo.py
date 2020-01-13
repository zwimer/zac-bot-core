from utils import reply
from loader import Loader
from utils import djoin


def invoke(update, context, _):
    try:
        what = context.args[0]
        fn = Loader.pre_protection_fn(what)
        del context.args[0]
        fn(update, context)
    except AssertionError:
        msg = 'Errpr: No such module.'
        msg += ' Loaded modules are:' + djoin(Loader.loaded())
        reply(update, msg)
    except IndexError:
        reply(update, '/sudo <module> [args...]')
