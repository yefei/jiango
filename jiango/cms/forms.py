# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
from django import forms
from jiango.importlib import import_object
from jiango.admin.models import LogTypes
from .utils import get_model_object, get_model_actions
from .models import Column
from .config import COLUMN_PATH_RE, CONTENT_ACTIONS, CONTENT_MODELS


class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
    
    def clean_path(self):
        path = self.cleaned_data['path'].strip(' /')
        paths = filter(lambda v: v != '', path.split('/'))
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


class ColumnDeleteForm(forms.Form):
    confirm = forms.BooleanField(label=u'我确定要删除以上数据')


class ActionForm(forms.Form):
    model = forms.ChoiceField(choices=((i, i) for i in CONTENT_MODELS.keys()))
    action = forms.CharField()
    back = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self._model_object = None
        self._form_object = None

    def clean_model(self):
        model = self.cleaned_data['model']
        self._model_object = get_model_object(model, 'model')
        return model
    
    def get_model_object(self):
        return self._model_object
    
    def clean_action(self):
        action = self.cleaned_data['action']
        actions = get_model_actions(self.cleaned_data['model'])
        if action not in actions:
            raise forms.ValidationError(u'无效的操作项')
        self._form_object = import_object(CONTENT_ACTIONS[action]['form'])
        return action
    
    def get_form_object(self):
        return self._form_object
    
    def get_action_name(self):
        action = self.cleaned_data.get('action')
        if action:
            return CONTENT_ACTIONS[action].get('name')


class RecycleClearForm(forms.Form):
    count = forms.IntegerField(label=u'请输入页面上显示的数量')
    
    def __init__(self, content_count, *args, **kwargs):
        super(RecycleClearForm, self).__init__(*args, **kwargs)
        self.content_count = content_count
    
    def clean_count(self):
        count = self.cleaned_data['count']
        if count != self.content_count:
            raise forms.ValidationError(u'需要被清空数量不正确，建议检查回收站中是否有新增内容')
        return count


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
