# -*- coding: utf-8 -*-
# Created on 2012-9-26
# @author: Yefei


class APIError(Exception):
    status_code = 200


class ParamError(APIError):
    pass


class LoginRequired(APIError):
    pass


class Forbidden(APIError):
    status_code = 403


class Deny(APIError):
    pass
