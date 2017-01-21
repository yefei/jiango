# -*- coding: utf-8 -*-
"""
Created on 2017/1/21
@author: Fei Ye <316606233@qq.com>
"""
from django import forms
from .models import get_value_type, TYPE_INT, TYPE_FLOAT


class ItemForm(forms.Form):
    def __init__(self, item, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        if len(item) > 2 and isinstance(item[2], forms.Field):
            field = item[2]
        else:
            if len(item) > 2:
                label = item[2]
            else:
                label = None

            value_type = get_value_type(item[1])
            if value_type == TYPE_INT:
                field = forms.IntegerField(label=label)
            elif value_type == TYPE_FLOAT:
                field = forms.FloatField(label=label)
            else:
                field = forms.CharField(label=label)
        self.fields['value'] = field
