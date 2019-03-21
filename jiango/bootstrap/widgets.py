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
from .config import COLOR_SELECT_VALUES


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


class ColorSelect(widgets.Input):
    input_type = 'hidden'
    colors = COLOR_SELECT_VALUES

    @property
    def media(self):
        return forms.Media(
            js=[static("js/bootstrap.color-select.js")],
            css={'all': [static("css/bootstrap.color-select.css")]}
        )

    def render(self, name, value, attrs=None):
        output = [super(ColorSelect, self).render(name, value, attrs)]
        output.append('<ul class="color-select" id="id_%s_select">' % name)
        selected = False
        for i in self.colors:
            s = value and i.lower() == value.lower()
            if selected is False and s:
                selected = True
            output.append('<li data-value="%s" style="background-color:%s"%s></li>' % (
                i, i, ' class="selected"' if s else ''))
        if selected is False and value:
            output.append('<li data-value="%s" style="background-color:%s" class="selected"><li>' % (value, value))
        output.append('</ul>')
        output.append('<script type="text/javascript">ColorSelect("id_%s_select", "id_%s");</script>' % (name, name))
        return mark_safe(''.join(output))


class ColorModelSelectMultiple(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), color_field='color', name_field='name'):
        self.color_field = color_field
        self.name_field = name_field
        super(ColorModelSelectMultiple, self).__init__(attrs, choices)

    @property
    def media(self):
        return forms.Media(
            css={'all': [static("css/bootstrap.color-select.css")]}
        )

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        final_attrs.pop('class', None)
        output = [u'<ul class="color-model-select">']
        str_values = set([force_unicode(v) for v in value])
        for i, q in enumerate(self.choices.queryset.all()):
            final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            label_for = u' for="%s" style="background-color:%s"' % (final_attrs['id'],  getattr(q, self.color_field))
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            rendered_cb = cb.render(name, force_unicode(q.pk))
            option_label = conditional_escape(force_unicode(getattr(q, self.name_field)))
            output.append(u'<li><label%s>%s%s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        if id_:
            id_ += '_0'
        return id_


def datetime_picker_media():
    return forms.Media(
        js=[static("js/moment.js"), static("js/bootstrap-datetimepicker.js")],
        css={'all': [static("css/bootstrap-datetimepicker.css")]}
    )


def datetime_picker_render(datetime_format, input_html, name):
    output = (
        u'<div class="input-group date" id="id_%s_datetimepicker">' % name,
        input_html,
        u'<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>',
        u'</div>',
        u'<script type="text/javascript">$("#id_%s_datetimepicker")'
        u'.datetimepicker({format:"%s"});</script>' % (name, datetime_format),
    )
    return mark_safe(''.join(output))


class DateTimePicker(widgets.DateTimeInput):
    @property
    def media(self):
        return datetime_picker_media()

    def render(self, name, value, attrs=None):
        input_html = super(DateTimePicker, self).render(name, value, attrs)
        return datetime_picker_render('L LTS', input_html, name)


class DatePicker(widgets.DateInput):
    @property
    def media(self):
        return datetime_picker_media()

    def render(self, name, value, attrs=None):
        input_html = super(DatePicker, self).render(name, value, attrs)
        return datetime_picker_render('L', input_html, name)


class TimePicker(widgets.TimeInput):
    @property
    def media(self):
        return datetime_picker_media()

    def render(self, name, value, attrs=None):
        input_html = super(TimePicker, self).render(name, value, attrs)
        return datetime_picker_render('LTS', input_html, name)
