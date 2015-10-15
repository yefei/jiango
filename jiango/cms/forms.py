# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
from django import forms
from jiango.importlib import import_object
from .models import Column
from .config import COLUMN_PATH_RE, CONTENT_ACTIONS, CONTENT_MODELS


IMPORTED_ACTIONS = {}

def get_action_form(action):
    if action in CONTENT_ACTIONS:
        if action not in IMPORTED_ACTIONS:
            IMPORTED_ACTIONS[action] = import_object(CONTENT_ACTIONS[action]['form'])
        return IMPORTED_ACTIONS[action]


class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
    
    def clean_path(self):
        path = self.cleaned_data['path'].strip(' /')
        paths = filter(lambda v: v!='', path.split('/'))
        for slug in paths:
            if slug.isdigit() or not COLUMN_PATH_RE.search(slug):
                raise forms.ValidationError(u"目录 '%s' 不符合规则" % slug)
        # 检查父路径是否存在
        if paths[:-1]:
            check = Column.objects.filter(path='/'.join(paths[:-1]))
            if self.instance.pk:
                check = check.exclude(pk=self.instance.pk)
            if not check.exists():
                raise forms.ValidationError(u"父栏目路径 '%s' 不存在" % '/'.join(paths[:-1]))
        return '/'.join(paths)


class ColumnEditForm(ColumnForm):
    class Meta:
        model = Column
        exclude = ('model',)


class ActionForm(forms.Form):
    model = forms.ChoiceField(choices=((i,i) for i in CONTENT_MODELS.keys()))
    action = forms.CharField()


class ActionBaseForm(forms.Form):
    def execute(self):
        pass


class DeleteAction(ActionBaseForm):
    pass

