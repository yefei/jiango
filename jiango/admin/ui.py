# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/9 Feiye
Version: $Id:$
"""
from django.utils.safestring import mark_safe
from jiango.ui import Element, Ul, A
from jiango.pagination import paginate


class MainUI(Element):
    TAG = 'section'

    def __init__(self):
        Element.__init__(self)
        self.set_attr('class', 'content')

    def add_table(self, table):
        r = Element(table, tag='div', attrs={'class': 'table-responsive'})
        self.append(r)

    def add_page(self, pager):
        self.append(PageUi(pager))


class PageUi(Ul):
    PREVIOUS = mark_safe('&laquo;')
    NEXT = mark_safe('&raquo;')

    def __init__(self, page_obj):
        Ul.__init__(self)
        self.set_attr('class', 'pagination pagination-sm no-margin pull-right')
        result = paginate(page_obj)
        self.li(Element(u'总数: %d' % len(page_obj), tag='span'), attrs={'class': 'disabled'})
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
