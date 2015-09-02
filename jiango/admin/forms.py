# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from django import forms
from .models import User


class AuthenticationForm(forms.Form):
    username = forms.CharField(label=u'用户名')
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            try:
                self.user_cache = User.objects.get(username=username)
            except User.DoesNotExist:
                self.user_cache = None
            if self.user_cache is None:
                raise forms.ValidationError(u'用户名不存在')
            if not self.user_cache.check_password(password):
                raise forms.ValidationError(u'密码错误')
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache
