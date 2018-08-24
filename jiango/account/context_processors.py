# -*- coding: utf-8 -*-
from .services import get_request_login, get_request_user


class RequestLazy(object):
    def __init__(self, request):
        self.request = request


class RequestLoginLazy(RequestLazy):
    def __call__(self, *args, **kwargs):
        return get_request_login(self.request)


class RequestUserLazy(RequestLazy):
    def __call__(self, *args, **kwargs):
        return get_request_user(self.request)


def request_user(request):
    return {
        'LOGIN': RequestLoginLazy(request),
        'USER': RequestUserLazy(request),
    }
