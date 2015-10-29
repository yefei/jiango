# -*- coding: utf-8 -*-
# Created on 2015-8-31
# @author: Yefei
import re


MOBILE_MATCH = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I | re.M)

MOBILE_METAS = (
    'HTTP_PROFILE',
    'HTTP_X_WAP_PROFILE',
    'HTTP_X_OPERAMINI_FEATURES',
)


class MobileDetectMiddleware(object):
    def process_request(self, request):
        for x in MOBILE_METAS:
            if x in request.META:
                request.is_mobile = True
                return
        
        http_accept = request.META.get('HTTP_ACCEPT')
        if http_accept and 'application/vnd.wap.xhtml+xml' in http_accept.lower():
            request.is_mobile = True
            return
        
        request.is_mobile = MOBILE_MATCH.search(request.META.get('HTTP_USER_AGENT', ''))
