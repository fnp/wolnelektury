# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
import traceback

from django.core.management.base import BaseCommand


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


class Command(BaseCommand):
    help = 'Reindex pictures.'

    def add_arguments(self, parser):
        self.add_argument(
                '-n', '--picture-id', action='store_true', dest='picture_id',
                default=False, help='picture id instead of slugs')
        self.add_argument('slug/id', nargs='*', metavar='slug/id')

    def handle(self, **opts):
        from picture.models import Picture
        from search.index import Index
        idx = Index()

        if opts['args']:
            pictures = []
            for a in opts['args']:
                if opts['picture_id']:
                    pictures += Picture.objects.filter(id=int(a)).all()
                else:
                    pictures += Picture.objects.filter(slug=a).all()
        else:
            pictures = list(Picture.objects.order_by('slug'))
        while pictures:
            try:
                p = pictures[0]
                print(p.slug)
                idx.index_picture(p)
                idx.index.commit()
                pictures.pop(0)
            except:
                traceback.print_exc()
                try:
                    # we might not be able to rollback
                    idx.index.rollback()
                except:
                    pass
                retry = query_yes_no("Retry?")
                if not retry:
                    break
