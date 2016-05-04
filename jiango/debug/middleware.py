# -*- coding: utf-8 -*-
# Created on 2012-9-26
# @author: Yefei
import sys
from django.db import connection


class SQLDebugMiddleware(object):
    def process_response(self, request, response):
        if connection.queries:
            sys.stdout.write("SQL %s\n" % ('=' * 26))
            for query in connection.queries:
                sys.stdout.write("[%s] %s\n" % (query['time'], query['sql']))
            sys.stdout.write("%s\n" % ('=' * 30))
        return response
