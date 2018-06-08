# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/6/8 Feiye
Version: $Id:$
"""
from .util import flatatt


class Element(object):
    TAG = None
    CLOSE_TAG = True

    def __init__(self, content=None, attrs=None):
        self.tag = self.TAG
        self.close_tag = self.CLOSE_TAG
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
            output.extend((i.render() if isinstance(i, Element) else unicode(i)) for i in self.contents)
        if self.close_tag:
            output.append('</%s>' % self.tag)
        return ''.join(output)


class H1(Element):
    TAG = 'h1'


class H2(Element):
    TAG = 'h2'


class H3(Element):
    TAG = 'h3'


class H4(Element):
    TAG = 'h4'


class H5(Element):
    TAG = 'h5'


class H6(Element):
    TAG = 'h6'


class P(Element):
    TAG = 'p'


class Img(Element):
    TAG = 'img'
    CLOSE_TAG = False

    def __init__(self, src=None):
        Element.__init__(self)
        if src:
            self.set_attr('src', src)


class Ul(Element):
    TAG = 'ul'

    class Li(Element):
        TAG = 'li'

    def li(self, el, **attrs):
        li = self.Li(el, attrs)
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

        def th(self, el, **attrs):
            th = self.Th(el, attrs)
            self.append(th)
            return th

        def td(self, el, **attrs):
            td = self.Td(el, attrs)
            self.append(td)
            return td

    def tr(self, el, **attrs):
        tr = self.Tr(el, attrs)
        self.append(tr)
        return tr

    def add_column(self, content, loop_key=None, do_render=None):
        pass

    def loop(self, data_list):
        for i in data_list:
            self.tr(i)
        return self
