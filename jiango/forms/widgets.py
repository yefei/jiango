# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from itertools import chain
from django.forms import TextInput, Select
from django.utils.encoding import force_unicode
from django.utils.html import escape
from jiango.utils.humanize import humanize_second
from jiango.utils.pinyin import chinese_to_pinyin


class SecondInput(TextInput):
    def _format_value(self, value):
        if isinstance(value, (int, long)):
            return humanize_second(value)
        return value


class PinyinGroupSelect(Select):
    def render_options(self, choices, selected_choices):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            return u'<option value="%s"%s>%s</option>' % (
                escape(option_value), selected_html,
                force_unicode(option_label))

        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []

        _choices = {}
        for option_value, option_label in chain(self.choices, choices):
            if option_value == '':
                output.append(render_option(option_value, option_label))
                continue

            py = chinese_to_pinyin.convert(option_label)
            print py
            p = '*'
            if py and len(py[0]) > 0:
                p = py[0][0].upper()
            if not _choices.has_key(p):
                _choices[p] = []
            _choices[p].append((option_value, option_label))

        choices_keys = _choices.keys()
        choices_keys.sort()

        for k in choices_keys:
            output.append(u'<optgroup label="%s">' % k)
            options = _choices[k]
            options.sort(key=lambda i: i[1])
            for option in options:
                output.append(render_option(*option))
            output.append(u'</optgroup>')

        return u'\n'.join(output)
