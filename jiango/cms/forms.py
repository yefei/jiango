# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
from django import forms
from jiango.importlib import import_object
from jiango.admin.models import LogTypes
from .models import Path
from .config import PATH_RE, CONTENT_ACTIONS, CONTENT_MODELS


class PathForm(forms.ModelForm):
    class Meta:
        model = Path
    
    def clean_path(self):
        path = self.cleaned_data['path'].strip(' /')
        paths = filter(lambda v: v != '', path.split('/'))
        for slug in paths:
            if slug.isdigit() or not PATH_RE.search(slug):
                raise forms.ValidationError(u"目录 '%s' 不符合规则" % slug)
        # 检查父路径是否存在
        if paths[:-1]:
            check = Path.objects.filter(path='/'.join(paths[:-1]))
            if self.instance.pk:
                check = check.exclude(pk=self.instance.pk)
            if not check.exists():
                raise forms.ValidationError(u"父栏目路径 '%s' 不存在" % '/'.join(paths[:-1]))
        return '/'.join(paths)


class PathEditForm(PathForm):
    class Meta:
        model = Path


class PathDeleteForm(forms.Form):
    confirm = forms.BooleanField(label=u'我确定要删除以上数据')


class ActionForm(forms.Form):
    action = forms.CharField()
    back = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self._form_object = None

    def clean_action(self):
        action = self.cleaned_data['action']
        if action not in CONTENT_ACTIONS:
            raise forms.ValidationError(u'无效的操作项')
        self._form_object = import_object(CONTENT_ACTIONS[action]['form'])
        return action
    
    def get_form_object(self):
        return self._form_object
    
    def get_action_name(self):
        action = self.cleaned_data.get('action')
        if action:
            return CONTENT_ACTIONS[action].get('name')


class ActionBaseForm(forms.Form):
    log_action = LogTypes.NONE
    
    def __init__(self, content_set, *args, **kwargs):
        super(ActionBaseForm, self).__init__(*args, **kwargs)
        self.content_set = content_set
    
    def execute(self):
        pass


class HideAction(ActionBaseForm):
    log_action = LogTypes.UPDATE
    is_hidden = forms.BooleanField(required=False, label='隐藏 (在前台不显示)', initial=True)
    
    def execute(self):
        self.content_set.update(is_hidden=self.cleaned_data['is_hidden'])


class DeleteAction(ActionBaseForm):
    log_action = LogTypes.DELETE
    
    def execute(self):
        self.content_set.update(is_deleted=True)
