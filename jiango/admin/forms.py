# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from django import forms
from jiango.bootstrap.widgets import FilteredSelectMultiple
from .models import User, Group
from .auth import get_temp_salt, verify_temp_salt
from .config import AUTH_SLAT_TIMEOUT, LOGIN_MAX_FAILS, SECRET_KEY_DIGEST


def md5str(s):
    return hashlib.md5(s).hexdigest()


class AuthenticationForm(forms.Form):
    username = forms.CharField(label=u'用户名')
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput)
    salt = forms.CharField(initial=get_temp_salt, widget=forms.HiddenInput)

    def __init__(self, client_password_encrypt=True, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.user = None
        self.client_password_encrypt = client_password_encrypt

    def clean(self):
        salt = ''
        if self.client_password_encrypt:
            salt = self.cleaned_data.get('salt')
            salt_verify = verify_temp_salt(salt)

            # 强制更新 POST 来的 salt
            self.data = self.data.copy()
            self.data['salt'] = get_temp_salt()

            if salt_verify is None:
                raise forms.ValidationError(u'加密数据错误')
            if salt_verify is False:
                raise forms.ValidationError(u'登陆验证超时，请在 %d 秒内完成登陆' % AUTH_SLAT_TIMEOUT)
        
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

            if self.client_password_encrypt:
                password_correct = password == md5str(salt + str(self.user.password_digest))
            else:
                password_correct = md5str(md5str(password)+SECRET_KEY_DIGEST) == self.user.password_digest

            if password_correct is not True:
                # 记录错误
                self.user.update_login_fails()
                raise forms.ValidationError(u'密码错误')
            
            # 已登陆用户防挤
            if self.user.is_online:
                raise forms.ValidationError(u'当前用户已经在线，你无法登陆。如果是本人意外掉线请等待 %d 秒后登陆' % (
                                        self.user.online_remain))
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user', None)


class SetPasswordForm(forms.Form):
    current = forms.CharField(label=u'当前密码', widget=forms.PasswordInput,
                              help_text=u'你当前的登陆密码。注意：如果输入错误你将被强制退出')
    new = forms.CharField(label=u'新密码', widget=forms.PasswordInput)
    confirmation = forms.CharField(label=u'新密码确认', widget=forms.PasswordInput, help_text=u'重复上面输入的密码')
    salt = forms.CharField(initial=get_temp_salt, widget=forms.HiddenInput)
    
    def __init__(self, user, client_password_encrypt=True, *args, **kwargs):
        self.user = user
        self.current_password_error = False
        self.client_password_encrypt = client_password_encrypt
        super(SetPasswordForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        salt = ''
        if self.client_password_encrypt:
            salt = self.cleaned_data.get('salt')
            salt_verify = verify_temp_salt(salt)

            # 强制更新 POST 来的 salt
            self.data = self.data.copy()
            self.data['salt'] = get_temp_salt()

            if salt_verify is None:
                raise forms.ValidationError(u'加密数据错误')
            if salt_verify is False:
                raise forms.ValidationError(u'验证超时，请在 %d 秒内完成修改' % AUTH_SLAT_TIMEOUT)

        password = self.cleaned_data['current']

        if self.client_password_encrypt:
            password_correct = password == md5str(salt + str(self.user.password_digest))
        else:
            password_correct = md5str(md5str(password) + SECRET_KEY_DIGEST) == self.user.password_digest

        if password_correct is not True:
            self.current_password_error = True
            raise forms.ValidationError(u'当前密码错误')
        
        if self.cleaned_data['new'] != self.cleaned_data['confirmation']:
            raise forms.ValidationError(u'新密码与新密码确认不一致')
        
        return self.cleaned_data

    def get_new_password(self):
        if self.client_password_encrypt:
            return self.cleaned_data.get('new')
        return md5str(md5str(self.cleaned_data.get('new')) + SECRET_KEY_DIGEST)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {'groups': FilteredSelectMultiple(u'用户组'),
                   'permissions': FilteredSelectMultiple(u'权限')}


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        widgets = {'permissions': FilteredSelectMultiple(u'权限')}
