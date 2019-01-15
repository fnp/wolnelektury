class DummyThumbnailBackend:
    class DummyThumbnail:
        def __init__(self, url):
            self.url = url

    def get_thumbnail(self, file_, geometry_string, **options):
        return self.DummyThumbnail(url='-'.join((file_.url, geometry_string)))
