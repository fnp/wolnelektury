from django.utils.timezone import now
from .models import Schedule


def get_active_schedule(user):
    if not user.is_authenticated:
        return None
    return Schedule.objects.filter(membership__user=user, expires_at__gt=now()).first()

