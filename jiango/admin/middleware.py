# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from .auth import get_request_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        get_request_user(request)
