# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.forms.widgets import RadioSelect


class InlineRadioWidget(RadioSelect):
    option_template_name = 'search/inline_radio_widget_option.html'
