# -*- coding: utf-8 -*-
# Created on 2015-9-6
# @author: Yefei
from itertools import chain
from django.forms import widgets
from django import forms
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.admin_static import static


class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
    def __init__(self, label_class='checkbox inline', attrs=None, choices=()):
        super(CheckboxSelectMultiple, self).__init__(attrs, choices)
        self.label_class = label_class
    
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = widgets.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<label class="%s"%s>%s %s</label>' % (self.label_class,
                                                                  label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))


class RadioSelect(widgets.RadioSelect):
    def __init__(self, label_class='radio inline', *args, **kwargs):
        super(RadioSelect, self).__init__(*args, **kwargs)
        self.label_class = label_class
    
    def render(self, name, value, attrs=None, choices=()):
        r = self.get_renderer(name, value, attrs, choices)
        return mark_safe('\n'.join([unicode(i).replace('<label', '<label class="%s"' % self.label_class) for i in r]))


class FilteredSelectMultiple(widgets.SelectMultiple):
    @property
    def media(self):
        return forms.Media(js=[static("js/bootstrap.selectfilter.js")])

    def __init__(self, verbose_name, attrs=None, choices=()):
        self.verbose_name = verbose_name
        super(FilteredSelectMultiple, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'selectfilter'
        output = [super(FilteredSelectMultiple, self).render(name, value, attrs, choices)]
        output.append(u'<script type="text/javascript">SelectFilter.init("id_%s", "%s");</script>\n' % (name, self.verbose_name.replace('"', '\\"')))
        return mark_safe(u''.join(output))
