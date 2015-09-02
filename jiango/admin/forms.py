# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from django import forms
from django.utils import timezone
from .models import User
from .auth import get_temp_salt, verify_temp_salt
from .config import AUTH_SLAT_TIMEOUT, LOGIN_FAIL_LOCK_TIMES, LOGIN_MAX_FAILS


class AuthenticationForm(forms.Form):
    username = forms.CharField(label=u'用户名')
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput)
    salt = forms.CharField(initial=get_temp_salt, widget=forms.HiddenInput)
    
    def clean(self):
        salt = self.cleaned_data.get('salt')
        salt_verify = verify_temp_salt(salt)
        
        # 强制更新 POST 来的 salt
        self.data = self.data.copy()
        self.data['salt'] = get_temp_salt()
        
        if salt_verify is None:
            raise forms.ValidationError(u'加密数据错误')
        if salt_verify is False:
            raise forms.ValidationError(u'登陆验证超时，请在 %d 秒内登陆' % AUTH_SLAT_TIMEOUT)
        
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            try:
                self.user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError(u'用户名不存在')
            
            # 密码错误次数检查
            if self.user.is_login_fail_lock:
                raise forms.ValidationError(u'密码错误超过 %d 次，账号被锁定 %d 秒' % (
                                        LOGIN_MAX_FAILS, self.user.login_fail_lock_remain))
            
            if password != hashlib.md5(salt + str(self.user.password_digest)).hexdigest():
                # 记录错误
                self.user.update_login_fails()
                raise forms.ValidationError(u'密码错误')
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user', None)
