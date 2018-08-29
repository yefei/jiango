# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/9 Feiye
"""
from django.utils.safestring import mark_safe
from jiango.ui import Element, Ul
from jiango.bootstrap import ui
from jiango.pagination import Paging


class MainUI(Element):
    TAG = 'section'

    def __init__(self, request=None):
        Element.__init__(self)
        self.set_attr('class', 'content')
        self.request = request

    def add_table(self, table):
        r = Element(table, tag='div', attrs={'class': 'table-responsive'})
        self.append(r)

    def add_page(self, pager):
        self.append(AdminPagination(pager))

    def add_paging_grid(self, qs, display_fields, per_page=100, field_name='page', **grid_kwargs):
        qs = Paging(qs, self.request, per_page, field_name).page()
        grid = ui.Grid(qs.object_list, display_fields, **grid_kwargs)
        self.add_table(grid)
        self.add_page(qs)
        return grid


class AdminPagination(ui.Pagination):
    PREVIOUS = mark_safe('&laquo;')
    NEXT = mark_safe('&raquo;')

    def __init__(self, page_obj):
        super(AdminPagination, self).__init__(page_obj)
        self.set_attr('class', 'pagination pagination-sm no-margin pull-right')
