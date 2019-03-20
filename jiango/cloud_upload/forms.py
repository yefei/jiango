# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/13
"""
from django import forms
from django.core.validators import EMPTY_VALUES
from .settings import SIZE_LIMIT
from .client import get_stream_hash
from .services import get_file_by_hash, create_by_stream, get_or_create_by_stream
from .widgets import CloudClearableFileInput


class UploadForm(forms.Form):
    file = forms.FileField(label=u'文件', max_length=SIZE_LIMIT)

    def clean_file(self):
        fp = self.cleaned_data['file']
        hash_key = get_stream_hash(fp)
        obj = get_file_by_hash(hash_key)
        if obj:
            raise forms.ValidationError(u'相同的文件已经存在: hash:%s, ID:%s' % (obj.hash, obj.pk))
        self._hash_key = hash_key
        return fp

    def save(self):
        fp = self.cleaned_data['file']
        return create_by_stream(fp, fp.content_type, self._hash_key)


class CloudFileFormField(forms.FileField):
    widget = CloudClearableFileInput

    def __init__(self, queryset=None, to_field_name=None, **kwargs):
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.fp = None
        super(CloudFileFormField, self).__init__(**kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        self.fp = super(CloudFileFormField, self).to_python(value)
        return get_or_create_by_stream(self.fp, self.fp.content_type)


class CloudImageFormField(forms.ImageField):
    widget = CloudClearableFileInput

    def __init__(self, queryset=None, to_field_name=None, **kwargs):
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.fp = None
        super(CloudImageFormField, self).__init__(**kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        self.fp = super(CloudImageFormField, self).to_python(value)
        return get_or_create_by_stream(self.fp, self.fp.content_type)


# from .models import Test
#
# class TestForm(forms.ModelForm):
#     class Meta:
#         model = Test
