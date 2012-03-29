# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.db.models.fields.files import FieldFile


class OverwritingFieldFile(FieldFile):
    """
        Deletes the old file before saving the new one.
    """

    def save(self, name, content, *args, **kwargs):
        leave = kwargs.pop('leave', None)
        # delete if there's a file already and there's a new one coming
        if not leave and self and (not hasattr(content, 'path') or
                                   content.path != self.path):
            self.delete(save=False)
        return super(OverwritingFieldFile, self).save(
                name, content, *args, **kwargs)


class OverwritingFileField(models.FileField):
    attr_class = OverwritingFieldFile


try:
    # check for south
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([], ["^catalogue\.fields\.OverwritingFileField"])
except ImportError:
    pass
