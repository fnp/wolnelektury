# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
class DummyThumbnailBackend:
    class DummyThumbnail:
        def __init__(self, url):
            self.url = url

    def get_thumbnail(self, file_, geometry_string, **options):
        return self.DummyThumbnail(url='-'.join((file_.url, geometry_string)))
