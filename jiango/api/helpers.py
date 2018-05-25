# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/3/22
Version: $Id: helpers.py 480 2017-08-03 01:09:14Z feiye $
"""
from jiango.api import FormError
from jiango.captcha.helpers import check_captcha
from .exceptions import APIError
from .errorcodes import *


class APIErrorResult(APIError):
    def __init__(self, error_code=SUCCESS, error_message=None, **params):
        self.error_code = error_code
        self.error_message = error_message
        self.params = params


def api_result(error_code=SUCCESS, error_message=None, **params):
    result = {'errorCode': error_code}
    if error_message:
        result['errorMessage'] = error_message
    result.update(params)
    return result


def query_set_page_result(request, qs, out_func=None, filter_ops='pk__lt', order_by='-pk', page_count=100):
    page_id = request.param.int('pageId', 0)
    if page_id > 0:
        qs = qs.filter(**{filter_ops: page_id})
    qs = qs.order_by(order_by)
    qs_list = list(qs[:page_count])
    qs_data = [out_func(i, request) for i in qs_list] if out_func else qs_list
    return dict(list=qs_data, total=qs.count(), count=len(qs_list), pageId=qs_list[-1].pk if qs_list else 1)


def assert_form_errors(form, error_codes=None):
    if form.is_valid():
        return
    if error_codes:
        for field, error in form.errors.items():
            e = error_codes.get(field)
            if e:
                raise APIErrorResult(*e, **{field: error})
    raise APIErrorResult(FROM_ERROR, FormError(form).message)


def assert_captcha_check(encrypt_data, value):
    if encrypt_data and value and check_captcha(encrypt_data, value):
        return
    raise APIErrorResult(*CAPTCHA_ERROR)
