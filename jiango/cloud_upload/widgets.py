# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/14
"""
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.forms.widgets import ClearableFileInput, CheckboxInput
from .models import File


class CloudClearableFileInput(ClearableFileInput):
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        template = u'%(input)s'
        substitutions['input'] = super(CloudClearableFileInput, self).render(name, value, attrs)

        if value:
            file_obj = File.objects.get(pk=value)
            template = self.template_with_initial
            substitutions['initial'] = (u'<a href="%s" target="_blank">%s: %s</a>'
                                        % (escape(file_obj.url), file_obj.pk, file_obj.hash))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
