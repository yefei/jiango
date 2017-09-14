# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
from django.db.models import ImageField, FileField
from .storage import hash_file_storage


class HashImageField(ImageField):
    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = '!'
        kwargs['max_length'] = 32
        super(HashImageField, self).__init__(*args, **kwargs)
        self.storage = hash_file_storage

    def formfield(self, **kwargs):
        kwargs['max_length'] = None # 不需要检查上传的文件名长度
        return super(HashImageField, self).formfield(**kwargs)


class HashFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = '!'
        kwargs['max_length'] = 32
        super(HashFileField, self).__init__(*args, **kwargs)
        self.storage = hash_file_storage

    def formfield(self, **kwargs):
        kwargs['max_length'] = None # 不需要检查上传的文件名长度
        return super(HashFileField, self).formfield(**kwargs)
