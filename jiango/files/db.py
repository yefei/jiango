# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
from django.db.models import ImageField
from .storage import hash_file_storage


class HashImageField(ImageField):
    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = '!'
        kwargs['max_length'] = 32
        super(HashImageField, self).__init__(*args, **kwargs)
        self.storage = hash_file_storage
