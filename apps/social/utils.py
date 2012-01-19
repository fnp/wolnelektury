from django.db.models import Q
from catalogue.models import Tag
from catalogue import utils
from catalogue.tasks import touch_tag


def likes(user, work):
    return user.is_authenticated() and work.tags.filter(category='set', user=user).exists()


def get_set(user, name):
    """Returns a tag for use by the user. Creates it, if necessary."""
    try:
        tag = Tag.objects.get(category='set', user=user, name=name)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(category='set', user=user, name=name,
                slug=utils.get_random_hash(name), sort_key=name.lower())
    return tag


def set_sets(user, work, sets):
    """Set tags used for given work by a given user."""

    old_sets = list(work.tags.filter(category='set', user=user))

    work.tags = sets + list(
            work.tags.filter(~Q(category='set') | ~Q(user=user)))

    for shelf in [shelf for shelf in old_sets if shelf not in sets]:
        touch_tag(shelf)
    for shelf in [shelf for shelf in sets if shelf not in old_sets]:
        touch_tag(shelf)

    # delete empty tags
    Tag.objects.filter(category='set', user=user, book_count=0).delete()
