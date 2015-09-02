# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .shortcuts import renderer
from .forms import AuthenticationForm
from .auth import LOGIN_NEXT_FIELD, set_login, set_login_cookie, set_logout, set_logout_cookie, get_admin_user
from .config import SECRET_KEY_DIGEST


render = renderer('admin/')


@render
def index(request, response):
    pass


@render(logout=True)
def login(request, response):
    secret_key = SECRET_KEY_DIGEST
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            next_url = request.REQUEST.get(LOGIN_NEXT_FIELD, reverse('admin:index'))
            resp = HttpResponseRedirect(next_url)
            set_login(user)
            set_login_cookie(resp, user)
            return resp
    else:
        form = AuthenticationForm()
    return locals()


# login=False 防止矬子已经退出后在刷新此页，然后跳转到登陆页面，登陆完了又回到退出页。永无止境啊！
@render(login=False)
def logout(request, response):
    if get_admin_user(request):
        set_logout(request.admin)
    set_logout_cookie(response)
