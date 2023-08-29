# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from os import path

PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
ROOT_DIR = path.dirname(path.dirname(PROJECT_DIR))
VAR_DIR = path.join(ROOT_DIR, 'var')
