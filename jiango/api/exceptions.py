# -*- coding: utf-8 -*-
# Created on 2012-9-26
# @author: Yefei
from django.forms.forms import NON_FIELD_ERRORS


class APIError(Exception):
    status_code = 422


class ParamError(APIError):
    pass


class LoginRequired(APIError):
    pass


class Forbidden(APIError):
    status_code = 403


class Deny(APIError):
    pass


class FormError(APIError):
    def __init__(self, form):
        errors = []
        if not form.is_valid():
            for f, e in form.errors.items():
                label = None
                if f != NON_FIELD_ERRORS:
                    label = form[f].label
                errors.append({'field': f, 'message': e, 'label': label})
        super(FormError, self).__init__(errors)
