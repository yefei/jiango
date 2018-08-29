# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from django.core.urlresolvers import reverse
from .util import flatatt, render_value


class Element(object):
    TAG = None

    def __init__(self, content=None, tag=None, attrs=None, close_tag=True):
        self.tag = tag or self.TAG
        self.close_tag = close_tag
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        self.contents = []
        if content:
            self.append(content)

    def __unicode__(self):
        return self.render()

    def set_tag(self, tag):
        self.tag = tag

    def set_close(self, is_close):
        self.close_tag = is_close

    def set_attr(self, key, value=None):
        self.attrs[key] = value

    def append(self, el):
        self.contents.append(el)

    def prepend(self, el):
        self.contents.insert(0, el)

    def render(self):
        output = []
        if self.tag:
            output.append('<%s' % self.tag)
            if self.attrs:
                output.append(' %s' % flatatt(self.attrs))
            output.append('>')
        if self.contents:
            output.extend((i.render() if isinstance(i, Element) else render_value(i)) for i in self.contents)
        if self.tag and self.close_tag:
            output.append('</%s>' % self.tag)
        return ''.join(output)


class Img(Element):
    TAG = 'img'

    def __init__(self, src=None):
        Element.__init__(self, close_tag=False)
        if src:
            self.set_attr('src', src)


class A(Element):
    TAG = 'a'

    def __init__(self, content, href=None, target=None):
        Element.__init__(self, content)
        if href:
            self.set_attr('href', href)
        if target:
            self.set_attr('target', target)


class Link(A):
    def __init__(self, content, viewname, args=None, kwargs=None, target=None):
        href = reverse(viewname, args=args, kwargs=kwargs)
        A.__init__(self, content, href, target=target)


class Ul(Element):
    TAG = 'ul'

    class Li(Element):
        TAG = 'li'

    def __init__(self, data_list=None):
        Element.__init__(self)
        self.data_list = data_list

    def li(self, el, attrs=None):
        li = self.Li(el, attrs=attrs)
        self.append(li)
        return li

    def loop(self, data_list):
        for i in data_list:
            self.li(i)
        return self

    def render(self):
        if self.data_list:
            self.loop(self.data_list)
        return super(Ul, self).render()


class Table(Element):
    TAG = 'table'

    class Tr(Element):
        TAG = 'tr'

        class Th(Element):
            TAG = 'th'

        class Td(Element):
            TAG = 'td'

        def th(self, el, attrs=None):
            th = self.Th(el, attrs=attrs)
            self.append(th)
            return th

        def td(self, el, attrs=None):
            td = self.Td(el, attrs=attrs)
            self.append(td)
            return td

    def __init__(self):
        Element.__init__(self)
        self._pre_add_data_row_callbacks = []
        self._post_add_data_row_callbacks = []
        self.columns = []
        self.thead = Element(tag='thead')
        self.tbody = Element(tag='tbody')
        # self.tfoot = Element(tag='tfoot')

    def add_column(self, content, data_key_or_func=None, attrs=None):
        self.columns.append(dict(
            content=content,
            data_key=data_key_or_func,
            attrs=attrs or {},
        ))

    def render_thead(self):
        tr = self.Tr()
        for c in self.columns:
            tr.th(c['content'], c['attrs'])
        self.thead.append(tr)
        self.append(self.thead)

    def data_col(self, col, data):
        key = col['data_key']
        attrs = col['attrs']
        if callable(key):
            content = key(data, attrs)
        elif key is not None:
            if isinstance(data, dict):
                content = data.get(key)
            else:
                content = getattr(data, key)
        else:
            content = None
        return self.Tr.Td(content, attrs=attrs)

    def pre_add_data_row(self, callback):
        self._pre_add_data_row_callbacks.append(callback)

    def post_add_data_row(self, callback):
        self._post_add_data_row_callbacks.append(callback)

    @staticmethod
    def _dispatch(callbacks, **kwargs):
        for func in callbacks:
            func(**kwargs)

    def add_data_row(self, data):
        tr = self.Tr()
        self._dispatch(self._pre_add_data_row_callbacks, tr=tr, data=data)
        for col in self.columns:
            tr.append(self.data_col(col, data))
        self._dispatch(self._post_add_data_row_callbacks, tr=tr, data=data)
        self.tbody.append(tr)

    def loop(self, data_list):
        for i in data_list:
            self.add_data_row(i)
        return self

    def render(self):
        self.render_thead()
        self.append(self.tbody)
        return super(Table, self).render()
