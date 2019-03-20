# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/14
"""
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.forms.widgets import ClearableFileInput, CheckboxInput, FileInput
from django.core.files.uploadedfile import UploadedFile
from .models import File


class CloudClearableFileInput(ClearableFileInput):
    template_with_initial = u'<div class="row">' \
                            u'<div class="col-md-6">%(initial_text)s: %(initial)s %(clear_template)s</div>' \
                            u'<div class="col-md-6">%(input_text)s: %(input)s</div>' \
                            u'</div>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        template = u'%(input)s'
        substitutions['input'] = FileInput.render(self, name, value, attrs)

        if value and not isinstance(value, UploadedFile):
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
