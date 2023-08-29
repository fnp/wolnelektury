#!/usr/bin/env python
# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "wolnelektury.settings.test"
        if 'test' in sys.argv
        else "wolnelektury.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
