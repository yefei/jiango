# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from .auth import get_request_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        user = get_request_user(request)
        if user:
            user.update_request_at()
