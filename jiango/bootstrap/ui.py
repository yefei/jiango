# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from django.db import models
from django.contrib.admin.util import label_for_field
from django.utils import timezone, formats
from django.utils.encoding import smart_unicode
from jiango.ui import (
    Element,
    Table as _Table,
)


class Label(Element):
    TAG = 'span'

    DEFAULT = 'default'
    PRIMARY = 'primary'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'

    def __init__(self, content, type=DEFAULT):
        Element.__init__(self, content)
        self.set_attr('class', 'label label-%s' % type)


class Table(_Table):
    def __init__(self, bordered=True, condensed=True, hover=True, striped=False):
        _Table.__init__(self)
        classes = ['table']
        bordered and classes.append('table-bordered')
        condensed and classes.append('table-condensed')
        hover and classes.append('table-hover')
        striped and classes.append('table-striped')
        self.set_attr('class', ' '.join(classes))


EMPTY_VALUE = Label(u'无')


def display_for_field(value, field):
    if field.flatchoices:
        return dict(field.flatchoices).get(value, EMPTY_VALUE)
    elif isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
        icon = {True: 'glyphicon glyphicon-ok-circle',
                False: 'glyphicon glyphicon-remove-circle',
                None: 'glyphicon glyphicon-ban-circle'}[value]
        return Element(tag='span', attrs={'class': icon})
    elif value is None:
        return EMPTY_VALUE
    elif isinstance(field, models.DateTimeField):
        return formats.localize(timezone.localtime(value))
    elif isinstance(field, models.DateField) or isinstance(field, models.TimeField):
        return formats.localize(value)
    elif isinstance(field, models.DecimalField):
        return formats.number_format(value, field.decimal_places)
    elif isinstance(field, models.FloatField):
        return formats.number_format(value)
    else:
        return smart_unicode(value)


class Grid(Table):
    def __init__(self, queryset, display_fields=('pk', '__unicode__'), request=None,
                 bordered=True, condensed=True, hover=True, striped=False, auto_append_padding_column=True):
        Table.__init__(self, bordered, condensed, hover, striped)

        self.queryset = queryset
        self.display_fields = display_fields
        self.request = request
        self.model = queryset.model
        self.model_fields = {}
        append_padding_column = auto_append_padding_column

        for name in display_fields:
            attrs = {}
            if name in ('pk', 'id'):
                label = '#'
                attrs['class'] = 'id'
            else:
                label = label_for_field(name, self.model)
                try:
                    field = self.queryset.model._meta.get_field_by_name(name)[0]
                    if isinstance(field, models.TextField):
                        if auto_append_padding_column:
                            append_padding_column = False
                    elif isinstance(field, models.DateField):
                        attrs['class'] = 'datetime'
                    elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                        attrs['class'] = 'number'
                    else:
                        attrs['class'] = 'nowrap'
                    self.model_fields[name] = field
                except models.FieldDoesNotExist:
                    pass
            self.add_column(label, name, attrs=attrs)

        if append_padding_column:
            self.add_column(None)

    def data_col(self, col, data):
        name = col['data_key']
        if name in self.model_fields:
            content = display_for_field(getattr(data, name), self.model_fields[name])
            return self.Tr.Td(content, attrs=col['attrs'])
        return Table.data_col(self, col, data)

    def render(self):
        self.loop(self.queryset)
        return super(Grid, self).render()
