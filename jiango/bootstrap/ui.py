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
from jiango.pagination import paginate
from jiango.ui import (
    Element, Ul, A, Link,
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
        icon = {True: 'glyphicon glyphicon-ok-circle text-success text-center center-block',
                False: 'glyphicon glyphicon-remove-circle text-danger text-center center-block',
                None: 'glyphicon glyphicon-ban-circle text-muted text-center center-block'}[value]
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
    elif isinstance(field, models.ManyToManyField):
        return u', '.join(unicode(i) for i in value.all())
    else:
        return smart_unicode(value)


class Grid(Table):
    def __init__(self, queryset, display_fields=None, request=None,
                 bordered=True, condensed=True, hover=True, striped=False, auto_append_padding_column=True):
        Table.__init__(self, bordered, condensed, hover, striped)

        self.queryset = queryset
        self.display_fields = display_fields or ('pk', '__unicode__')
        self.request = request
        self.model = queryset.model
        self.model_fields = {}
        append_padding_column = auto_append_padding_column

        for name in display_fields:
            attrs = {}
            if name in ('pk', 'id'):
                label = '#'
                attrs['class'] = 'id'
            elif callable(name):
                label = getattr(name, 'verbose_name', name.__name__)
                attrs['class'] = 'nowrap'
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


class Pagination(Ul):
    TOTAL = u'总数：'
    PREVIOUS = u'上一页'
    NEXT = u'下一页'

    def __init__(self, page_obj):
        Ul.__init__(self)
        self.set_attr('class', 'pagination')
        result = paginate(page_obj)
        self.li(Element(u'%s%d' % (self.TOTAL, len(page_obj)), tag='span'), attrs={'class': 'disabled'})
        if result and result['previous_url']:
            self.li(A(self.PREVIOUS, result['previous_url']))
        else:
            self.li(Element(self.PREVIOUS, tag='span'), attrs={'class': 'disabled'})
        if result:
            for page, url in result['page_urls']:
                if page:
                    if page == page_obj.number:
                        self.li(Element(page, tag='span'), attrs={'class': 'active'})
                    else:
                        self.li(A(page, url))
                else:
                    self.li(Element('...', tag='span'), attrs={'class': 'disabled'})
        if result and result['next_url']:
            self.li(A(self.NEXT, result['next_url']))
        else:
            self.li(Element(self.NEXT, tag='span'), attrs={'class': 'disabled'})


class Nav(Ul):
    STYLE_TABS = 'tabs'  # 默认样式
    STYLE_PILLS = 'pills'  # 胶囊式标签页
    TYPE_STACKED = 'stacked'  # 堆叠样式
    TYPE_JUSTIFIED = 'justified'  # 两端对齐

    def __init__(self, style=STYLE_TABS, type=None):
        super(Nav, self).__init__()
        self.set_attr('class', 'nav nav-%s%s' % (style, ' nav-%s' % type if type else ''))
        self.items = []

    def add_item(self, content, is_active=False, is_disabled=False, is_dropdown=False):
        classes = []
        if is_active:
            classes.append('active')
        if is_disabled:
            classes.append('disabled')
        if is_dropdown:
            classes.append('dropdown')
        attrs = {'role': 'presentation', 'class': ' '.join(classes)}
        self.li(content, attrs)

    def link_loop(self, viewname, choices, active=None):
        for k, v in choices:
            self.add_item(Link(v, viewname, [k]), is_active=active==k)
