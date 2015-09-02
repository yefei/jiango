# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .shortcuts import renderer
from .forms import AuthenticationForm
from .auth import AUTHENTICATE_NEXT_FIELD, set_login, set_login_cookie, set_logout, set_logout_cookie


render = renderer('admin/')


@render
def index(request, response):
    pass


@render(logout=True)
def login(request, response):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            next_url = request.REQUEST.get(AUTHENTICATE_NEXT_FIELD, reverse('admin:index'))
            resp = HttpResponseRedirect(next_url)
            set_login(user)
            set_login_cookie(resp, user)
            return resp
    else:
        form = AuthenticationForm()
    return locals()


@render
def logout(request, response):
    set_logout(request.admin)
    set_logout_cookie(response)
