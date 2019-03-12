# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management import BaseCommand
from catalogue.models import Tag


class Command(BaseCommand):
    help = "Update description for given tag."

    def add_arguments(self, parser):
        parser.add_argument('category')
        parser.add_argument('slug')
        parser.add_argument('description_filename')

    def handle(self, category, slug, description_filename, **options):
        tag = Tag.objects.get(category=category, slug=slug)
        description = open(description_filename).read().decode('utf-8')
        tag.description = description
        tag.save()
