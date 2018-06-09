# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
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


class Ul(Element):
    TAG = 'ul'

    class Li(Element):
        TAG = 'li'

    def __init__(self, data_list=None):
        Element.__init__(self)
        if data_list:
            self.loop(data_list)

    def li(self, el, attrs=None):
        li = self.Li(el, attrs=attrs)
        self.append(li)
        return li

    def loop(self, data_list):
        for i in data_list:
            self.li(i)
        return self


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
        self.columns = []
        self.thead = Element(tag='thead')
        self.tbody = Element(tag='tbody')
        # self.tfoot = Element(tag='tfoot')

    def add_column(self, content, data_key=None, attrs=None, do_render=None):
        self.columns.append(dict(
            content=content,
            data_key=data_key,
            attrs=attrs,
            do_render=do_render,
        ))

    def render_thead(self):
        tr = self.Tr()
        for c in self.columns:
            tr.th(c['content'], c['attrs'])
        self.thead.append(tr)
        self.append(self.thead)

    def data_col(self, col, data):
        do_render = col['do_render']
        if do_render:
            content = do_render(col, data)
        else:
            key = col['data_key']
            if key:
                if isinstance(data, dict):
                    content = data.get(key)
                else:
                    content = getattr(data, key)
            else:
                content = None
        return self.Tr.Td(content, attrs=col['attrs'])

    def add_data_row(self, data):
        tr = self.Tr()
        for col in self.columns:
            tr.append(self.data_col(col, data))
        self.tbody.append(tr)

    def loop(self, data_list):
        self.render_thead()
        for i in data_list:
            self.add_data_row(i)
        self.append(self.tbody)
        return self
