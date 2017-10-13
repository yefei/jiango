# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
import re
import datetime
from django.utils.timezone import is_aware, utc
from django.utils.translation import ungettext, ugettext
from django.utils.encoding import force_unicode
from django.utils import dateformat


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
    u = None
    for u in units:
        if abs(size) < step:
            break
        size /= float(step)
    return size, u


def intcomma4(value):
    return re.sub(r"(\d)(?=(\d{4})+(?!\d))", r"\1,", force_unicode(value))


def timesince_single(d, now=None, reversed=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.
    """
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n))
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)

    delta = (d - now) if reversed else (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'0 ' + ugettext('minutes')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    return ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}


def time_humanize(d):
    u"""
    人性化时间显示
    :param d: 时间
    :return: 字符串
    """
    now = datetime.datetime.now()
    delta = now - d
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        return u'刚刚'
    if since < 60:
        return u'%d秒前' % since
    if since < 60 * 60:
        return u'%d分钟前' % (since / 60)

    # 6-12上午，12-18下午，18-24晚上，0-6凌晨
    if d.hour >= 18:
        a = u'晚上'
    elif d.hour >= 12:
        a = u'下午'
    elif d.hour >= 6:
        a = u'上午'
    else:
        a = u'凌晨'
    # 子时（23-1点）：半夜
    # 丑时（1-3点）：凌晨
    # 寅时（3-5点）：黎明
    # 卯时（5-7点）：清晨
    # 辰时（7-9点）：早上
    # 巳时（9-11点）：上午
    # 午时（11-13点）：中午
    # 未时（13-15点）：午后
    # 申时（15-17点）：下午
    # 酉时（17-19点）：傍晚
    # 戌时（19-21点）：晚上
    # 亥时（21-23点）：深夜
    # if d.hour in (23, 0, 1): a = u'半夜'
    # elif d.hour >= 21: a = u'深夜'
    # elif d.hour >= 19: a = u'晚上'
    # elif d.hour >= 17: a = u'傍晚'
    # elif d.hour >= 15: a = u'下午'
    # elif d.hour >= 13: a = u'午后'
    # elif d.hour >= 11: a = u'中午'
    # elif d.hour >= 9: a = u'上午'
    # elif d.hour >= 7: a = u'早上'
    # elif d.hour >= 5: a = u'清晨'
    # elif d.hour >= 3: a = u'黎明'
    # else: a = u'凌晨'

    # 时间显示 1点 or 1:23
    g = d.hour
    if d.hour == 0:
        g = 12
    if d.hour > 12:
        g = d.hour - 12
    time = u'%d点' % g if d.minute == 0 else u'%d:%02d' % (g, d.minute)

    # 今天、昨天、前天
    days = (now.date() - d.date()).days
    if days == 0:
        return a + time
    if days == 1:
        return u'昨天' + a + time
    if days == 2:
        return u'前天' + a + time
    # if days == 3:
    #     return u'大前天' + a + time

    if d.year == now.year:
        week = {0: u'一', 1: u'二', 2: u'三', 3: u'四', 4: u'五', 5: u'六', 6: u'日'}[d.weekday()]
        # 本周、上周
        weeks = now.isocalendar()[1] - d.isocalendar()[1]
        if weeks == 0:
            return u'本周' + week + a + time
        if weeks == 1:
            return u'上周' + week + a + time

        return dateformat.format(d, u'n月j日') + a + time

    return dateformat.format(d, u'Y年n月j日')
