# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import cProfile
import functools
import os

_object = None


def profile(meth):
    def _wrapper(self, *args, **kwargs):
        setattr(self, "__%s" % meth.__name__, meth)
        cProfile.runctx(
            'object.__%s(object, *args, **kwargs)' % (meth.__name__, ), globals(), locals(),
            'profile.%d' % os.getpid())

    functools.update_wrapper(_wrapper, meth)
    return _wrapper
