# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from itertools import groupby
from django.forms import Field, ModelChoiceField
from django.forms.models import ModelChoiceIterator
from django.core.validators import EMPTY_VALUES
from jiango.utils.humanize import parse_humanize_second
from .widgets import SecondInput


class SecondField(Field):
    widget = SecondInput
    
    def __init__(self, label=None, help_text=None, *args, **kwargs):
        label = label or u'秒数'
        help_text = help_text or u'1d=1天,1h=1小时,1m=1分钟,1s=1秒s可以不加。例如10天20小时15分3秒: 10d20h15m3'
        super(SecondField, self).__init__(label=label, help_text=help_text, *args, **kwargs)
    
    def to_python(self, value):
        if value in EMPTY_VALUES:
            return ''
        return parse_humanize_second(value)


class GroupedModelChoiceField(ModelChoiceField):
    def __init__(self, queryset, group_by_field, group_label=None, *args, **kwargs):
        super(GroupedModelChoiceField, self).__init__(queryset, *args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label
    
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, ModelChoiceField._set_choices)


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ('', self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    (self.field.group_label(group), [self.choice(ch) for ch in choices])
                        for group,choices in groupby(self.queryset.all(),
                            key=lambda row: getattr(row, self.field.group_by_field))
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for group, choices in groupby(self.queryset.all(),
                    key=lambda row: getattr(row, self.field.group_by_field)):
                yield (self.field.group_label(group), [self.choice(ch) for ch in choices])
