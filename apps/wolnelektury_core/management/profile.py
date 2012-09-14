
import cProfile
import functools
import os

_object = None

def profile(meth):
    def _wrapper(self, *args, **kwargs):
        object = self
        setattr(object, "__%s" % meth.__name__, meth)
        cProfile.runctx('object.__%s(object, *args, **kwargs)' % (meth.__name__, ), globals(), locals(),
            "profile.%d" % os.getpid())

    functools.update_wrapper(_wrapper, meth)
    return _wrapper

