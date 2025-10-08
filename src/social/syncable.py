from datetime import datetime
from django.utils.timezone import now, utc


class Syncable:
    @classmethod
    def sync(cls, user, instance, data):
        ts = data.get('timestamp')
        if ts is None:
            ts = now()
        else:
            ts = datetime.fromtimestamp(ts, tz=utc)

        if instance is not None:
            if ts and ts < instance.reported_timestamp:
                return

        if instance is None:
            if data.get('deleted'):
                return
            instance = cls.create_from_data(user, data)
            if instance is None:
                return

        instance.reported_timestamp = ts
        for f in cls.syncable_fields:
            if f in data:
                setattr(instance, f, data[f])

        instance.save()
        return instance

    @property
    def timestamp(self):
        return self.updated_at.timestamp()
    
    @classmethod
    def create_from_data(cls, user, data):
        raise NotImplementedError
