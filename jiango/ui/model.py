# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/9 Feiye
Version: $Id:$
"""
from django.contrib.admin.util import label_for_field
from .base import Table


class Grid(Table):
    def __init__(self, queryset, display_fields=('pk', '__unicode__'), request=None):
        Table.__init__(self)
        self.queryset = queryset
        self.display_fields = display_fields
        self.request = request

        for name in display_fields:
            label = label_for_field(name, self.queryset.model)
            self.add_column(label, name)

        self.loop(self.queryset)
