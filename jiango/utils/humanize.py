# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei

# 1d=1天,1h=1小时,1m=1分钟,1s=1秒s可以不加。例如10天20小时15分3秒: 10d20h15m3
def parse_humanize_second(value):
    if isinstance(value, basestring):
        if value.isdigit():
            return int(value)
        tmp = ''
        sec = 0
        for c in str(value).lower():
            if c.isdigit():
                tmp += c
            elif c == 'd':
                sec += int(tmp) * 86400
                tmp = ''
            elif c == 'h':
                sec += int(tmp) * 3600
                tmp = ''
            elif c == 'm':
                sec += int(tmp) * 60
                tmp = ''
            elif c == 's':
                sec += int(tmp)
                tmp = ''
        # 结尾不加 s 的秒数
        if tmp:
            sec += int(tmp)
        return sec
    return value


def humanize_second(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return ''.join((('%dd' % days if days else ''),
                    ('%dh' % hours if hours else ''),
                    ('%dm' % minutes if minutes else ''),
                    (str(seconds) if seconds else ''),
                    ))


SIZE_UNITS = [None,'K','M','G','T','P','E','Z','Y']

def humanize_size(size, step=1024, units=SIZE_UNITS):
    if size < step:
        return size, None
    for u in units:
        if abs(size) < step:
            break
        size /= float(step)
    return size, u
